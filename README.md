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
- 400 with error "bad_request" if the body isn't JSON, or content_id or reasoning is missing, not a string, or empty.
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

**What I found when testing it:** I tested three texts: a formal AI essay, a casual restaurant review that I asked an AI to write so it sounds like a person, and a real forum post from 15 years ago.

| Measure | AI essay | AI pretending to be human | Real human (forum) |
|---|---|---|---|
| sentence length spread (higher = more human) | 0.26 | 0.73 | 0.51 |
| word variety (higher = more AI) | 0.92 | 0.89 | 0.80 |
| punctuation sameness (higher = more AI) | 0.50 | 0.33 | 0.00 |

The fake casual review fooled the sentence measure. It has uneven sentences and short fragments like "honestly?", so it scored *more* human than the real human. The attacker doesn't even need to edit the text by hand. Asking the AI to "sound casual" is enough, because the style is exactly what it copies. On the other two measures it landed between the AI essay and the real human, so the style signal will probably call it unsure, not AI.

Word variety worked the opposite way from what I expected. I thought AI would repeat words more, but both AI texts used a wider vocabulary than the human. So I count a higher value as more AI.

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
- Label thresholds: `HUMAN_THRESHOLD = 0.35`, `AI_THRESHOLD = 0.65`. Below 0.35 is human, above 0.65 is AI, in between is unsure.

I tested five texts:

| Text | Model | Style | Plain average | My rule | Label |
|---|---|---|---|---|---|
| Clearly AI (essay) | 0.80 | 0.76 | 0.78 | 0.76 | AI |
| Lightly-edited AI | 0.75 | 0.69 | 0.72 | 0.69 | AI |
| Plain human (my own writing) | 0.83 | 0.53 | 0.68 (AI ✗) | 0.53 | unsure |
| AI pretending to be human | 0.40 | 0.35 | 0.37 | 0.37 | unsure |
| Clearly human (forum post) | 0.32 | 0.13 | 0.22 | 0.22 | human |

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

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

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



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



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
