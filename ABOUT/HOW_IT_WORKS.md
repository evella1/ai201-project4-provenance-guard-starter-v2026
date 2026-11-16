# How it works — my notes on the failure handling

Personal notes, to help me understand what was built and why. The build plan is in `EXTENSION_PLAN.md` (same folder). This file is updated after each step.

---

## Words to know

| Word | What it means |
|---|---|
| **Exception** | Python's way of saying "something went wrong". It stops the code at that point. If nobody catches it, the program (or the request) crashes. |
| **Catching an exception** | `try: ... except SomeError: ...` — "try this; if this error happens, do that instead of crashing". |
| **Raising an exception** | `raise SomeError("message")` — causing the error on purpose. Fault injection does this. |
| **Unhandled exception** | An error no code planned for. In Flask it used to become an HTML debug page. |
| **Error handler** | A function Flask calls when an error happens, so I decide what the caller sees. `@app.errorhandler(Exception)` catches every kind. |
| **Status code** | The number at the start of every web answer that says how it went (see the table below). |
| **Environment variable** | A setting given to a program from outside, without editing code. In PowerShell: `$env:NAME = "value"`. It only lasts for that terminal window. |
| **Fault injection** | Making a part fail on purpose, to test that the failure is handled. |
| **Degraded mode** | The service keeps answering, honestly and in a reduced way, when one part is broken. (Step 2.) |
| **Timeout** | A time limit: "if this isn't done in N seconds, give up and do something else". (Step 3.) |
| **Failing safely** | Sometimes the right answer to a failure is to refuse, so nothing wrong or untraceable happens. (Step 4.) |
| **Audit log** | `logs/audit.jsonl` — one line of JSON per event: decisions, appeals, rejections, and now errors. |

### Status codes my service uses

