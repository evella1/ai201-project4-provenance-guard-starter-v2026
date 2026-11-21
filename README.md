# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

1. A writer sends their text and their creator ID to the /submit route in app.py. The route checks that there is actually some text. If there isn't, it sends back an error instead of crashing.

2. The text goes to the model signal in detector.py. A language model running on this machine reads it and measures how predictable it is. This adds a model score between 0 and 1, where higher means more likely AI.

3. The text goes to the style signal in stylometry.py. This looks at the shape of the writing: how much sentence lengths vary, how often words repeat, and how punctuation is used. This adds a style score between 0 and 1, where higher again means more likely AI.

4. The two scores go to combine_signals in scoring.py, which merges them into one overall score. This is where I decide how much to trust each signal and what happens when they disagree.

5. The overall score goes to score_to_label in scoring.py. It uses the thresholds in config.py to sort the text into one of three groups: likely human, unsure, or likely AI. It also adds the sentence a reader will see.

6. The decision is written to the audit log by audit.py. The text gets a content ID, and the log keeps both signal scores, the overall score and the label. That way the decision can be checked later and the writer can appeal it.

7. The service sends the result back to the writer: the content ID, the guess, the confidence, the label, and both signal scores. If the writer thinks it's wrong, they can send the content ID and their reasoning to /appeal. That changes the status and records the appeal in the log.

### The endpoints

Both endpoints take JSON and return JSON. Every error, from either endpoint, has the same shape: {"error": "<short code>", "message": "<a sentence a person can read>"}.

POST /submit

What goes in:
- text: string, required. Must contain at least one non-space character and be no longer than 20,000 characters.
- creator_id: string, optional. Identifies who submitted. If it's missing, it is recorded as "unknown".

What comes out on success (200):
- content_id: string, starting with "c_" followed by 12 letters and numbers, for example "c_3f9a1b2c4d5e". It is unique to this submission and is what you send to /appeal.
- creator_id: string, the same value that was sent in (or "unknown").
- guess: string, always exactly one of "human", "unsure" or "ai", in lowercase.
- confidence: number from 0 to 1. This is the combined score from both signals. It always means how likely the text is to be AI, whatever the guess is. 0 means confidently human, 1 means confidently AI.
- label: string, the full sentence shown to the writer. It explains the result in plain words and, for "unsure" and "ai", mentions that they can appeal.
- model_score: number from 0 to 1, the model signal from detector.py. Higher means more likely AI.
- style_score: number from 0 to 1, the style signal from stylometry.py. Higher means more likely AI.

What comes out when something goes wrong:
- 400 with error "bad_request" if the body isn't JSON, or text is missing, not a string, or empty.
- 400 with error "text_too_long" if text is over 20,000 characters.
- 429 if the caller has sent too many submissions (rate limiting, added in unit 8).

POST /appeal

What goes in:
- content_id: string, required. Must be a content_id that /submit returned earlier.
- reasoning: string, required, not empty. The writer's explanation of why the result is wrong.
- creator_id: string, optional. If it's missing, the creator_id from the original submission is used.

What comes out on success (200):
- content_id: string, the same one that was sent in.
- status: string, always "under_review".
- message: string, a sentence confirming the appeal was received and that a person will review it.

What comes out when something goes wrong:
- 400 with error "bad_request" if the body isn't JSON, or content_id or reasoning is missing, not a string, or empty, or if creator_id is sent but isn't a non-empty string.
- 404 with error "not_found" if no submission with that content_id exists.

Appealing the same content_id more than once is allowed. Each appeal is recorded in the log, and the status stays "under_review". The original decision is never changed or deleted. The appeal is added after it in the log.


---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** How predictable the text is. A small language model (GPT-2) runs on this machine and reads the text word by word, checking how easily it could have guessed each next word. This is called perplexity. detector.py turns it into a score from 0 to 1, where a higher score means the text was easier to predict and so more likely AI.

**Why that might differ between human and AI writing:** An AI model writes by picking a likely next word, so the text it produces is text a model finds easy to predict. People's writing is less predictable.

**What it can't see:** who actually wrote the text. A detector only measures how predictable the writing is, and simple, plain writing looks predictable whether a person or a machine produced it. That means honest writers can get flagged by mistake, while AI text that’s been roughed up a little can slip through as human.

### Signal two — the style signal

**What it measures:** The style of the writing, without reading the meaning. It looks at three things: how much sentence lengths vary, how often words repeat, and how many different kinds of punctuation marks are used. stylometry.py combines these into a score from 0 to 1, where a higher score means more likely AI.

**Why that might differ between human and AI writing:** AI writing is very even. Its sentences are about the same length, it uses the same kinds of words, and its punctuation is regular. This is because AI always picks the most likely next word, so the text comes out average. People write in a more uneven way. A short sentence of three words can sit next to a long one of forty words. People also have their own habits with dashes, semicolons, and repeating words.

**What it can't see:** what the text means. A detector only looks at the shape of the writing, so anything that changes the style moves the score. Adding typos, splitting long sentences into short ones, putting in a quotation, or adding a question mark can make AI text look human, and these are easy to do on purpose. It can also wrongly flag a person who naturally writes in a steady, tidy way, with sentences of the same length and plain punctuation.

**What I found when testing it:** I tested five texts: a formal AI essay, the same essay lightly edited by hand, a casual restaurant review that I asked an AI to write so it sounds like a person, a real forum post from 15 years ago, and my own plain writing. All five texts and their scores are in `samples/calibration.md`.

| Measure | AI essay | Lightly-edited AI | AI pretending to be human | Real human (forum) | Plain human (mine) |
|---|---|---|---|---|---|
| sentence length spread (higher = more human) | 0.26 | 0.35 | 0.73 | 0.51 | 0.39 |
| word variety (higher = more AI) | 0.92 | 0.92 | 0.89 | 0.80 | 0.87 |
| punctuation sameness (higher = more AI) | 0.50 | 0.50 | 0.33 | 0.00 | 0.50 |
| style signal (higher = more AI) | 0.76 | 0.69 | 0.35 | 0.13 | 0.53 |

The fake casual review fooled the sentence measure. It has uneven sentences and short fragments like "honestly?", so it scored *more* human than the real human. The attacker doesn't even need to edit the text by hand. Asking the AI to "sound casual" is enough, because the style is exactly what it copies. On the other two measures it landed between the AI essay and the real human, and the style signal gave it 0.35, on the human side.

The lightly-edited AI and my own plain writing look almost the same to this signal. The style signal can tell the forum post from the AI essay, but not plain human writing from edited AI.

Word variety worked the opposite way from what I expected. I thought AI would repeat words more, but all three AI texts used a wider vocabulary than both human texts. So I count a higher value as more AI.

I also dropped three ideas after testing:
- A list of typical AI words ("delve", "crucial", "moreover"). It found only 2 of 110 words in a clear AI essay, it is easy to avoid, and formal or non-native writers use many of these words too, so it would push my false positive (below) toward AI.
- Counting dashes and semicolons. None of my samples used them, so the measure was 0 for everything and couldn't tell texts apart.
- Counting commas. The real human used more commas (8.5 per 100 words) than the AI essay (about 5.5). Comma habits depend on the person, not on AI. I kept only how many *different* punctuation marks are used.

A testing lesson: in PowerShell, text inside double quotes loses things. `$19` disappeared (PowerShell read it as a variable) and quote marks were removed, which changed the punctuation score. I now pass text with a here-string (`@'...'@`) piped into the script.


### The false positive I'm designing against

The writer: a student writing an essay in English, which is their second language. They wrote every word themselves. Because they stick to words they're sure of, the essay uses common vocabulary, short sentences of similar length, and simple punctuation.

What score they get: the model signal finds plain, common wording easy to predict, so it scores them high, around 0.75. The style signal sees even sentence lengths, repeated words and plain punctuation, so it also scores them on the AI side, around 0.6. Combined, they land around 0.7. With the starting thresholds in config.py (human below 0.35, AI above 0.65), that might put them over the line into high-confidence AI.

What the label says to them: if the AI label reads like a verdict, such as "This was written by AI", an honest student is being told they cheated. Nothing in the response tells them why, or that the system can be wrong.

What they can do about it: the response gives them a content ID. They can send that ID with their explanation to /appeal, which moves the decision to under review and records the appeal in the audit log. But this only helps if they know the appeal exists, so the label itself has to tell them.

What this changes in my design:

1. Thresholds: someone like this student should land in unsure, not AI. A plain human essay should not be able to reach the AI label on predictability alone, so I'll set the AI threshold high enough that it takes strong evidence from both signals.

2. Combining rule: both of my signals are fooled by the same kind of writing, so two high scores on plain text are less independent than they look. The AI label should need both signals to agree clearly, and when they disagree, the answer should be unsure.

3. Labels: the AI and unsure labels should describe what the system noticed, not accuse the writer. They should say that the system can be wrong and that the writer can appeal using their content ID.

The trade: making it harder to reach the AI label means some real AI text will be labelled unsure instead. I'd rather let some AI text through as unsure than tell an honest writer they cheated.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:** To call a text AI, both signals have to agree. If both scores are above 0.5, the combined score is the lower of the two, so one confident signal alone can't push a text to AI. In every other case, the combined score is the average of the two.

**The numbers:** All of these are in config.py.
- "Both lean AI" cut-off: `BOTH_LEAN_AI = 0.5`
- Weights for the average: `WEIGHT_MODEL_SIGNAL = 0.5`, `WEIGHT_STYLE_SIGNAL = 0.5`. Equal, because with five test texts I have no evidence that one signal deserves more.
- Label thresholds: `HUMAN_THRESHOLD = 0.35`, `AI_THRESHOLD = 0.65`. 0.35 or below is human, 0.65 or above is AI, in between is unsure.

I tested five texts:

