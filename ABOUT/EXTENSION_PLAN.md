# Extension plan — B: Harden against failure

The shape, scope and size check are in the README under **The Shape**. This file is the build plan: what to implement, in what order, and how to prove it works. What was actually built, and the concepts behind it, are in `HOW_IT_WORKS.md` (same folder).

**This milestone:** build one hardening layer (steps 0–4), confirm the original system still works, and commit as I go (at least three commits).
**Later milestone:** health check and deployment (step 5).

---

## Step 0 — A switch that causes failures on purpose

**The idea (fault injection):** real failures are rare and random, so I can't wait for GPT-2 to crash to test my handling. A setting makes the failure happen on demand.

**What to build:** one setting `FAULT` in `config.py`, read from an environment variable, so it can be switched without editing code.

| `FAULT` value | What it simulates |
|---|---|
| `none` (default) | normal operation |
| `model_error` | GPT-2 throws an error |
| `model_slow` | GPT-2 takes 30 seconds to answer |
| `log_error` | the audit log can't be written |

## Step 1 — Never an HTML crash page; fix `/appeal`

**The idea (unhandled exceptions):** when Python hits an error nobody planned for, Flask shows an HTML debug page. That breaks anything expecting JSON and can reveal code. A catch-all error handler is the last safety net.

**What to build:**
- A catch-all error handler in `app.py`: any unexpected error returns 500 with `{"error": "internal_error", "message": "..."}` and writes a log entry.
- `/appeal` still crashes on a JSON array body (the same bug as RQ07). Give it the same check `/submit` has.

## Step 2 — Degraded mode when GPT-2 fails

**The idea (graceful degradation):** when one part breaks, the service keeps answering, honestly and in a reduced way, instead of crashing.

**What to build:** `/submit` catches any detector error (except "too short", which stays a 400) and switches to degraded mode:
- `guess: "unsure"`, with a label saying the text couldn't be fully checked right now
- `"degraded": true` in the response
- `model_score: null` (it never ran); the style score is still recorded, for information only
- a log entry with `degraded: true` and the reason (`model_error`)

Why always "unsure" and not the style signal alone: my tests showed the style signal is the weaker one and easy to fool, so on its own it could clear AI text as human.

## Step 3 — A time limit on GPT-2

**The idea (timeouts):** without a time limit, a slow part makes everything wait. A timeout says "if this isn't done in N seconds, give up and do something else."

**What to build:**
- Run the detector with a time limit, `DETECTOR_TIMEOUT_SECONDS` in `config.py` (about 10 seconds). Over the limit: degraded mode from step 2, reason `timeout`.
- Load GPT-2 when the server starts, otherwise the first request (which loads the model) would always hit the timeout.

**Limitation to note in the README:** Python can't really stop the slow work. It keeps running in the background; the service just stops waiting for it.

## Step 4 — When the audit log can't be written

**The idea (failing safely):** sometimes the right answer is to refuse. A decision that isn't recorded can't be appealed (`/appeal` would say "not found") or checked later.

**What to build:** if writing the decision fails, `/submit` returns **503** ("We couldn't save this result, please try again") and gives no content ID. Since the log itself failed, the failure is reported to the server console instead.

## Step 5 — Instrument and deploy (later milestone)

- `GET /health`: is GPT-2 loaded, and how many recent decisions were degraded.
- Deploy to Hugging Face Spaces (GPT-2 needs about 1 GB of memory).

---

## Criteria

To be added to `criteria.md` as 6–10 under an "Extension" heading, so the original five stay unchanged.

6. **Model failure:** with `FAULT=model_error`, 10 of 10 submissions return 200 with `guess: "unsure"` and `degraded: true`. None return a 500, and each is logged as degraded.
7. **Slow model:** with `FAULT=model_slow`, 10 of 10 submissions answer within 12 seconds (a 10-second limit plus margin), as degraded "unsure".
8. **Log failure:** with `FAULT=log_error`, 10 of 10 submissions return a JSON 503, never a 500, and none returns a content ID.
9. **No HTML errors:** every bad request to either endpoint, including a JSON array sent to `/appeal`, returns JSON. 0 HTML pages across the whole attack set.
10. **Nothing else changes:** with `FAULT=none`, my 10 own texts get the same scores and labels as in unit 8.

## Confirming the original system still works

After building, with `FAULT=none`:
- rerun `python run_eval.py --label extension` and compare with `results/run_2026-11-15_1427_after.md`: same verdicts for criteria 1–5
- rerun the attack set and compare with `results/attack_run_2026-11-15_1427_after.md`: still 49 HELD and 7 BROKE
- rerun the appeal test for criterion 4

## Commits

| Commit | Contains |
|---|---|
| 1 | Step 0 (fault switch) + step 1 (JSON error handler, `/appeal` fix) |
| 2 | Step 2 (degraded mode) |
| 3 | Step 3 (timeout, load GPT-2 at startup) |
| 4 | Step 4 (log failure → 503) |
| 5 | Regression check results + README and criteria updates |

## Open decisions

1. **Log failure:** refuse with a 503 (recommended), or return the result marked "not saved" (but then the writer can't appeal it)?
2. **New criteria:** add them to `criteria.md` as 6–10 under an "Extension" heading?
