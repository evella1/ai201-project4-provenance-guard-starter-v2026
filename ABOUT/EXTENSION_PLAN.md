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
- Path: **local, with logs** (decided). The project doesn't fit a free host: torch + GPT-2 need more than a free tier's 512 MB, and the model would re-download after every spin-down. Run path, environment and logs are written up in `RUNNING.md`.

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

## Decisions

1. **Log failure:** refuse with a 503. ✅ Decided and built in step 4 (also for `/appeal`).
2. **Degraded mode:** always "unsure", never style-only scoring. ✅ Decided and built in step 2.
3. **Run path:** local, with logs (the project doesn't fit a free host). ✅ Decided, written up in `RUNNING.md`.
4. **New criteria:** add them to `criteria.md` as 6–10 under an "Extension" heading. ⏳ Planned, not done yet.

---

## Status and next steps

### Done

- [x] Shape, out of scope, size check and build step headers in README "The Shape"
- [x] Step 0: fault switch (`AI201_FAULT`)
- [x] Step 1: JSON error handler for any crash, `/appeal` fix
- [x] Step 2: degraded mode when GPT-2 fails
- [x] Step 3: 10-second time limit on GPT-2, model loaded at startup
- [x] Step 4: 503 when the audit log can't be written
- [x] `RUNNING.md`: run path (local, with logs), environment, start commands, settings, logs
- [x] Notes for each step in `HOW_IT_WORKS.md`

### Next, in order

1. **Commit what's not committed yet:** step 4 (`app.py`), the `ABOUT/` folder (it was never added to git), `RUNNING.md`, and the moved `EXTENSION_PLAN.md`.
   ```powershell
   git add ABOUT EXTENSION_PLAN.md app.py RUNNING.md logs/audit.jsonl
   git commit -m "Add step 4 and run instructions"
   git push
   ```
2. **Regression check** (server running with `AI201_FAULT` = `none`): confirm the original system still works.
   - `python run_eval.py --label extension` → same verdicts as `results/run_2026-11-15_1427_after.md` (criteria 1, 3, 5 MET; 2 MISSED)
   - `python run_attacks.py --set attack_set --label extension` → still 49 HELD and 7 BROKE (compare with `results/attack_run_2026-11-15_1427_after.md`), and every answer JSON
   - rerun the appeal test for criterion 4 → 10 of 10, bad 3 of 3
3. **Criteria 6–10 runs, three trials each,** saved in `results/` as evidence. Each fault needs the server restarted with that fault switched on:
   - 6: `AI201_FAULT=model_error` → 10 of 10 return 200, unsure, `degraded: true`, logged as degraded
   - 7: `AI201_FAULT=model_slow` → 10 of 10 answer within 12 seconds, degraded unsure
   - 8: `AI201_FAULT=log_error` → 10 of 10 return JSON 503, no content_id
   - 9: `AI201_FAULT=none` → every bad request to either endpoint is JSON, 0 HTML pages across the attack set
   - 10: `AI201_FAULT=none` → my 10 texts get the same scores and labels as in unit 8
4. **`criteria.md`:** add criteria 6–10 under an "Extension" heading (the original five stay unchanged).
5. **README:**
   - endpoint description: `confidence` can be `null` in degraded mode; new fields `degraded` and `degraded_reason`; `/submit` can return 503 (log can't be written); every error, including 404/405/500, is JSON
   - the extension's results: the criteria 6–10 table (three trials) and real pasted output, like unit 8
   - "What's Still Broken": add short texts getting the AI label (the style signal returns 0.5, so the model score decides alone)
6. **Commit** the results, criteria and README updates (commit 5 in the table above).