| Text | Model | Style | Plain average | My rule | Label |
|---|---|---|---|---|---|
| Clearly AI (essay) | 0.80 | 0.76 | 0.78 | 0.76 | AI |
| Lightly-edited AI | 0.75 | 0.69 | 0.72 | 0.69 | AI |
| Plain human (my own writing) | 0.83 | 0.53 | 0.68 (AI ✗) | 0.53 | unsure |
| AI pretending to be human | 0.40 | 0.35 | 0.37 | 0.37 | unsure |
| Clearly human (forum post) | 0.32 | 0.13 | 0.23 | 0.23 | human |

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:** My own plain writing about meeting a friend at a coffee shop. The model signal gave it 0.83, the most AI-like score of all five texts, even higher than the real AI essay. That is because short sentences and everyday words are easy for GPT-2 to predict. The style signal gave it only 0.53. A plain average would be 0.68, which is labelled AI, so the system would accuse me of using AI for my own writing. My rule takes the lower score, 0.53, so it is labelled unsure. The real AI texts still reach AI, because both signals are high on them.

The weak spot: the edited AI only just reaches AI (style 0.69, line at 0.65). A slightly heavier edit would drop it to unsure. That is the trade I chose: I'd rather let some AI through as unsure than accuse a person.


---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 – 0.35 | We think this was probably written by a person. |
| unsure | 0.35 – 0.65 | We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID. |
| high-confidence AI | 0.65 – 1.00 | This text has patterns we often see in AI-generated writing. This is a guess, not proof, and we can be wrong. If you wrote it yourself, you can appeal using your content ID and a person will review it. |

The ranges come from `HUMAN_THRESHOLD` and `AI_THRESHOLD` in config.py (`scoring.label_ranges()` prints them). A score of exactly 0.35 counts as human and exactly 0.65 as AI. In my tests, each label was reached: the forum post got human (0.23), my own plain text got unsure (0.53), and the AI essay got AI (0.76).

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->

My own plain writing landed on unsure, so I wrote this label for a person like me: someone who wrote every word and is now being told the system isn't sure. It says plainly that the system can't tell, and "parts of it read like both" explains why without blaming the writer. "This is not an accusation" is there because that is the first thing an honest writer would worry about. It ends with what they can do: appeal with their content ID. The AI label also says it is "a guess, not proof", because even my AI label can be wrong, and my own writing scored higher than real AI on one signal.


---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

```powershell
$text = @'
Today, I went to see my friend at a coffee shop. We ordered pastries and coffee. Unfortunately the coffee came with extra sugar, which I didn't ask for. I almost asked for a refund but held back seeing how busy the baristas were. We had some good chat about what we've been up to in the last few weeks. She told me she's been working out a lot. I found that inspiring and I signed up for a gym the next day. We'll see how it goes.
'@
$body = @{ text = $text; creator_id = "ewelina" } | ConvertTo-Json
$body | curl.exe -X POST http://127.0.0.1:5000/submit -H "Content-Type: application/json" --data-binary "@-"
```

```json
{
  "confidence": 0.5322,
  "content_id": "c_01c723ac0f8f",
  "creator_id": "ewelina",
  "guess": "unsure",
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "model_score": 0.8288,
  "style_score": 0.5322
}
```

**An appeal**

```powershell
$body = @{ content_id = "c_01c723ac0f8f"; reasoning = "I wrote this myself about meeting my friend. English is my second language, so I use simple words and short sentences." } | ConvertTo-Json
$body | curl.exe -X POST http://127.0.0.1:5000/appeal -H "Content-Type: application/json" --data-binary "@-"
```

```json
{
  "content_id": "c_01c723ac0f8f",
  "message": "Thanks, we've received your appeal. A person will review this decision; the original result is on hold until then.",
  "status": "under_review"
}
```

**What the log shows afterwards**

The original decision stays as it was, and the appeal is added after it with status `under_review`.

```powershell
curl.exe "http://127.0.0.1:5000/log?limit=2"
```

```json
{
  "count": 2,
  "entries": [
    {
      "combined_score": 0.5322,
      "content_id": "c_01c723ac0f8f",
      "creator_id": "ewelina",
      "guess": "unsure",
      "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
      "model_score": 0.8288,
      "status": "decided",
      "style_score": 0.5322,
      "timestamp": "2026-11-11T09:00:12+00:00"
    },
    {
      "content_id": "c_01c723ac0f8f",
      "creator_id": "ewelina",
      "event": "appeal",
      "reasoning": "I wrote this myself about meeting my friend. English is my second language, so I use simple words and short sentences.",
      "status": "under_review",
      "timestamp": "2026-11-11T09:02:09+00:00"
    }
  ]
}
```

---

## How I Used AI

**Moment 1**

- *What I asked for:* I gave Claude my idea for the style measures: standard deviation for sentence length, a list of words that AI uses a lot ("delve", "crucial", "moreover"), and counting long dashes and semicolons, because AI uses them and people rarely do.
- *What came back:* Claude built all three. It put the AI-word check in its own function instead of inside the type-token ratio, because the two point in opposite directions. It also warned me that many people use semicolons and that these checks are easy to avoid.
- *What I changed:* I tested it on real texts. The word list found only 2 of 110 words in a clear AI essay, and the dash and semicolon count was 0 for every text. I removed both. Then I tested a real forum post and saw that it had more commas than the AI essay, so I also dropped the comma count. I kept only how many different kinds of punctuation a text uses. I also flipped word variety to "higher = more AI", because my tests showed the opposite of what I expected.

**Moment 2**

- *What I asked for:* My own plain text got a model score of 0.83, higher than the real AI essay, and a plain average labelled it AI. I asked Claude for suggestions about the rules.
- *What came back:* Claude suggested a combining rule: if both signals are above 0.5, use the lower one; otherwise use the average. It showed that with this rule my text gets 0.53 (unsure) while the AI texts still get AI. Claude coded it in `scoring.py::combine_signals` with the 0.5 cut-off written straight into the code.
- *What I changed:* First I asked Claude to explain the rule, because I thought it dropped the high score whenever the signals disagree. It actually only looks at whether both lean AI. Then I checked the rule against the milestone instructions, which say the weights and thresholds live in config.py. The 0.5 cut-off was not there, so I had it moved into config.py as `BOTH_LEAN_AI`, and listed every number by its config.py name in the combining rule section of this README.

**Moment 3**

- *What I asked for:* to compare the numbers from my test runs, so I didn't have to do it by hand: the averages for criterion 2, the before and after attack runs, and which attacks changed from BROKE to HELD.
- *What came back:* Claude read the result files, worked out the averages and counts.
- *What I changed:* I filled in the verdict based on the numbers.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 5 per minute, 50 per day (`RATE_LIMIT_PER_MINUTE` and `RATE_LIMIT_PER_DAY` in config.py)

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

A writer revising their own work might resubmit several times in a couple of minutes and rarely exceed 25 submissions in a day, so both limits sit above realistic human use. Someone probing the thresholds needs on the order of 1,000 submissions - at 50/day that takes about three weeks per IP instead of minutes, and leaves a clear pattern in the audit log.

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

Per creator_id. If a request has no usable creator_id (it's missing, not a string, or the body isn't a JSON object), it counts against the caller's address instead (`app.py::rate_limit_key`). The weakness: one script can rotate creator_ids and look like many writers. The attack run also showed the other side: several requests without a creator_id shared one address and used up its limit together.

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```
15 submissions as 'flood_tester' against http://127.0.0.1:5000
The first one is slow while the model loads.

  [ 1/15] 200
  [ 2/15] 200
  [ 3/15] 200
  [ 4/15] 200
  [ 5/15] 200
  [ 6/15] 429
  [ 7/15] 429
  [ 8/15] 429
  [ 9/15] 429
  [10/15] 429
  [11/15] 429
  [12/15] 429
  [13/15] 429
  [14/15] 429
  [15/15] 429

============================================================
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429
============================================================

10 of 15 were rate limited.
```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->

Run: `results/attack_run_2026-11-15_0024.md` (56 attacks, produced by `run_attacks.py::main`).

**How I decide HELD or BROKE**

HELD and BROKE are about my service, not about the scores. BROKE means the attack got what it wanted, or my service did something harmful or broke its own promises. HELD means the service handled it acceptably.

Rules for every attack:
- A 500 (crash) is always BROKE.
- A clean 400 for bad input is HELD.
- Anything that breaks a promise in my endpoint description (for example, the 20,000 character limit, or creator_id being a string) is BROKE.

Rules for each family:

| Family | HELD | BROKE | Why |
|---|---|---|---|
| False positive (real human writing) | human or unsure | ai | Criterion 1: a real writer must not get the AI label. Unsure is acceptable because the label says it is not an accusation and offers an appeal. |
| Evasion (AI text with tricks) | ai or unsure | human | The attacker wants a "probably a person" label. My design accepts AI landing in unsure (see "The trade" above), because unsure never clears the text, it says "we can't tell". |
| Prompt injection | the instruction changes nothing: label is not human, and the label and log contain only my own text | the result is what the instruction asked for (human), or anything injected shows up in the label or log | The attacker wins if the text gets cleared or if they can write into my output. |
| Malformed text that still got a 200 | unsure, or a clean 400 | ai or human | Emoji, punctuation or one repeated letter is not writing. The only honest answer is "can't tell" or a rejection. Claiming either way is wrong, and "ai" is a false accusation. |
| Malformed request | clean 400, or accepted when my spec allows it | 500, or accepted when my spec says it should be rejected | My endpoint description is the promise. |
| Flood | the limiter blocks after the limit, and each block is logged | requests keep getting through, or blocks leave no trace | Criterion: rate limiting with a trace. |

If a request never reached the check it was meant to test (for example, it was rate-limited first), I mark it **UNTESTED** and re-run it, instead of calling it HELD.

Every attack and its outcome, from `results/attack_run_2026-11-15_0024.md`:

