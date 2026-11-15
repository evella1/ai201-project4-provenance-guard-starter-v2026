# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-15 14:27
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **56**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `c_84374c9c7f1b` | unsure | 0.498 | HELD |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `c_f7505edfcb31` | unsure | 0.507 | HELD |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `c_698d59828aa5` | unsure | 0.565 | HELD |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `c_8ec6a84f9284` | unsure | 0.611 | HELD |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `c_e7dcabae8b48` | human | 0.304 | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `c_1e2970cae00f` | unsure | 0.474 | HELD |
| EV07 | evasion | signal two: padding with punctuation | 200 | `c_ea8388b4892d` | unsure | 0.543 | HELD |
| EV08 | evasion | signal one: text below the token window | 200 | `c_55e0177b892e` | unsure | 0.373 | HELD |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `c_7c6b21b8a291` | unsure | 0.555 | HELD |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `c_cda611990ce9` | ai | 0.714 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `c_a7e66758bcab` | unsure | 0.508 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | `c_3da29796f305` | unsure | 0.522 | HELD |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c_e39011ec74d0` | unsure | 0.592 | HELD |
| FP04 | false_positive | a student essay written to a rubric | 200 | `c_26780ccc235a` | unsure | 0.508 | HELD |
| FP05 | false_positive | technical documentation written by a person | 200 | `c_44ebfb29ae96` | unsure | 0.646 | HELD |
| FP06 | false_positive | a person imitating a formal template | 200 | `c_636e4fa166b4` | unsure | 0.586 | HELD |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `c_fa0cb612b8ab` | unsure | 0.552 | HELD |
| FP08 | false_positive | very short genuine human submission | 200 | `c_dd34938566a9` | unsure | 0.411 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `c_40e545a1a353` | unsure | 0.537 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `c_25de5989ade5` | human | 0.324 | BROKE |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `c_3c920e26e5ce` | unsure | 0.594 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `c_182872097773` | unsure | 0.423 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `c_978319d99de1` | unsure | 0.570 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `c_28333a2634a6` | unsure | 0.491 | HELD |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | `—` | — | — | HELD |
| MF03 | malformed | text is control characters | 200 | `c_9bc2216fa0fe` | human | 0.250 | BROKE |
| MF04 | malformed | text is only punctuation | 200 | `c_7b3905b81985` | human | 0.256 | BROKE |
| MF05 | malformed | text is a very long single word | 200 | `c_7132273ad392` | ai | 0.749 | BROKE |
| MF06 | malformed | text is emoji only | 200 | `c_8c0676c74654` | ai | 0.749 | BROKE |
| MF07 | malformed | text is right-to-left script | 200 | `c_2b457af66b9e` | ai | 0.703 | BROKE |
| MF08 | malformed | text is 60,000 characters | 400 | `—` | — | — | HELD |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — | HELD |
| RQ02 | malformed | no creator_id | 200 | `c_950fa3e2a3b0` | unsure | 0.370 | HELD |
| RQ03 | malformed | text is a number | 400 | `—` | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | `—` | — | — | HELD |
| RQ05 | malformed | text is null | 400 | `—` | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — | HELD |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | `—` | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — | UNTESTED |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — | UNTESTED |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_f81724fea76d` | human | 0.264 | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_4dfa07a53299` | human | 0.264 | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_b902b5a73a0a` | human | 0.264 | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_7471bdb5531c` | human | 0.264 | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_9279c2b0fa1e` | human | 0.264 | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "c_84374c9c7f1b",
  "creator_id": "attacker_EV01",
  "guess": "unsure",
  "confidence": 0.4984,
  "model_score": 0.1635,
  "style_score": 0.8333,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "c_f7505edfcb31",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.5074,
  "model_score": 0.5943,
  "style_score": 0.4206,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "c_698d59828aa5",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.5651,
  "model_score": 0.6662,
  "style_score": 0.4639,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "c_8ec6a84f9284",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.6114,
  "model_score": 0.6114,
  "style_score": 0.8333,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "c_e7dcabae8b48",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.3044,
  "model_score": 0.3212,
  "style_score": 0.2875,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "c_1e2970cae00f",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.4739,
  "model_score": 0.5727,
  "style_score": 0.3752,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "c_ea8388b4892d",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.5431,
  "model_score": 0.5862,
  "style_score": 0.5,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "c_55e0177b892e",
  "creator_id": "attacker_EV08",
  "guess": "unsure",
  "confidence": 0.3726,
  "model_score": 0.2452,
  "style_score": 0.5,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "c_7c6b21b8a291",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.5548,
  "model_score": 0.7042,
  "style_score": 0.5548,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "c_cda611990ce9",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.7144,
  "model_score": 0.9792,
  "style_score": 0.4495,
  "label": "This text has patterns we often see in AI-generated writing. This is a guess, not proof, and we can be wrong. If you wrote it yourself, you can appeal using your content ID and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "c_a7e66758bcab",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.5085,
  "model_score": 0.6175,
  "style_score": 0.3994,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "c_3da29796f305",
  "creator_id": "attacker_FP02",
  "guess": "unsure",
  "confidence": 0.5219,
  "model_score": 0.7387,
  "style_score": 0.5219,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "c_e39011ec74d0",
  "creator_id": "attacker_FP03",
  "guess": "unsure",
  "confidence": 0.5919,
  "model_score": 0.8051,
  "style_score": 0.5919,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "c_26780ccc235a",
  "creator_id": "attacker_FP04",
  "guess": "unsure",
  "confidence": 0.5079,
  "model_score": 0.8329,
  "style_score": 0.5079,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "c_44ebfb29ae96",
  "creator_id": "attacker_FP05",
  "guess": "unsure",
  "confidence": 0.646,
  "model_score": 0.8005,
  "style_score": 0.4915,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "c_636e4fa166b4",
  "creator_id": "attacker_FP06",
  "guess": "unsure",
  "confidence": 0.5855,
  "model_score": 0.8814,
  "style_score": 0.2896,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "c_fa0cb612b8ab",
  "creator_id": "attacker_FP07",
  "guess": "unsure",
  "confidence": 0.5519,
  "model_score": 0.8816,
  "style_score": 0.2222,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "c_dd34938566a9",
  "creator_id": "attacker_FP08",
  "guess": "unsure",
  "confidence": 0.4112,
  "model_score": 0.3223,
  "style_score": 0.5,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "c_40e545a1a353",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.5368,
  "model_score": 0.4625,
  "style_score": 0.6111,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "c_25de5989ade5",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.3244,
  "model_score": 0.2044,
  "style_score": 0.4444,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "c_3c920e26e5ce",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.5943,
  "model_score": 0.5943,
  "style_score": 0.6438,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "c_182872097773",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.4235,
  "model_score": 0.4998,
  "style_score": 0.3472,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "c_978319d99de1",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.57,
  "model_score": 0.6401,
  "style_score": 0.5,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "c_28333a2634a6",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.4908,
  "model_score": 0.5583,
  "style_score": 0.4233,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "c_9bc2216fa0fe",
  "creator_id": "attacker_MF03",
  "guess": "human",
  "confidence": 0.25,
  "model_score": 0.0,
  "style_score": 0.5,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "c_7b3905b81985",
  "creator_id": "attacker_MF04",
  "guess": "human",
  "confidence": 0.2556,
  "model_score": 0.0112,
  "style_score": 0.5,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "c_7132273ad392",
  "creator_id": "attacker_MF05",
  "guess": "ai",
  "confidence": 0.7488,
  "model_score": 0.9976,
  "style_score": 0.5,
  "label": "This text has patterns we often see in AI-generated writing. This is a guess, not proof, and we can be wrong. If you wrote it yourself, you can appeal using your content ID and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "c_8c0676c74654",
  "creator_id": "attacker_MF06",
  "guess": "ai",
  "confidence": 0.7485,
  "model_score": 0.9969,
  "style_score": 0.5,
  "label": "This text has patterns we often see in AI-generated writing. This is a guess, not proof, and we can be wrong. If you wrote it yourself, you can appeal using your content ID and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "c_2b457af66b9e",
  "creator_id": "attacker_MF07",
  "guess": "ai",
  "confidence": 0.7032,
  "model_score": 0.9064,
  "style_score": 0.5,
  "label": "This text has patterns we often see in AI-generated writing. This is a guess, not proof, and we can be wrong. If you wrote it yourself, you can appeal using your content ID and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 200,
  "content_id": "c_950fa3e2a3b0",
  "creator_id": null,
  "guess": "unsure",
  "confidence": 0.3698,
  "model_score": 0.2395,
  "style_score": 0.5,
  "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "c_f81724fea76d",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2643,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "c_4dfa07a53299",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2643,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "c_b902b5a73a0a",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2643,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "c_7471bdb5531c",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2643,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "c_9279c2b0fa1e",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2643,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