| Code | Meaning | When my service sends it |
|---|---|---|
| 200 | OK | a normal answer |
| 400 | Bad request — the caller sent something wrong | empty text, too long, not JSON, etc. |
| 404 | Not found | unknown URL, or an appeal for a content_id that doesn't exist |
| 405 | Method not allowed | e.g. `GET /submit` (it only accepts POST) |
| 429 | Too many requests | rate limit hit |
| 500 | Internal server error — *my* side broke | an unexpected crash |
| 503 | Service unavailable — try again later | planned for step 4 (log can't be written) |

**Rule of thumb:** 4xx = the caller's fault, 5xx = my service's fault.

---

## Step 0 — The fault switch

**Purpose:** real failures are rare and random. I can't wait for GPT-2 to crash to see if my handling works, so I added a switch that makes things fail on demand.

**What was built:**
- `config.py`: a setting `FAULT`, read from the environment variable `AI201_FAULT`. Values:
  - `none` — normal (default)
  - `model_error` — GPT-2 throws an error
  - `model_slow` — GPT-2 waits 30 seconds (`FAULT_SLOW_SECONDS`) before answering
  - `log_error` — writing to the audit log fails
- A typo (e.g. `AI201_FAULT=typo`) stops the server from starting, with a clear message. Otherwise a typo would silently test nothing.
- The faults are placed **inside the parts that fail**: `detector.py` (`model_signal`) and `audit.py` (`_append`). `app.py` doesn't know about the switch, so it has to handle the errors like real ones. That keeps the test honest.
- The server's startup message shows `fault injection: ...`, with a warning when a fault is on.

**How to use it (PowerShell, in the terminal where I start the server):**

```powershell
$env:AI201_FAULT = "model_error"; python app.py   # break the model
$env:AI201_FAULT = "none"; python app.py          # back to normal
```

**What the tests showed before any handling (my "before" picture):**

| `FAULT` | Result |
|---|---|
| `none` | 200 JSON — normal |
| `model_error` | 500 HTML page — crash |
| `model_slow` | 200, but the writer waits the whole time |
| `log_error` | 500 HTML page, after all the scoring work was done |
| `typo` | server refuses to start |

---

## Step 1 — Never an HTML crash page; fix `/appeal`

**Purpose:** an unexpected error used to give an HTML debug page. Programs expecting JSON can't read it, it shows my code, and the crash left no trace in the log.

**What was built:**
- `app.py`: a catch-all error handler, `handle_any_error`, Flask's last safety net. Two kinds of errors reach it:
  - **HTTP errors Flask raises itself** (404, 405): expected, so they keep their code, just as JSON.
  - **Real crashes:** the caller gets a 500 with a short, safe message ("Something went wrong on our side..."). The details go to the audit log.
  - If the log itself is broken, it reports the problem on the server console instead of crashing a second time.
- `audit.py`: a new function `log_error`, which writes an `"event": "error"` entry (route, error type, short description).
- `app.py` `/appeal`: now checks the body is a JSON object, like `/submit`. A JSON array gets a 400 instead of crashing. Bad appeals are still not logged (criterion 4).

**What the tests showed (debug mode on, like the real server):**

| Test | Before | After |
|---|---|---|
| Normal submit | 200 JSON | 200 JSON (unchanged) |
| `/appeal` with a JSON array | crash, HTML | 400 JSON |
| Unknown URL `/nope` | 404 HTML | 404 JSON |
| `GET /submit` | 405 HTML | 405 JSON |
| `FAULT=model_error` | 500 HTML | 500 JSON + `error` entry in the log |
| `FAULT=log_error` | 500 HTML | 500 JSON + message on the console |

**Still to fix:** these are clean failures, not handled ones. Step 2 turns `model_error` into a real "unsure" answer (degraded mode); step 4 turns `log_error` into a clear 503.

---

## Step 2 — Degraded mode when GPT-2 fails

**Purpose:** with one signal broken, the service should still answer, honestly, instead of crashing. This is called *graceful degradation*. I decided the answer is always "unsure": the style signal alone is the weaker one and easy to fool, so it could clear AI text as human.

**What was built:**
- `app.py` `/submit`: the detector call now catches two kinds of errors separately:
  - `ValueError` = text too short → 400, as before.
  - **any other error** = the model failed → degraded mode. The error is written to the server console, and the service carries on without the model score.
- In degraded mode the answer is:
  - `guess: "unsure"`, `confidence: null`, `model_score: null` (the model never ran)
  - `style_score` is still calculated and recorded, for information only. It doesn't decide anything.
  - `label`: a new text, `DEGRADED_LABEL` in `scoring.py`: "We couldn't fully check this text right now, so we can't say whether it was written by a person or with AI help. This is not an accusation. Please submit it again later for a full check."
  - `"degraded": true` and `"degraded_reason": "model_error"`
- The decision is still logged with a content_id (so it can be appealed), plus `degraded: true`, `degraded_reason` and `error_type`.
- Normal answers now also include `"degraded": false`, so every response has the same shape.

**Why `except Exception` and not just one error type:** I can't know every way GPT-2 might break (out of memory, missing files, a bug). Catching every kind here is deliberate: whatever breaks inside the model, the writer still gets an honest answer. The order matters: Python checks `except ValueError` first, so "too short" still gets its 400.

**What the tests showed (my 10 own texts):**

| `FAULT` | Status | Guess | Degraded | Logged |
|---|---|---|---|---|
| `model_error` | 10 × 200 (no 500s) | 10 × unsure | all true | 10 entries, all marked degraded |
| `none` | 10 × 200 | 9 unsure, 1 human — same as unit 8 | all false | 10 entries, none degraded |

So with the model broken, criterion 6 ("10 of 10 return 200 with unsure and degraded: true, each logged as degraded") passes in this check, and normal behavior didn't change.

**To update later:** my README's endpoint description says `confidence` is always a number from 0 to 1. In degraded mode it is now `null`, and there are new fields (`degraded`, `degraded_reason`). The endpoint description needs a line about this.

---

## Step 3 — A time limit on GPT-2

**Purpose:** without a time limit, a slow model makes the writer wait as long as it takes, maybe forever. A *timeout* says: "if this isn't done in N seconds, stop waiting and do something else". The "something else" is the degraded mode from step 2.

**What was built:**
- `config.py`: `DETECTOR_TIMEOUT_SECONDS = 10`. A normal check takes about 0.1–0.4 seconds once the model is loaded (even the longest allowed text), so 10 seconds is a lot of room.
- `app.py`: a small **worker pool** (`_detector_pool`, 4 workers). Instead of calling GPT-2 directly, `/submit` hands the job to a worker and waits for the result with a time limit:
  ```python
  future = _detector_pool.submit(detector.model_signal, text)
  model_score = future.result(timeout=config.DETECTOR_TIMEOUT_SECONDS)
  ```
  - A **future** is a "ticket" for a job that's running somewhere else. `future.result(timeout=10)` means "give me the answer, but I'll only wait 10 seconds".
  - If the 10 seconds pass → `TimeoutError` → degraded mode with `degraded_reason: "timeout"`.
  - If the job itself fails (e.g. `model_error`), the error comes back through the future, so step 2 still works.
- `app.py` `main()`: **GPT-2 is now loaded when the server starts**, not on the first request. Loading takes several seconds, so otherwise the first submission after every start would hit the time limit. If loading fails, the server still starts and prints a warning; submissions then answer in degraded mode.
  - In debug mode Flask starts the app twice (a watcher that restarts the server when code changes, and the real server). Only the real one loads the model (`WERKZEUG_RUN_MAIN`), so the model isn't loaded twice.

**Why a separate thread is needed:** Python runs code line by line. If `/submit` called GPT-2 directly, it would be stuck on that line until GPT-2 finished. Running GPT-2 on another thread lets `/submit` keep control of the clock.

**The limitation (honest note):** Python can't force-stop the slow job. After the timeout, the job keeps running in the background until it ends; the route just stops waiting for it. With only 4 workers, many stuck jobs at once could fill the pool. New jobs would then wait in line and also time out (still a degraded answer, never a hang).

**What the tests showed (model loaded first, like the real server):**

| `FAULT` | Result | Time |
|---|---|---|
| `model_slow` (GPT-2 takes 30 s) | 3 × 200, unsure, degraded, reason `timeout`, logged with `error_type: TimeoutError` | 10.0 s each (not 30) |
| `model_error` | 2 × 200, unsure, degraded, reason `model_error` (step 2 still works) | 0.0 s |
| `none` | 3 × 200, normal answers, not degraded | 0.1–0.2 s |

So criterion 7 ("10 of 10 answer within 12 seconds as degraded unsure") is on track: the answer comes at 10 seconds, within the 12-second target.

---

## Step 4 — When the audit log can't be written

**Purpose:** the audit log is what makes appeals and audits possible. A decision that isn't recorded can't be appealed (`/appeal` would say "not found") or checked later. So when the log can't be written, the safest answer is to *refuse* — this is called *failing safely* (or "failing closed").

**What was built (`app.py`):**
- `_log_unavailable(...)`: the answer when the log fails — **503** ("service unavailable, try again later"): "We couldn't save this result, so we can't give you one right now. Please try again in a few minutes." The problem is written to the server console, because the log itself is what's broken.
- `/submit`: if saving the decision fails → 503, and **no content_id** (an ID for a decision that was never saved would lead nowhere).
- `/appeal`: if saving the appeal fails → 503 too. This wasn't in the original plan, but it follows the same rule: confirming an appeal that was never saved would tell the writer "a person will review it" when nobody will.
- `_try_log_rejection(...)`: rejections (400 bad input, 429 rate limit) are still logged when possible, but a broken log **doesn't change the answer**: a bad request is still a 400, a flood is still a 429. Only the missing trace goes to the console.

**Why `except OSError` (and not every error):** a log that can't be written raises an `OSError` (full disk, file locked, no permission). Other errors, like a bug in my own code, are not "the log is down" — they still go to the catch-all handler from step 1 as a 500. Catching only the error I expect keeps real bugs visible.

**Why 503 and not 500:** 500 means "my service broke". 503 means "temporarily unavailable, try again later" — it tells the caller the problem is expected to pass and retrying makes sense.

**What the tests showed:**

| `FAULT` | 10 × `/submit` | Empty text | `/appeal` (real content_id) | New log lines |
|---|---|---|---|---|
| `log_error` | 10 × **503**, 0 content_ids | **400** (still refused) | **503** | 0 |
| `none` | 10 × 200, 10 content_ids | 400 | 200 under_review | 12 (10 decisions, 1 rejection, 1 appeal) |

With the log broken, the console shows a report for every failed write (that's the "report it somewhere" part).

So criterion 8 ("10 of 10 return a JSON 503, never a 500, and none returns a content ID") passes in this check.

---

## Things I noticed along the way

- **Short texts can get the AI label.** A 3-sentence, ~20-word test text got AI (0.65): it's too short for the style signal (which returns 0.5), so the model score decides alone. Same mechanism as the Arabic text (diagnosis 2). Belongs in "What's Still Broken".
- **Git line-ending warnings** ("LF will be replaced by CRLF") are normal on Windows and harmless.
- **VS Code tabs can be out of date** when files change on disk. Use Ctrl+Shift+P → `File: Revert File` before editing.