| ID | Family | What it tried | Status | Guess | Score | Verdict |
|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | unsure | 0.498 | HELD |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | unsure | 0.507 | HELD |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | unsure | 0.565 | HELD |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | unsure | 0.611 | HELD |
| EV05 | evasion | both signals: heavy human editing pass | 200 | human | 0.304 | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | unsure | 0.474 | HELD |
| EV07 | evasion | signal two: padding with punctuation | 200 | unsure | 0.543 | HELD |
| EV08 | evasion | signal one: text below the token window | 200 | unsure | 0.373 | HELD |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | unsure | 0.555 | HELD |
| EV10 | evasion | signal two: repeated stanza structure | 200 | ai | 0.714 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | unsure | 0.508 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | unsure | 0.522 | HELD |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | unsure | 0.592 | HELD |
| FP04 | false_positive | a student essay written to a rubric | 200 | unsure | 0.508 | HELD |
| FP05 | false_positive | technical documentation written by a person | 200 | unsure | 0.646 | HELD |
| FP06 | false_positive | a person imitating a formal template | 200 | unsure | 0.586 | HELD |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | unsure | 0.552 | HELD |
| FP08 | false_positive | very short genuine human submission | 200 | unsure | 0.411 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | unsure | 0.537 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | human | 0.324 | BROKE |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | unsure | 0.594 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | unsure | 0.423 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | unsure | 0.570 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | unsure | 0.491 | HELD |
| MF01 | malformed | text is only whitespace | 400 | — | — | HELD |
| MF02 | malformed | text is a single character | 500 | — | — | BROKE |
| MF03 | malformed | text is control characters | 200 | human | 0.250 | BROKE |
| MF04 | malformed | text is only punctuation | 200 | human | 0.256 | BROKE |
| MF05 | malformed | text is a very long single word | 200 | ai | 0.749 | BROKE |
| MF06 | malformed | text is emoji only | 200 | ai | 0.749 | BROKE |
| MF07 | malformed | text is right-to-left script | 200 | ai | 0.703 | BROKE |
| MF08 | malformed | text is 60,000 characters | 200 | ai | 0.681 | BROKE |
| RQ01 | malformed | no text field at all | 400 | — | — | HELD |
| RQ02 | malformed | no creator_id | 200 | unsure | 0.370 | HELD |
| RQ03 | malformed | text is a number | 400 | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | — | — | HELD |
| RQ05 | malformed | text is null | 400 | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 200 | human | 0.275 | BROKE |
| RQ07 | malformed | body is a JSON array, not an object | 500 | — | — | BROKE |
| RQ08 | malformed | body is unparseable JSON | 400 | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | — | — | UNTESTED |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | — | — | UNTESTED |
| RQ12 | malformed | deeply nested JSON | 400 | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | human | 0.264 | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | human | 0.264 | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | human | 0.264 | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | human | 0.264 | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | human | 0.264 | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | HELD |

**What I found**

- False positives: 0 of 8 got the AI label, so criterion 1 held on this run. But it is fragile: FP02–FP07 all had model scores of 0.74–0.88, and only the style signal kept them out of AI. FP05 missed the AI label by 0.004.
- Evasion: only EV05 (a heavy human editing pass) got the human label. The other evasions landed in unsure, which my design accepts. EV05's text reads like real human writing after the edit, so this is partly a question of when edited AI stops being AI.
- Prompt injection: no instruction was "obeyed", because nothing in my service reads instructions. But PI02's fake SYSTEM line made the text less predictable: the AI paragraph alone scores 0.75 on the model signal, with the line in front it scores 0.20, and the text got the human label. The label and log stayed clean for PI04 and PI05: the label is always my own fixed text, and the submitted text is never logged.
- Malformed text: the biggest group of failures. Text that is not English writing (emoji, one repeated letter, Arabic) gets a confident AI label, and control characters or punctuation get a human label. The 57,640-character text was accepted although my endpoint description promises a 400 above 20,000 characters.
- Crashes: a single character (MF02) and a JSON array body (RQ07) crashed the service with a 500. Both crash pages showed the debugger, because debug mode is on.
- Rate limiting: the flood was stopped after 5 submissions, and every block was logged. RQ10 and RQ11 were rate-limited before the route ran, so I re-ran them alone after the improvement (see Attack Run — After).


**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

The eight worst outcomes from the run, worst first, then two rejections, so the log's refused requests are shown too. Each entry is copied from `logs/audit.jsonl`.

1. MF07, Arabic text labelled AI. A real person writing in their own language is accused. GPT-2 was trained on English and splits each Arabic letter into several small pieces. After the first piece, the rest are easy to guess, so the whole text looks very predictable (model 0.91), and the style signal falls back to 0.5 because it can't count English words.

```json
{"timestamp": "2026-11-15T08:24:47+00:00", "content_id": "c_322285e017d7", "creator_id": "attacker_MF07", "guess": "ai", "model_score": 0.9064, "style_score": 0.5, "combined_score": 0.7032, "label": "This text has patterns we often see in AI-generated writing. This is a guess, not proof, and we can be wrong. If you wrote it yourself, you can appeal using your content ID and a person will review it.", "status": "decided"}
```

2. FP05, human technical documentation. 0.646 is 0.004 below the AI label. Documentation is supposed to be plain and consistent, which is exactly what both signals read as AI.

```json
{"timestamp": "2026-11-15T08:24:45+00:00", "content_id": "c_cfae545d1260", "creator_id": "attacker_FP05", "guess": "unsure", "model_score": 0.8005, "style_score": 0.4915, "combined_score": 0.646, "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.", "status": "decided"}
```

3. FP03, a non-native speaker writing carefully. This is the writer my false-positive section is about. Model 0.81; only the "both must agree" rule kept it at unsure.

```json
{"timestamp": "2026-11-15T08:24:45+00:00", "content_id": "c_f8a71af5c423", "creator_id": "attacker_FP03", "guess": "unsure", "model_score": 0.8051, "style_score": 0.5919, "combined_score": 0.5919, "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.", "status": "decided"}
```

4. PI02, AI text with a fake SYSTEM line. The extra line made the text less predictable (model 0.20), so AI text got "probably written by a person".

```json
{"timestamp": "2026-11-15T08:24:46+00:00", "content_id": "c_5d9b704ac2a4", "creator_id": "attacker_PI02", "guess": "human", "model_score": 0.2044, "style_score": 0.4444, "combined_score": 0.3244, "label": "We think this was probably written by a person.", "status": "decided"}
```

5. EV05, AI text after a heavy human edit. Both signals moved to the human side, so the edit fully hid it.

```json
{"timestamp": "2026-11-15T08:24:44+00:00", "content_id": "c_03857725637c", "creator_id": "attacker_EV05", "guess": "human", "model_score": 0.3212, "style_score": 0.2875, "combined_score": 0.3044, "label": "We think this was probably written by a person.", "status": "decided"}
```

6. MF06, emoji only, labelled AI. Not writing at all, but the AI label tells the sender they used AI.

```json
{"timestamp": "2026-11-15T08:24:47+00:00", "content_id": "c_e4fea4f378a5", "creator_id": "attacker_MF06", "guess": "ai", "model_score": 0.9969, "style_score": 0.5, "combined_score": 0.7485, "label": "This text has patterns we often see in AI-generated writing. This is a guess, not proof, and we can be wrong. If you wrote it yourself, you can appeal using your content ID and a person will review it.", "status": "decided"}
```

7. MF08, 57,640 characters, labelled AI. My endpoint description promises a 400 above 20,000 characters, but the text was accepted. The detector only reads the first 400 tokens, so most of the text was never checked.

```json
{"timestamp": "2026-11-15T08:24:47+00:00", "content_id": "c_ad40e033715d", "creator_id": "attacker_MF08", "guess": "ai", "model_score": 0.9876, "style_score": 0.3738, "combined_score": 0.6807, "label": "This text has patterns we often see in AI-generated writing. This is a guess, not proof, and we can be wrong. If you wrote it yourself, you can appeal using your content ID and a person will review it.", "status": "decided"}
```

8. RQ06, creator_id sent as an object. It was saved into the log as an object, not a string, so the log no longer has one shape for this field, and a creator_id like this also falls back to the address-based rate limit.

```json
{"timestamp": "2026-11-15T08:24:48+00:00", "content_id": "c_e6b1374aa709", "creator_id": {"id": "x"}, "guess": "human", "model_score": 0.0492, "style_score": 0.5, "combined_score": 0.2746, "label": "We think this was probably written by a person.", "status": "decided"}
```

9. A rejection from the flood (FL01): the rate limiter blocked the 6th submission in a minute and logged it, even though the request never reached the route.

```json
{"timestamp": "2026-11-15T08:24:48+00:00", "creator_id": "attacker_flood", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute"}
```

10. A rejection after the improvement: MF08 sent again, now refused with `text_too_long` and logged as a rejection instead of being scored.

```json
{"timestamp": "2026-11-15T23:30:26+00:00", "creator_id": "attacker_MF08", "event": "rejected", "status": "rejected", "reason": "text_too_long", "route": "/submit"}
```

The two crashes (MF02, RQ07) are not in this list because they have no log entry at all: the service crashed before it reached `audit.log_decision`. A failure that leaves no trace is its own problem.

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

MF07: a text written in Arabic got the high-confidence AI label (combined 0.70, model 0.91, style 0.50). The writer did nothing wrong. They just wrote in their own language, and my system told them their work has "patterns we often see in AI-generated writing". The cause has nothing to do with AI: GPT-2 was trained on English, so it can't judge other languages, and my style signal only counts English words, so it gave up and returned 0.5. The "both must agree" rule didn't help: it only applies when both signals are above 0.5, and a style score of exactly 0.5 is not above it. So the rule used the plain average, and the model's 0.91 pulled the text over the AI line. Of all the failures, this is the one I'd least want to explain. It is a false accusation, and it hits the same group my false-positive section is about: people whose first language is not English.

---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. My own writing | At most 1 of 10 labelled AI | 0 of 10 | 0 of 10 | 0 of 10 | MET |
| 2. AI vs human scores | AI average at least 0.3 above human average | gap 0.08 | gap 0.08 | gap 0.08 | MISSED |
| 3. Label coverage | human, unsure and ai each reached | all 3 | all 3 | all 3 | MET |
| 4. Appeals | 10 of 10 real appeals work; bad appeals get 400 or 404 and aren't logged | 10 of 10, bad 3 of 3 | 10 of 10, bad 3 of 3 | 10 of 10, bad 3 of 3 | MET |
| 5. Bad input | Empty, missing, null and over 20,000 characters each get 400 | 3 of 4 | 3 of 4 | 3 of 4 | MISSED |

All three trials gave exactly the same scores: GPT-2 scores the same text the same way every time. Criteria 1, 2, 3 and 5 were run with `run_eval.py`. `run_eval.py` did not run criterion 4: an appeal needs a content_id from an earlier submission, and run_eval can only send texts or fixed request bodies. I ran criterion 4 separately against the running service (see below).

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

