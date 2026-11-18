# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1.

<!-- Your criterion. It must name a number. -->

At most 1/10 written by me (Ewelina) text is labeled high confidence AI.


**Why this target:**
Accusing an honest writer of using AI when they didn't can get them in real trouble, so the detector should rarely make that mistake. Keeping it to 1 in 10 also means a “high confidence” label can actually be trusted.


---

## 2.

<!-- Your criterion. -->
Using 5 AI-generated texts and 5 texts written by people without AI help, the average AI score is at least 0.3 higher than the average human score.


**Why this target:**
If AI and human texts score close together, no cutoff can tell them apart and the labels are just guesses. My unsure band is 0.3 wide (0.35 to 0.65), so a gap smaller than that means the two groups can't land on opposite sides of it. 


---

## 3.

<!-- Your criterion. -->
Each of the three labels (human, unsure, ai) is produced by at least one input in every trial.


**Why this target:**
If one of the labels never shows up, it isn't doing anything, and that probably means something is off with my score ranges. This could really happen: a weighted average pulls scores toward the middle, so the human label may be hard to reach if the style signal doesn't change much.

---

## 4.

<!-- Your criterion. -->

10 out of 10 appeals with real content_ids return status under_review and show up in the log. Appeals with a made-up, empty, or missing content_id return a 404 or 400 and are not logged.


**Why this target:**
The appeal is a wrongly accused writer's only way to push back, so it has to work every time, not just most of the time. A writer who types the wrong ID should be told, not shown a confirmation for an appeal that was never saved.

---

## 5.

<!-- Your criterion. -->

Empty text, missing text, text set to null, and text over 20,000 characters each return a 400 with an error message. None return a 500 or crash the service.


**Why this target:**
Crashing on bad input is one of the most common failures, and people send text that's empty, missing, or way too long all the time, sometimes by accident and sometimes on purpose. My endpoint promises a clear 400 error for bad input like this, so every case should get one, with no exceptions.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->


**Unit 9 - Capstone Criteria**


## 1. Model failure

With `AI201_FAULT=model_error`, 10 of 10 submissions return 200 in degraded mode, and none returns a 500:
- `guess: "unsure"`, with a label saying the text couldn't be fully checked right now
- `"degraded": true` in the response
- `model_score: null` (it never ran); the style score is still recorded, for information only
- a log entry with `degraded: true` and the reason (`model_error`)

Text that is too short to check still gets a 400, as before.

**Why this target:**
With GPT-2 broken, every submission used to crash. The answer has to be "unsure" and not a score from the style signal alone, because my tests showed the style signal is the weaker one and easy to fool, so on its own it could clear AI text as human. "Unsure" never accuses a writer and never claims something the service couldn't check.

## 2. Slow model

With `AI201_FAULT=model_slow` (GPT-2 takes 30 seconds), 10 of 10 submissions answer within 12 seconds, in the same degraded mode as criterion 1, with reason `timeout`.

**Why this target:**
Without a time limit, a slow model makes the writer wait as long as it takes, maybe forever. A normal check takes under a second, so the 10-second limit (`DETECTOR_TIMEOUT_SECONDS`) leaves plenty of room; 12 seconds is that limit plus a margin for the rest of the request. A writer who waits that long should get an honest answer, not a hang.

## 3. Log failure

With `AI201_FAULT=log_error`, 10 of 10 submissions return a JSON 503 ("We couldn't save this result, please try again"), never a 500, and none returns a content ID. Since the log itself failed, each failure is reported to the server console instead.

**Why this target:**
A decision that isn't recorded can't be appealed (`/appeal` would answer "not found") or checked later. Giving a writer a content ID for a decision that was never saved would point them to an appeal that can't work, so the safe answer is to refuse.

## 4. No HTML errors

Every error from either endpoint is JSON: 0 HTML pages across the whole attack set, a JSON array sent to `/appeal`, an unknown URL and a wrong method. An unexpected crash returns a 500 with `{"error": "internal_error", "message": "..."}` and writes an `error` entry to the log.

**Why this target:**
An unexpected error used to show an HTML debug page: programs expecting JSON couldn't read it, it showed my code, and the crash left no trace in the log. A failure that leaves no record can't be found or fixed later, so the target is zero HTML pages, not "few".

## 5. Nothing else changes

With `AI201_FAULT=none`, my 10 own texts get exactly the same scores and labels as in unit 8.

**Why this target:**
The failure handling should only change what happens when something breaks. If it moved any score, I would have changed how the detector judges text, and every result from unit 8 would no longer hold.