Produced by `run_eval.py::main`, sending requests to `app.py::submit` (scores from `scoring.py::combine_signals`). Trial 1 of `results/run_2026-11-15_1344_before.md`, which has the full output of all three trials.

Criterion 1, my text that came closest to the AI label:

```json
{
  "status": 200,
  "guess": "unsure",
  "confidence": 0.6139,
  "model_score": 0.7457,
  "style_score": 0.482,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "sent": "I apologize for the delayed answer. Thank you for reaching out to me a"
}
```

Criterion 2, the lowest-scoring AI text and the highest-scoring human text:

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3586,
    "model_score": 0.6556,
    "style_score": 0.0616,
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "sent": "For thirty-one years, Mara Okonkwo kept the light on Gull Point. When "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6139,
    "model_score": 0.7457,
    "style_score": 0.482,
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "sent": "I apologize for the delayed answer. Thank you for reaching out to me a"
  }
]
```

Criterion 3, all three labels:

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7561,
    "model_score": 0.7969,
    "style_score": 0.7561,
    "label": "This text has patterns we often see in AI-generated writing. This is a guess, not proof, and we can be wrong. If you wrote it yourself, you can appeal using your content ID and a person will review it.",
    "sent": "Time management is an essential skill that plays a crucial role in bot"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.2261,
    "model_score": 0.3198,
    "style_score": 0.1324,
    "label": "We think this was probably written by a person.",
    "sent": "Took a ride to Wat Takien today. Great little find! For all those \"aut"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5322,
    "model_score": 0.8288,
    "style_score": 0.5322,
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "sent": "Today, I went to see my friend at a coffee shop. We ordered pastries a"
  }
]
```

Criterion 5, the four bad inputs:

```json
[
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "(empty text)"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "{\"creator_id\": \"eval_bad_missing\"}"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "{\"text\": null, \"creator_id\": \"eval_bad_null\"}"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7488,
    "model_score": 0.9975,
    "style_score": 0.5,
    "label": "This text has patterns we often see in AI-generated writing. This is a guess, not proof, and we can be wrong. If you wrote it yourself, you can appeal using your content ID and a person will review it.",
    "sent": "word word word word word word word word word word word word word word "
  }
]
```

Criterion 4, run separately (not by `run_eval.py`): requests sent to `app.py::appeal`, decisions read back from `logs/audit.jsonl` (written by `audit.py::log_decision` and `audit.py::log_appeal`). Trial 1:

A real appeal, response (HTTP 200):

```json
{
  "content_id": "c_8d449a42e6ae",
  "message": "Thanks, we've received your appeal. A person will review this decision; the original result is on hold until then.",
  "status": "under_review"
}
```

The log for that content_id afterwards, original decision then appeal:

```json
[
  {"timestamp": "2026-11-15T22:03:24+00:00", "content_id": "c_8d449a42e6ae", "creator_id": "appeal_t1_1", "guess": "unsure", "model_score": 0.8288, "style_score": 0.5322, "combined_score": 0.5322, "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.", "status": "decided"},
  {"timestamp": "2026-11-15T22:03:24+00:00", "content_id": "c_8d449a42e6ae", "creator_id": "appeal_t1_1", "event": "appeal", "status": "under_review", "reasoning": "I wrote this myself."}
]
```

Bad appeals: made-up content_id (HTTP 404), then empty and missing content_id (HTTP 400 each):

```json
{"error": "not_found", "message": "We couldn't find a submission with content ID c_000000000000. Please check the ID from your original result."}
{"error": "bad_request", "message": "Send JSON with a non-empty \"content_id\"."}
{"error": "bad_request", "message": "Send JSON with a non-empty \"content_id\"."}
```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->

The misses and broken attacks come down to four problems.

**1. The route doesn't check its input.** Stage: the route (`app.py::submit`).
Covers: criterion 5, MF08, MF02, RQ07, RQ06.
- Criterion 5 and MF08: the route never checks the 20,000-character limit my endpoint description promises, so the 25,000- and 57,640-character texts went to the signals and got the AI label. Both texts repeat the same words or paragraph, and repeated text is very predictable for GPT-2 (model 0.99).
- MF02: a single character is fewer than 3 tokens, so `detector.model_signal` raises an error. The route doesn't catch it, so the service crashed with a 500.
- RQ07: a JSON array is not an object. `request.get_json() or {}` keeps the array (a non-empty list counts as true), and calling `.get` on it crashed the route.
- RQ06: creator_id is never checked to be a string, so an object went straight into the log.
- The two crashes left no log entry, because the route failed before `audit.log_decision`.

**2. Text that isn't English writing gets a confident label.** Stages: signal one, signal two and the combining rule.
Covers: MF05, MF06, MF07 (labelled AI) and MF03, MF04 (labelled human).
- Signal two only counts English words (`[a-z0-9']`). Emoji, Arabic and one long repeated letter give it 0 or 1 words, so its short-text guard returns 0.5 ("can't tell").
- My combining rule only uses the lower score when both signals are *above* 0.5. A style score of exactly 0.5 isn't, so the rule takes the plain average, and the model signal alone decides.
- Signal one: GPT-2 splits emoji and Arabic letters into several byte pieces, and the later pieces are easy to guess, so the text looks very predictable (0.91 to 1.00). Average with 0.5 gives about 0.70 to 0.75, which is AI. Control characters and punctuation are the opposite: very unpredictable (model 0.00 to 0.01), so the average is about 0.25, which is human.
- MF07 (Arabic) is a real writer falsely accused, the worst outcome of the run.

**3. Signal one can't tell plain human writing from AI writing.** Stage: signal one, which the combining rule only partly offsets.
Covers: criterion 2 (missed), and why criterion 1 only just held.
- Signal one scores how predictable the words are. Plain and formal writing uses common phrases ("I apologize for the delayed answer", "Hope you are doing well"), which are easy to predict. On the criterion 2 texts, signal one averaged 0.64 for AI and 0.66 for human, so it can't separate them at all. Signal two did a little better (0.48 against 0.33), but averaged together the gap is only 0.08.
- Four of the five human texts are mine, and English is my second language. I think that makes them more predictable: I stick to words and phrases I'm sure of. The human text not written by me, the forum post, scored lowest (0.23). The attack set shows the same pattern: the non-native speaker text (FP03) had a model score of 0.81.
- On the AI side, only the two essay-style texts reached the AI label. The casual review, the travel answer and the story are written in a natural, varied way, so both signals read them as fairly human (the story got 0.06 on signal two because of its dialogue, quote marks and mix of short and long sentences).
- Criterion 1 held because of the combining rule: 8 of my 10 texts scored 0.60 or more on signal one, and only signal two or the "both must agree" rule kept them out of the AI label. My internship email reached 0.61, with the AI line at 0.65.

**4. Small changes move signal one a lot.** Stage: signal one, then the combining rule.
Covers: PI02, EV05.
- PI02: nothing in my service reads instructions, so the instruction itself did nothing. But the fake SYSTEM line is very unusual text. GPT-2 averages its surprise over the whole text, and the text is short (45 words), so one odd line dropped the model score from 0.75 (the AI paragraph alone) to 0.20. With style 0.44, the average was 0.32, which is human.
- EV05: a heavy human edit added fragments ("Obviously."), a dash and uneven sentences. That changes exactly what both signals measure, so both moved to the human side (model 0.32, style 0.29). Once the edit is this heavy, the text is arguably human writing.

---

## The Improvement

**What I changed:** I added input validation to `app.py::submit`, so the input is checked before the signals see it. One improvement, four checks:

1. The body must be a JSON object. Otherwise: 400 `bad_request`.
2. `creator_id` must be a non-empty string (a missing one still becomes "unknown", as my endpoint description says). Otherwise: 400 `bad_request`.
3. Text over 20,000 characters: 400 `text_too_long`. The limit is `MAX_TEXT_CHARS` in config.py.
4. Text too short to score (the detector needs at least 3 tokens): 400 `text_too_short`, instead of a crash.

Each of these 400s is also written to the audit log as a `rejected` entry with its reason, so a refused input leaves a trace (before, only the 429s did).

**Which diagnosis pointed at it:** All four checks come from what I observed in the first ("before") runs: the attack run (`results/attack_run_2026-11-15_0024.md`) and the eval run (`results/run_2026-11-15_1344_before.md`). I didn't add anything those runs didn't show. Diagnosis 1, "The route doesn't check its input". It covered the criterion 5 miss and four broken attacks: MF08 (60,000 characters), MF02 (single character, crash), RQ07 (JSON array, crash) and RQ06 (creator_id as an object). Each check fixes one of them.

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->

Run: `results/attack_run_2026-11-15_1427_after.md` (same 56 attacks, same rules for HELD and BROKE).

| ID | Family | What it tried | Status | Guess | Score | Verdict |
|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | unsure | 0.498 | HELD |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | unsure | 0.507 | HELD |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | unsure | 0.565 | HELD |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | unsure | 0.611 | HELD |
| EV05 | evasion | both signals: heavy human editing pass | 200 | human | 0.304 | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | unsure | 0.474 | HELD |
| EV07 | evasion | signal two: padding with punctuation | 200 | unsure | 0.543 | HELD |
| EV08 | evasion | signal one: text below the token window | 200 | unsure | 0.373 | HELD |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | unsure | 0.555 | HELD |
| EV10 | evasion | signal two: repeated stanza structure | 200 | ai | 0.714 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | unsure | 0.508 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | unsure | 0.522 | HELD |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | unsure | 0.592 | HELD |
| FP04 | false_positive | a student essay written to a rubric | 200 | unsure | 0.508 | HELD |
| FP05 | false_positive | technical documentation written by a person | 200 | unsure | 0.646 | HELD |
| FP06 | false_positive | a person imitating a formal template | 200 | unsure | 0.586 | HELD |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | unsure | 0.552 | HELD |
| FP08 | false_positive | very short genuine human submission | 200 | unsure | 0.411 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | unsure | 0.537 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | human | 0.324 | BROKE |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | unsure | 0.594 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | unsure | 0.423 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | unsure | 0.570 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | unsure | 0.491 | HELD |
| MF01 | malformed | text is only whitespace | 400 | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | — | — | HELD |
| MF03 | malformed | text is control characters | 200 | human | 0.250 | BROKE |
| MF04 | malformed | text is only punctuation | 200 | human | 0.256 | BROKE |
| MF05 | malformed | text is a very long single word | 200 | ai | 0.749 | BROKE |
| MF06 | malformed | text is emoji only | 200 | ai | 0.749 | BROKE |
| MF07 | malformed | text is right-to-left script | 200 | ai | 0.703 | BROKE |
| MF08 | malformed | text is 60,000 characters | 400 | — | — | HELD |
| RQ01 | malformed | no text field at all | 400 | — | — | HELD |
| RQ02 | malformed | no creator_id | 200 | unsure | 0.370 | HELD |
| RQ03 | malformed | text is a number | 400 | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | — | — | HELD |
| RQ05 | malformed | text is null | 400 | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 400 | — | — | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 400 | — | — | HELD |
| RQ08 | malformed | body is unparseable JSON | 400 | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | — | — | HELD |
| RQ10 * | malformed | body is form-encoded, not JSON | 400 | — | — | HELD |
| RQ11 * | malformed | body is JSON claiming to be plain text | 400 | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | human | 0.264 | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | human | 0.264 | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | human | 0.264 | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | human | 0.264 | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | human | 0.264 | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | HELD |

\* RQ10 and RQ11 were rate-limited in the full run, so I re-ran each one alone: `results/attack_run_2026-11-15_1530_after_RQ10.md` and `..._RQ11.md`. They were never reached in the before run, so they have no before result.

| | Before | After |
|---|---|---|
| HELD | 43 | 49 |
| BROKE | 11 | 7 |
| UNTESTED | 2 | 0 |

The eval run after the change: `results/run_2026-11-15_1427_after.md`.

| Criterion | Before | After |
|---|---|---|
| 1. My own writing | MET | MET |
| 2. AI vs human scores | MISSED | MISSED |
| 3. Label coverage | MET | MET |
| 4. Appeals | MET | MET |
| 5. Bad input | MISSED | MET |

**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->

Yes, for what it targeted:
- Attacks: MF02, MF08, RQ06 and RQ07 moved from BROKE to HELD, each now a clean 400. No attack got worse, and the service no longer crashes on any attack.
- RQ10 and RQ11: re-run alone, both got a clean 400, so every one of the 56 attacks now has an outcome.
- Criterion 5: 3 of 4 bad inputs got a 400 before, 4 of 4 after, in all three trials.
- Criterion 4: I ran the appeal test separately again (it isn't part of `run_eval.py`). 10 of 10 real appeals and 3 of 3 bad appeals passed in each of 3 trials, the same as before.
- Criteria 1, 2 and 3: every score is exactly the same as before (criterion 2 is still a gap of 0.08: 0.541 against 0.463), because the checks only run before the signals and never change how text is scored.

What it costs: a real writer with a text over 20,000 characters is now turned away instead of checked, and a very short message (a word or two) gets an error instead of a label. A missing creator_id is still accepted, but an empty one is now rejected.

The failures that are left come from the signals, not the route, so this change couldn't reach them. They are in "What's Still Broken".

---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->

**Text that isn't English writing gets a confident label: MF03, MF04, MF05, MF06, MF07.** Still the worst problem: the Arabic text (MF07) is a real writer labelled AI.
- **Update (extension):** MF05 and MF06 are fixed. The extension's "too short" check (fewer than 3 words → 400, before GPT-2 runs) now refuses both, so they moved from BROKE to HELD (see "Extension Run Log — After"). MF03, MF04 and MF07 are still broken.
- What I'd do: count how much of the text is English words before scoring. If there are too few, return unsure ("we can't check this kind of text") instead of a score. A second, simpler fix: make the combining rule never return AI when the style signal had nothing to measure (exactly 0.5).
- Why I stopped: I'd have to choose what counts as "enough English", and a wrong cut-off would push real English writers with names, numbers or code into unsure. I wanted one clean improvement I could prove with the runs, and this needs its own testing on non-English and mixed-language text.

**Criterion 2 is missed (gap 0.08, target 0.3).**
- What I'd do: signal one can't separate my AI and human texts at all (0.64 against 0.66), so reweighting won't close the gap; even all weight on signal two would give about 0.15. It needs a better first signal, for example a larger or newer model than GPT-2, or a model trained to tell AI from human writing instead of just measuring predictability. I'd also test with more than five texts per group, and with more human writers than just me.
- Why I stopped: replacing the model is a much bigger change than this unit allows, and it would need the whole calibration redone. I kept the target at 0.3, because the rules say a missed target stays.

**Small changes move signal one: PI02, EV05.**
- What I'd do: for PI02, score the text in parts (for example, each paragraph) and use the most AI-like part, so one strange line can't hide the rest. EV05 I'd probably leave: after a heavy human edit, the text is arguably human writing.
- Why I stopped: scoring in parts changes how every text is scored, and short human texts with one AI-like paragraph could start getting the AI label. That's the opposite of what my design protects.

**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->

I'd keep making the AI label hard to reach, so fewer honest writers get accused, even though more AI text gets through as unsure. The people who pay for it are teachers and site owners, who get fewer confident answers and have to judge more unsure cases themselves, instead of writers like me who wrote every word in their second language.

<!-- ═══════════════════════ EXTENSION ═══════════════════════ -->

---

## What This Extends

**The system:** Provenance Guard (Unit 7-8).

**What was already there:**  A writer sends text to `/submit`, two signals score it (GPT-2 predictability and writing style), the combined score becomes one of three labels (human, unsure, AI), every decision goes to an audit log, and a wrongly labelled writer can appeal through `/appeal`.
-the two signals
-the combining rule
-the labels
-the appeal path, rate limiting
-the input checks added in unit 8. 

**What's new: what happens when the service's own parts fail** (extension B, "Harden against failure"):

| New | What it does |
|---|---|
| Fault switch (`AI201_FAULT`) | makes GPT-2 fail, GPT-2 slow, or the audit log unwritable on purpose, so each failure can be tested on demand |
| JSON for every error | a catch-all error handler: an unexpected crash returns a JSON 500 instead of an HTML debug page, and is logged. Unknown URLs and wrong methods are JSON too |
| Degraded mode | when GPT-2 fails, the writer still gets an answer: always "unsure", with a label saying the text couldn't be fully checked. Logged as degraded, with the reason |
| Time limit on GPT-2 | after 10 seconds, the service stops waiting and answers in degraded mode (reason `timeout`). GPT-2 now loads when the server starts |
| Log failure → 503 | if the decision can't be saved, the service refuses with a 503 and gives no content ID, because an unsaved decision can't be appealed |
| Structured logging | every log entry now also has `duration_ms` and `text_chars`, and 404/405 answers leave a record (see Instrumentation) |
| Cost measurement | `measure_cost.py`: one submission costs 0.52 s of compute on my laptop (see What It Costs) |
| Checks I can rerun | `check_logging.py` (every kind of failure leaves a record) and `run_capstone.py` (the five capstone criteria, three trials) |
| Run path | `RUNNING.md`: local, with logs, tested by cloning my own repo. The fixes for what failed are written in |
| Fixes from feedback | `/appeal` now rejects a `creator_id` that isn't a string (the RQ06 bug, found in its sibling), `RATE_LIMITING_ENABLED` is a real boolean, and "too short" has its own error type, so no other error can be mistaken for it |

**What didn't change:** how text is judged. The signals, the combining rule, the thresholds and the labels are the same as in unit 8, and my own texts get exactly the same scores. The judgment problems (non-English text, the criterion 2 gap, PI02 and EV05) are still in "What's Still Broken".

---

## The Shape

**B: Harden against failure.** My service works when everything goes right, but it has never been tested when one of its own parts fails. If GPT-2 can't load or throws an error, every submission crashes with a 500 and an HTML debug page. If the detector is slow, the writer just waits. If the audit log can't be written, the decision is lost after all the scoring work is done. And `/appeal` still crashes on a JSON array body, the same bug RQ07 found in `/submit`. I'm adding failure handling for these cases: a JSON error instead of a crash for anything unexpected, a time limit on the detector, a clear answer when the log can't be written, and a "degraded mode" for when the model signal fails. In degraded mode the service always answers "unsure", with a label saying the text couldn't be fully checked right now, and logs the decision as degraded. I chose this over scoring with the style signal alone: my tests showed the style signal is the weaker one and easy to fool (the AI ramen review scored 0.35 on it, right on the human line), so on its own it could clear AI text as human. "Unsure" never accuses a writer and never claims something the service couldn't check. To prove each case works, I'll add a setting that makes the failure happen on purpose, and every failure will leave an entry in the audit log.

**Out of scope:**
- I'm not fixing how the signals judge text: non-English writing, the criterion 2 gap and the PI02/EV05 evasions stay in "What's Still Broken". Those are judgment problems, not failures.
- I'm not adding retries. My only dependency is GPT-2 running on the same machine, and retrying a local model that failed the same way will just fail again.
- I'm not building the appeal review step (`/review`, `/status`). It's a new feature, not failure handling.

**Size check:** four pieces, each small: (1) a JSON error handler for unexpected errors plus the `/appeal` fix, (2) degraded mode when the detector fails, (3) a time limit on the detector, (4) handling a log write failure, plus a setting to trigger each one. That should fit in about ninety minutes. If it doesn't, the time limit is the first thing I'd cut.

**Build steps** (details in `ABOUT/EXTENSION_PLAN.md`):
0. A switch that causes failures on purpose
1. Never an HTML crash page; fix `/appeal`
2. Degraded mode when GPT-2 fails
3. A time limit on GPT-2
4. When the audit log can't be written
5. Instrument and deploy (later milestone)

---

## Instrumentation

**Where:** `logs/audit.jsonl`, one JSON object per line, written by `audit.py`. It can be read back with `audit.read_entries()`, through the service with `GET /log?limit=N`, or by opening the file. Nothing is recorded with `print()`.

**Every run writes a record.** Four kinds of entry, each with named fields:

| Entry | When | Fields |
|---|---|---|
| decision (`status: decided`) | every scored submission | timestamp, content_id, creator_id, guess, model_score, style_score, combined_score, label, status, duration_ms, text_chars; plus degraded, degraded_reason, error_type when the model failed or timed out |
| appeal (`event: appeal`) | every accepted appeal | timestamp, content_id, creator_id, status, reasoning, duration_ms |
| rejection (`event: rejected`) | every refused request: bad input (400), unknown URL (404), wrong method (405), rate limit (429) | timestamp, creator_id, reason, route, duration_ms, text_chars; http_status and method for 404/405; limit for 429 |
| error (`event: error`) | every unexpected crash (500) | timestamp, route, error_type, detail, duration_ms, text_chars |

How the requirement's fields map to mine:
- **timestamp:** `timestamp`, UTC, on every entry.
- **input:** `text_chars`, the length of the submitted text, plus `creator_id`. The text itself is never logged, on purpose: that way nothing a caller sends can be written into my log (PI05 in the attack run).
- **output:** `guess`, `label`, the three scores and the `content_id` the writer received. For a refused request, `reason` (the error code they got).
- **duration:** `duration_ms`, from the moment the request arrives until it is logged. The clock starts before the rate limiter, so 429s are timed too.
- **specific to my system:** both signal scores separately (so a wrong label can be traced to the signal that caused it), `degraded` and `degraded_reason` (whether the answer was a full check), `error_type`, and `status`, which shows where an item is in its life (decided → under_review).

### Log entries from a real run

Twelve consecutive entries from `logs/audit.jsonl`, copied as written. I started the real server (`python app.py`) and sent requests over HTTP: six submissions (three of my own texts, two AI texts, the forum post), one appeal, three bad inputs and an unknown URL. Then I restarted the server with `AI201_FAULT=model_slow` (GPT-2 takes 30 seconds) and sent one more submission.

Six decisions, one per label group (my texts got unsure, the AI essays got AI, the forum post got human):

```json
{"timestamp": "2026-11-18T00:14:12+00:00", "content_id": "c_c7ecfae9ecf2", "creator_id": "instr_1", "guess": "unsure", "model_score": 0.8288, "style_score": 0.5322, "combined_score": 0.5322, "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.", "status": "decided", "duration_ms": 728.4, "text_chars": 430}
{"timestamp": "2026-11-18T00:14:12+00:00", "content_id": "c_a1b7c58a9149", "creator_id": "instr_2", "guess": "unsure", "model_score": 0.5971, "style_score": 0.3114, "combined_score": 0.4542, "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.", "status": "decided", "duration_ms": 366.9, "text_chars": 422}
{"timestamp": "2026-11-18T00:14:13+00:00", "content_id": "c_cd85d156b83a", "creator_id": "instr_3", "guess": "unsure", "model_score": 0.7457, "style_score": 0.482, "combined_score": 0.6139, "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.", "status": "decided", "duration_ms": 429.9, "text_chars": 567}
{"timestamp": "2026-11-18T00:14:13+00:00", "content_id": "c_c2c2cb39781a", "creator_id": "instr_4", "guess": "ai", "model_score": 0.7969, "style_score": 0.7561, "combined_score": 0.7561, "label": "This text has patterns we often see in AI-generated writing. This is a guess, not proof, and we can be wrong. If you wrote it yourself, you can appeal using your content ID and a person will review it.", "status": "decided", "duration_ms": 509.8, "text_chars": 790}
{"timestamp": "2026-11-18T00:14:14+00:00", "content_id": "c_6ab77a24acfe", "creator_id": "instr_5", "guess": "ai", "model_score": 0.7508, "style_score": 0.6857, "combined_score": 0.6857, "label": "This text has patterns we often see in AI-generated writing. This is a guess, not proof, and we can be wrong. If you wrote it yourself, you can appeal using your content ID and a person will review it.", "status": "decided", "duration_ms": 510.8, "text_chars": 761}
{"timestamp": "2026-11-18T00:14:14+00:00", "content_id": "c_efa0ae5163f1", "creator_id": "instr_6", "guess": "human", "model_score": 0.3198, "style_score": 0.1324, "combined_score": 0.2261, "label": "We think this was probably written by a person.", "status": "decided", "duration_ms": 879.3, "text_chars": 919}
```

An appeal on the first one:

```json
{"timestamp": "2026-11-18T00:14:15+00:00", "content_id": "c_c7ecfae9ecf2", "creator_id": "instr_1", "event": "appeal", "status": "under_review", "reasoning": "I wrote this myself.", "duration_ms": 28.4}
```

**Failed runs.** Four rejected inputs (empty text, 25,000 characters, a two-letter text, an unknown URL) and one timeout:

```json
{"timestamp": "2026-11-18T00:14:15+00:00", "creator_id": "instr_bad", "event": "rejected", "status": "rejected", "reason": "bad_request", "route": "/submit", "duration_ms": 1.3, "text_chars": 3}
{"timestamp": "2026-11-18T00:14:15+00:00", "creator_id": "instr_bad", "event": "rejected", "status": "rejected", "reason": "text_too_long", "route": "/submit", "duration_ms": 1.0, "text_chars": 25000}
{"timestamp": "2026-11-18T00:14:15+00:00", "creator_id": "instr_bad", "event": "rejected", "status": "rejected", "reason": "text_too_short", "route": "/submit", "duration_ms": 1.8, "text_chars": 2}
{"timestamp": "2026-11-18T00:14:15+00:00", "creator_id": "unknown", "event": "rejected", "status": "rejected", "reason": "not_found", "route": "/nope", "method": "GET", "http_status": 404, "duration_ms": 0.3}
{"timestamp": "2026-11-18T00:15:01+00:00", "content_id": "c_7bc7a590495b", "creator_id": "instr_slow", "guess": "unsure", "model_score": null, "style_score": 0.5322, "combined_score": null, "label": "We couldn't fully check this text right now, so we can't say whether it was written by a person or with AI help. This is not an accusation. Please submit it again later for a full check.", "status": "decided", "degraded": true, "degraded_reason": "timeout", "error_type": "TimeoutError", "duration_ms": 10020.5, "text_chars": 430}
```

What the entries show:
- The timeout is visible directly in `duration_ms`: 10,020 ms against 370–880 ms for a normal check. The writer still got an answer (degraded "unsure", and the client waited 11.1 s in total) and a content_id they can appeal with. The server terminal printed `ERROR in app: Detector took longer than 10s, answering in degraded mode`.
- Rejections take 1–2 ms: they are refused before GPT-2 runs, so a bad input costs almost nothing.
- `text_chars` explains each rejection without storing the text: 3 characters of whitespace, 25,000 characters (over the 20,000 limit), 2 characters (too short).
- The scores are exactly the same as in unit 8 (0.5322, 0.4542, 0.6139, 0.7561, 0.2261), so adding the new fields changed nothing about how text is judged.

**Failures leave a record too.** I tested every kind with `check_logging.py` (output in `results/logging_check_2026-11-18.md`). It runs the real app against a temporary log and causes each failure on purpose:

| Case | Status | Log entry |
|---|---|---|
| normal submission | 200 | decision |
| appeal | 200 | appeal |
| empty text, too short, JSON array body | 400 | rejected, with the reason |
| unknown URL / wrong method | 404 / 405 | rejected, with `http_status` |
| one over the rate limit | 429 | rejected, `rate_limited` |
| GPT-2 fails | 200, degraded "unsure" | decision with `degraded_reason: model_error`, `error_type: RuntimeError` |
| unexpected crash | 500 | error, with `error_type` |
| the log itself can't be written | 503 | **none, by necessity**: reported on the server terminal instead |

Three entries from that run, copied from its output: a degraded decision, a crash and a rate limit:

```json
{"timestamp": "2026-11-18T00:09:39+00:00", "content_id": "c_3be57816dfb5", "creator_id": "chk_model", "guess": "unsure", "model_score": null, "style_score": 0.5, "combined_score": null, "label": "We couldn't fully check this text right now, so we can't say whether it was written by a person or with AI help. This is not an accusation. Please submit it again later for a full check.", "status": "decided", "degraded": true, "degraded_reason": "model_error", "error_type": "RuntimeError", "duration_ms": 6.3, "text_chars": 153}
{"timestamp": "2026-11-18T00:09:39+00:00", "event": "error", "status": "error", "route": "/submit", "error_type": "RuntimeError", "detail": "simulated bug", "duration_ms": 160.3, "text_chars": 153}
{"timestamp": "2026-11-18T00:09:39+00:00", "creator_id": "chk_flood", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute", "duration_ms": 1.2, "text_chars": 153}
```

**What's still not in the log:**
- Bad appeals (400, 404 for an unknown content_id) are deliberately not logged, as criterion 4 requires.
- When the log can't be written, the failure can only go to the server terminal. That's why the service refuses with a 503 instead of giving an answer nobody can check later.
- Entries written before 2026-11-18 don't have `duration_ms` and `text_chars`, because the fields were added then.

(The test text in the check is only two sentences, so the style signal returns 0.5 and it gets the AI label. That's the known short-text problem, not something the logging changed.)

---

## What It Costs

**What the real cost is:** seconds of compute on my own laptop. There is no API, so there's no money spent per run and no tokens: GPT-2 runs locally. What a submission uses up is CPU time while GPT-2 reads the text.

**The number:** one submission takes **0.52 seconds** (average of 10 runs, wall-clock time), and it keeps the processor busy for **1.85 seconds of CPU time** in that half second. CPU time is higher than wall time because torch spreads the work over 4 processor cores at once.

| | Wall time | CPU time |
|---|---|---|
| Average of 10 runs | 520 ms | 1,855 ms |
| Median | 482 ms | |
| Fastest / slowest | 400 ms / 1,004 ms | |
| One-time model load, at server start | 13.8 s | |

The first run was the slowest (1.0 s): torch does some setup on its first real calculation. Runs 2–10 took 0.40–0.54 s.

**How I measured it:** `measure_cost.py`, output saved in `results/cost_2026-11-18.md`.
- It runs my real Flask app in-process (Flask's test client), so each run goes through the whole `/submit` route: input checks, GPT-2, the style signal, the combining rule, the label and the audit log write. Only the network trip is left out, which on my own machine is a few milliseconds.
- The same text every time: the 87-word coffee shop text from my Sample Run, a typical short submission.
- GPT-2 is loaded once before timing, like `python app.py` does at startup, so the 13.8-second load is counted separately instead of landing on run 1.
- Per run, `time.perf_counter()` for wall time and `time.process_time()` for CPU time, before and after the request.
- The audit log goes to a temporary file, so my real log isn't filled with test entries, and each run uses its own creator_id so the rate limit doesn't interfere.
- Machine: my laptop, Intel Core 8th–10th generation (8 logical CPUs), 15.8 GB memory, Python 3.13, torch 2.15 (CPU only).

**The same number in the audit log:** every log entry now has `duration_ms` (how long the request took) and `text_chars` (how long the text was, without storing the text). So the cost of every real run can be read back from `logs/audit.jsonl`, not only from this test.

**What it means in practice:**
- **A hundred runs a day:** about 52 seconds of wall time (100 × 0.52 s), keeping the processor busy for about 3 minutes of CPU time (100 × 1.85 s), plus one 13.8-second model load when the server starts. API spend is $0, because nothing is hosted, and 3 CPU-minutes of electricity on a laptop is negligible. My rate limit allows 50 a day per writer, so 100 a day means at least two writers; the cost depends on the total number of submissions, not on who sends them.
- One writer at the daily limit (50 submissions) costs about 26 seconds of compute a day.
- The detector only reads the first 400 tokens of a text, so a long text doesn't cost much more than a short one. I measured only the 87-word text, so I'm not claiming a number for the longest allowed text.
- A run that times out costs much more: the writer waits the full 10 seconds, and GPT-2 keeps working in the background after that. In a test where the model wasn't loaded in advance, the first submission timed out and was logged with `duration_ms: 10057.7`.

---

## Extension Run Log — Before

Three separate runs of `run_capstone.py --trials 1` (`run_capstone.py::main`). Each run started a fresh process with a fresh audit log and its own creator_ids. Every request goes through the real routes, `app.py::submit` and `app.py::appeal`, with Flask's test client, and each fault is switched with `config.FAULT`. Saved output: `results/capstone_2026-11-21_0440_run1.md`, `results/capstone_2026-11-21_0443_run2.md`, `results/capstone_2026-11-21_0446_run3.md`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Model failure gives degraded "unsure", too-short text still a 400 | 11 of 11 | 10/11 | 10/11 | 10/11 | MISSED |
| 2. Slow model answers within 12 s as degraded "unsure" | 10 of 10 | 10/10 | 10/10 | 10/10 | MET |
| 3. Log failure returns a JSON 503 with no content ID | 10 of 10 | 10/10 | 10/10 | 10/10 | MET |
| 4. Every error is JSON, never an HTML page | 72 of 72 | 72/72 | 72/72 | 72/72 | MET |
| 5. Scores and labels unchanged from unit 8 | 10 of 10 | 10/10 | 10/10 | 10/10 | MET |

Criterion 1 counts 11 checks per run: the 10 submissions (all passed) and the two-letter text, which got a 200 instead of a 400.

**Real output from run 1** (`results/capstone_2026-11-21_0440_run1.md`).

**Criterion 1**, produced by `run_capstone.py::c1_model_failure` with `config.FAULT = "model_error"`. The response from `app.py::submit` (HTTP 200) for submission 1, and its log entry written by `audit.py::log_decision`:

```json
{"confidence": null, "content_id": "c_5114e3679cf1", "creator_id": "cap1_c1_1", "degraded": true, "degraded_reason": "model_error", "guess": "unsure", "label": "We couldn't fully check this text right now, so we can't say whether it was written by a person or with AI help. This is not an accusation. Please submit it again later for a full check.", "model_score": null, "style_score": 0.5322}
```

```json
{"timestamp": "2026-11-20T21:38:52+00:00", "content_id": "c_5114e3679cf1", "creator_id": "cap1_c1_1", "guess": "unsure", "model_score": null, "style_score": 0.5322, "combined_score": null, "label": "We couldn't fully check this text right now, so we can't say whether it was written by a person or with AI help. This is not an accusation. Please submit it again later for a full check.", "status": "decided", "degraded": true, "degraded_reason": "model_error", "error_type": "RuntimeError", "duration_ms": 10.6, "text_chars": 430}
```

The two-letter text `"hi"` under the same fault (HTTP 200):

```json
{"confidence": null, "content_id": "c_de2c5078e0d8", "creator_id": "cap1_c1_short", "degraded": true, "degraded_reason": "model_error", "guess": "unsure", "label": "We couldn't fully check this text right now, so we can't say whether it was written by a person or with AI help. This is not an accusation. Please submit it again later for a full check.", "model_score": null, "style_score": 0.5}
```

**Criterion 2**, produced by `run_capstone.py::c2_slow_model` with `config.FAULT = "model_slow"`. Submission 1 answered after 10.02 s (HTTP 200); the response from `app.py::submit` and the log entry from `audit.py::log_decision`:

```json
{"confidence": null, "content_id": "c_fae4a868e4e5", "creator_id": "cap1_c2_1", "degraded": true, "degraded_reason": "timeout", "guess": "unsure", "label": "We couldn't fully check this text right now, so we can't say whether it was written by a person or with AI help. This is not an accusation. Please submit it again later for a full check.", "model_score": null, "style_score": 0.5322}
```

```json
{"timestamp": "2026-11-20T21:39:24+00:00", "content_id": "c_fae4a868e4e5", "creator_id": "cap1_c2_1", "guess": "unsure", "model_score": null, "style_score": 0.5322, "combined_score": null, "label": "We couldn't fully check this text right now, so we can't say whether it was written by a person or with AI help. This is not an accusation. Please submit it again later for a full check.", "status": "decided", "degraded": true, "degraded_reason": "timeout", "error_type": "TimeoutError", "duration_ms": 10011.5, "text_chars": 430}
```

**Criterion 3**, produced by `run_capstone.py::c3_log_failure` with `config.FAULT = "log_error"`. The response from `app.py::submit` (HTTP 503) for submission 1, and the console message written by `app.py::_log_unavailable` (no log entry, because the log is what failed):

```json
{"error": "service_unavailable", "message": "We couldn't save this result, so we can't give you one right now. Please try again in a few minutes."}
```

```
ERROR in app: Could not write a decision to the audit log
```

**Criterion 4**, produced by `run_capstone.py::c4_no_html`. 72 requests: the attack set, 7 rapid submissions from one creator, bad appeals, an unknown URL and wrong methods. 0 responses weren't JSON and 0 were a 500. A selection of the responses, from `app.py::submit`, `app.py::appeal`, `app.py::rate_limited` and `app.py::handle_any_error`:

```json
{"request": "attack MF02", "status": 400, "json": true, "response": {"error": "text_too_short", "message": "Text is too short to check. Please send at least a few sentences."}}
{"request": "attack RQ07", "status": 400, "json": true, "response": {"error": "bad_request", "message": "Send a JSON object, like {\"text\": \"...\"}."}}
{"request": "flood 6", "status": 429, "json": true, "response": {"error": "rate_limited", "limit": "5 per 1 minute", "message": "Too many submissions. Try again shortly."}}
{"request": "/appeal JSON array", "status": 400, "json": true, "response": {"error": "bad_request", "message": "Send a JSON object, like {\"content_id\": \"...\", \"reasoning\": \"...\"}."}}
{"request": "/appeal creator_id object", "status": 400, "json": true, "response": {"error": "bad_request", "message": "\"creator_id\" must be a non-empty string."}}
{"request": "/appeal unknown content_id", "status": 404, "json": true, "response": {"error": "not_found", "message": "We couldn't find a submission with content ID c_000000000000. Please check the ID from your original result."}}
{"request": "GET /nope", "status": 404, "json": true, "response": {"error": "not_found", "message": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."}}
{"request": "GET /submit", "status": 405, "json": true, "response": {"error": "method_not_allowed", "message": "The method is not allowed for the requested URL."}}
{"request": "PUT /submit", "status": 405, "json": true, "response": {"error": "method_not_allowed", "message": "The method is not allowed for the requested URL."}}
```

**Criterion 5**, produced by `run_capstone.py::c5_nothing_changes` with no fault. The response from `app.py::submit` for text 1 and its log entry from `audit.py::log_decision`. Unit 8 gave this text guess "unsure", confidence 0.5322, model 0.8288, style 0.5322 (`results/run_2026-11-15_1427_after.md`):

```json
{"confidence": 0.5322, "content_id": "c_e6344519c940", "creator_id": "cap1_c5_1", "degraded": false, "guess": "unsure", "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.", "model_score": 0.8288, "style_score": 0.5322}
```

```json
{"timestamp": "2026-11-20T21:38:47+00:00", "content_id": "c_e6344519c940", "creator_id": "cap1_c5_1", "guess": "unsure", "model_score": 0.8288, "style_score": 0.5322, "combined_score": 0.5322, "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.", "status": "decided", "duration_ms": 828.3, "text_chars": 430}
```

### Why criterion 1 is missed

**What happened:** with GPT-2 broken, all 10 real submissions got the right degraded "unsure" answer, in all three runs. The one check that failed is the two-letter text `"hi"`: it got a 200 degraded answer instead of the 400 "too short" my criterion promises.

**Stage and mechanism:** the route, through signal one. The only "too short" check lives inside the detector: `detector.perplexity` asks GPT-2's tokenizer to split the text into tokens and raises `TextTooShort` if there are fewer than 3. But the model failure happens first, at the top of `detector.model_signal`, before `perplexity` is ever called. So when the model is broken, nothing checks the length, and every text, even `"hi"`, falls through to degraded mode.

This isn't only a quirk of my fault switch. In a real failure, for example GPT-2 not loading, the tokenizer comes from the same download and can be missing too, so the length still couldn't be checked. My design put the input check inside the part that can fail.

**Who it affects:** nobody is accused. `"hi"` gets "unsure" and "please submit it again later" instead of "too short". But it breaks two promises: the criterion's 400, and the honesty of the label. "Submit it again later" is wrong advice for a text that will be refused as too short once the model works. It also costs a log entry and a content ID for a text that could never be scored.

### Improvement

**What I'm changing:** I'm moving the "too short" check out of the part that can fail and into the route. `app.py::submit` gets one more input check, next to the ones for empty and too-long text: if the text has fewer than 3 words, it returns the 400 `text_too_short` right away, before GPT-2 is called. This check doesn't need the model or its tokenizer, so it works even when GPT-2 is broken.

**Why 3 words:** the detector refuses texts with fewer than 3 GPT-2 tokens. A word is always at least one token, so any text with 3 or more words has at least 3 tokens. The route check therefore refuses every text the detector would refuse. `TextTooShort` in the detector stays as a backstop.

**What I expect to change:**
- Criterion 1: `"hi"` gets a 400 whether the model works or not, so the target becomes 11 of 11.
- A text of one or two very long words is now refused instead of scored. MF05 (one very long word, labelled AI in unit 8) should move from BROKE to HELD. One word isn't writing, so refusing it is the honest answer.
- Criterion 5 (scores unchanged): my own texts are all far longer than 3 words, so their scores shouldn't move.

**What I'm not doing:** rewording the criterion to "too-short text gets a 400 when no fault is on". That would make it pass without fixing anything, and the course rules say a missed target stays and gets a fix attempted.

**How I'll check it (After):** the same three separate runs of `run_capstone.py --trials 1` and the same table. I'll also run the attack set to confirm that MF05 changes and that no other attack gets worse.

---

## Extension Run Log — After

The same three separate runs of `run_capstone.py --trials 1` (`run_capstone.py::main`), after the improvement: the "too short" check moved into `app.py::submit`, before GPT-2 runs (`MIN_WORDS = 3` in `config.py`). Everything else is the same as Before: a fresh process and audit log per run, its own creator_ids, the real routes through Flask's test client, and faults switched with `config.FAULT`. Saved output: `results/capstone_2026-11-21_1050_after_run1.md`, `results/capstone_2026-11-21_1053_after_run2.md`, `results/capstone_2026-11-21_1055_after_run3.md`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Model failure gives degraded "unsure", too-short text still a 400 | 11 of 11 | 11/11 | 11/11 | 11/11 | MET |
| 2. Slow model answers within 12 s as degraded "unsure" | 10 of 10 | 10/10 | 10/10 | 10/10 | MET |
| 3. Log failure returns a JSON 503 with no content ID | 10 of 10 | 10/10 | 10/10 | 10/10 | MET |
| 4. Every error is JSON, never an HTML page | 72 of 72 | 72/72 | 72/72 | 72/72 | MET |
| 5. Scores and labels unchanged from unit 8 | 10 of 10 | 10/10 | 10/10 | 10/10 | MET |

**Before and After**

| Criterion | Before | After |
|---|---|---|
| 1. Model failure | MISSED (10/11) | MET (11/11) |
| 2. Slow model | MET | MET |
| 3. Log failure | MET | MET |
| 4. No HTML errors | MET | MET |
| 5. Scores unchanged | MET | MET |

**The attack set after the improvement.** `run_attacks.py::main` against the real server (`python app.py`, no fault), all 56 attacks: `results/attack_run_2026-11-21_1056_after_min_words.md`. Compared with the last unit 8 run (`results/attack_run_2026-11-15_1427_after.md`) on status, guess and score, exactly two attacks changed, both from BROKE to HELD under my unit 8 rules (malformed text that gets a 200 is BROKE, a clean 400 is HELD):

| Attack | Unit 8 | After |
|---|---|---|
| MF05, a very long single word | 200, ai, 0.749 (BROKE) | 400 `text_too_short` (HELD) |
| MF06, emoji only | 200, ai, 0.749 (BROKE) | 400 `text_too_short` (HELD) |

The other 54 attacks got exactly the same status, guess and score as in unit 8, so no attack got worse. BROKE goes from 7 to 5: EV05, PI02, MF03, MF04 and MF07 are still in "What's Still Broken". RQ10 and RQ11 were rate-limited again in the full run, as in unit 8; re-run alone in unit 8, both got a clean 400.

The responses to the two changed attacks from the new check in `app.py::submit`, as recorded by `run_capstone.py::c4_no_html` in After run 1:

```json
{"request": "attack MF05", "status": 400, "json": true, "response": {"error": "text_too_short", "message": "Text is too short to check. Please send at least a few sentences."}}
{"request": "attack MF06", "status": 400, "json": true, "response": {"error": "text_too_short", "message": "Text is too short to check. Please send at least a few sentences."}}
```

**Real output from After run 1** (`results/capstone_2026-11-21_1050_after_run1.md`).

**Criterion 1**, produced by `run_capstone.py::c1_model_failure` with `config.FAULT = "model_error"`. The response from `app.py::submit` (HTTP 200) for submission 1, and its log entry written by `audit.py::log_decision`:

```json
{"confidence": null, "content_id": "c_de42e9028878", "creator_id": "cap1_c1_1", "degraded": true, "degraded_reason": "model_error", "guess": "unsure", "label": "We couldn't fully check this text right now, so we can't say whether it was written by a person or with AI help. This is not an accusation. Please submit it again later for a full check.", "model_score": null, "style_score": 0.5322}
```

```json
{"timestamp": "2026-11-21T03:48:12+00:00", "content_id": "c_de42e9028878", "creator_id": "cap1_c1_1", "guess": "unsure", "model_score": null, "style_score": 0.5322, "combined_score": null, "label": "We couldn't fully check this text right now, so we can't say whether it was written by a person or with AI help. This is not an accusation. Please submit it again later for a full check.", "status": "decided", "degraded": true, "degraded_reason": "model_error", "error_type": "RuntimeError", "duration_ms": 37.1, "text_chars": 430}
```

The two-letter text `"hi"` under the same fault, now refused by the new check in `app.py::submit` (HTTP 400):

```json
{"error": "text_too_short", "message": "Text is too short to check. Please send at least a few sentences."}
```

**Criterion 2**, produced by `run_capstone.py::c2_slow_model` with `config.FAULT = "model_slow"`. Submission 1 answered after 10.02 s (HTTP 200); the response from `app.py::submit` and the log entry from `audit.py::log_decision`:

```json
{"confidence": null, "content_id": "c_eb8735b7552a", "creator_id": "cap1_c2_1", "degraded": true, "degraded_reason": "timeout", "guess": "unsure", "label": "We couldn't fully check this text right now, so we can't say whether it was written by a person or with AI help. This is not an accusation. Please submit it again later for a full check.", "model_score": null, "style_score": 0.5322}
```

```json
{"timestamp": "2026-11-21T03:48:44+00:00", "content_id": "c_eb8735b7552a", "creator_id": "cap1_c2_1", "guess": "unsure", "model_score": null, "style_score": 0.5322, "combined_score": null, "label": "We couldn't fully check this text right now, so we can't say whether it was written by a person or with AI help. This is not an accusation. Please submit it again later for a full check.", "status": "decided", "degraded": true, "degraded_reason": "timeout", "error_type": "TimeoutError", "duration_ms": 10011.2, "text_chars": 430}
```

**Criterion 3**, produced by `run_capstone.py::c3_log_failure` with `config.FAULT = "log_error"`. The response from `app.py::submit` (HTTP 503) for submission 1, and the console message written by `app.py::_log_unavailable` (no log entry, because the log is what failed):

```json
{"error": "service_unavailable", "message": "We couldn't save this result, so we can't give you one right now. Please try again in a few minutes."}
```

```
ERROR in app: Could not write a decision to the audit log
```

**Criterion 4**, produced by `run_capstone.py::c4_no_html`. 72 requests: the attack set, 7 rapid submissions from one creator, bad appeals, an unknown URL and wrong methods. 0 responses weren't JSON and 0 were a 500. A selection of the responses, from `app.py::submit`, `app.py::appeal`, `app.py::rate_limited` and `app.py::handle_any_error`:

```json
{"request": "attack MF02", "status": 400, "json": true, "response": {"error": "text_too_short", "message": "Text is too short to check. Please send at least a few sentences."}}
{"request": "attack MF05", "status": 400, "json": true, "response": {"error": "text_too_short", "message": "Text is too short to check. Please send at least a few sentences."}}
{"request": "attack RQ07", "status": 400, "json": true, "response": {"error": "bad_request", "message": "Send a JSON object, like {\"text\": \"...\"}."}}
{"request": "flood 6", "status": 429, "json": true, "response": {"error": "rate_limited", "limit": "5 per 1 minute", "message": "Too many submissions. Try again shortly."}}
{"request": "/appeal JSON array", "status": 400, "json": true, "response": {"error": "bad_request", "message": "Send a JSON object, like {\"content_id\": \"...\", \"reasoning\": \"...\"}."}}
{"request": "/appeal creator_id object", "status": 400, "json": true, "response": {"error": "bad_request", "message": "\"creator_id\" must be a non-empty string."}}
{"request": "/appeal unknown content_id", "status": 404, "json": true, "response": {"error": "not_found", "message": "We couldn't find a submission with content ID c_000000000000. Please check the ID from your original result."}}
{"request": "GET /nope", "status": 404, "json": true, "response": {"error": "not_found", "message": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."}}
{"request": "GET /submit", "status": 405, "json": true, "response": {"error": "method_not_allowed", "message": "The method is not allowed for the requested URL."}}
{"request": "PUT /submit", "status": 405, "json": true, "response": {"error": "method_not_allowed", "message": "The method is not allowed for the requested URL."}}
```

**Criterion 5**, produced by `run_capstone.py::c5_nothing_changes` with no fault. The response from `app.py::submit` for text 1 and its log entry from `audit.py::log_decision`. Unit 8 gave this text guess "unsure", confidence 0.5322, model 0.8288, style 0.5322 (`results/run_2026-11-15_1427_after.md`):

```json
{"confidence": 0.5322, "content_id": "c_9a99c978712c", "creator_id": "cap1_c5_1", "degraded": false, "guess": "unsure", "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.", "model_score": 0.8288, "style_score": 0.5322}
```

```json
{"timestamp": "2026-11-21T03:48:08+00:00", "content_id": "c_9a99c978712c", "creator_id": "cap1_c5_1", "guess": "unsure", "model_score": 0.8288, "style_score": 0.5322, "combined_score": 0.5322, "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.", "status": "decided", "duration_ms": 1677.5, "text_chars": 430}
```

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
