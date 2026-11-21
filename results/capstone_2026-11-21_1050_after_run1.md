# Capstone criteria run: after_run1

- Produced by: `run_capstone.py` · 2026-11-21 10:50
- Real app in-process (Flask test client), faults switched with `config.FAULT`, temporary audit log
- 1 trial(s) · unit 8 baseline: `run_2026-11-15_1427_after.md`

| Criterion | Trial 1 | Verdict |
|---|---|---|
| 1. Model failure | pass: 10/10, too-short -> 400 | MET |
| 2. Slow model | pass: 10/10, slowest 10.0s | MET |
| 3. Log failure | pass: 10/10, console reports 10, new log lines 0 | MET |
| 4. No HTML errors | pass: 72/72 JSON, 0 x 500 | MET |
| 5. Nothing else changes | pass: 10/10 identical | MET |

## 1. Model failure

**Trial 1**

```json
{
 "submissions": [
  {
   "n": 1,
   "status": 200,
   "guess": "unsure",
   "degraded": true,
   "reason": "model_error",
   "model_score": null,
   "logged_degraded": true,
   "pass": true
  },
  {
   "n": 2,
   "status": 200,
   "guess": "unsure",
   "degraded": true,
   "reason": "model_error",
   "model_score": null,
   "logged_degraded": true,
   "pass": true
  },
  {
   "n": 3,
   "status": 200,
   "guess": "unsure",
   "degraded": true,
   "reason": "model_error",
   "model_score": null,
   "logged_degraded": true,
   "pass": true
  },
  {
   "n": 4,
   "status": 200,
   "guess": "unsure",
   "degraded": true,
   "reason": "model_error",
   "model_score": null,
   "logged_degraded": true,
   "pass": true
  },
  {
   "n": 5,
   "status": 200,
   "guess": "unsure",
   "degraded": true,
   "reason": "model_error",
   "model_score": null,
   "logged_degraded": true,
   "pass": true
  },
  {
   "n": 6,
   "status": 200,
   "guess": "unsure",
   "degraded": true,
   "reason": "model_error",
   "model_score": null,
   "logged_degraded": true,
   "pass": true
  },
  {
   "n": 7,
   "status": 200,
   "guess": "unsure",
   "degraded": true,
   "reason": "model_error",
   "model_score": null,
   "logged_degraded": true,
   "pass": true
  },
  {
   "n": 8,
   "status": 200,
   "guess": "unsure",
   "degraded": true,
   "reason": "model_error",
   "model_score": null,
   "logged_degraded": true,
   "pass": true
  },
  {
   "n": 9,
   "status": 200,
   "guess": "unsure",
   "degraded": true,
   "reason": "model_error",
   "model_score": null,
   "logged_degraded": true,
   "pass": true
  },
  {
   "n": 10,
   "status": 200,
   "guess": "unsure",
   "degraded": true,
   "reason": "model_error",
   "model_score": null,
   "logged_degraded": true,
   "pass": true
  }
 ],
 "too_short_under_fault": {
  "status": 400,
  "error": "text_too_short",
  "guess": null
 },
 "real_output": {
  "response_status": 200,
  "response": {
   "confidence": null,
   "content_id": "c_de42e9028878",
   "creator_id": "cap1_c1_1",
   "degraded": true,
   "degraded_reason": "model_error",
   "guess": "unsure",
   "label": "We couldn't fully check this text right now, so we can't say whether it was written by a person or with AI help. This is not an accusation. Please submit it again later for a full check.",
   "model_score": null,
   "style_score": 0.5322
  },
  "log_entry": {
   "timestamp": "2026-11-21T03:48:12+00:00",
   "content_id": "c_de42e9028878",
   "creator_id": "cap1_c1_1",
   "guess": "unsure",
   "model_score": null,
   "style_score": 0.5322,
   "combined_score": null,
   "label": "We couldn't fully check this text right now, so we can't say whether it was written by a person or with AI help. This is not an accusation. Please submit it again later for a full check.",
   "status": "decided",
   "degraded": true,
   "degraded_reason": "model_error",
   "error_type": "RuntimeError",
   "duration_ms": 37.1,
   "text_chars": 430
  },
  "too_short_status": 400,
  "too_short_response": {
   "error": "text_too_short",
   "message": "Text is too short to check. Please send at least a few sentences."
  }
 }
}
```

## 2. Slow model

**Trial 1**

```json
{
 "submissions": [
  {
   "n": 1,
   "seconds": 10.02,
   "status": 200,
   "guess": "unsure",
   "reason": "timeout",
   "pass": true
  },
  {
   "n": 2,
   "seconds": 10.01,
   "status": 200,
   "guess": "unsure",
   "reason": "timeout",
   "pass": true
  },
  {
   "n": 3,
   "seconds": 10.02,
   "status": 200,
   "guess": "unsure",
   "reason": "timeout",
   "pass": true
  },
  {
   "n": 4,
   "seconds": 10.02,
   "status": 200,
   "guess": "unsure",
   "reason": "timeout",
   "pass": true
  },
  {
   "n": 5,
   "seconds": 10.02,
   "status": 200,
   "guess": "unsure",
   "reason": "timeout",
   "pass": true
  },
  {
   "n": 6,
   "seconds": 10.02,
   "status": 200,
   "guess": "unsure",
   "reason": "timeout",
   "pass": true
  },
  {
   "n": 7,
   "seconds": 10.01,
   "status": 200,
   "guess": "unsure",
   "reason": "timeout",
   "pass": true
  },
  {
   "n": 8,
   "seconds": 10.02,
   "status": 200,
   "guess": "unsure",
   "reason": "timeout",
   "pass": true
  },
  {
   "n": 9,
   "seconds": 10.01,
   "status": 200,
   "guess": "unsure",
   "reason": "timeout",
   "pass": true
  },
  {
   "n": 10,
   "seconds": 10.01,
   "status": 200,
   "guess": "unsure",
   "reason": "timeout",
   "pass": true
  }
 ],
 "real_output": {
  "seconds": 10.02,
  "response_status": 200,
  "response": {
   "confidence": null,
   "content_id": "c_eb8735b7552a",
   "creator_id": "cap1_c2_1",
   "degraded": true,
   "degraded_reason": "timeout",
   "guess": "unsure",
   "label": "We couldn't fully check this text right now, so we can't say whether it was written by a person or with AI help. This is not an accusation. Please submit it again later for a full check.",
   "model_score": null,
   "style_score": 0.5322
  },
  "log_entry": {
   "timestamp": "2026-11-21T03:48:44+00:00",
   "content_id": "c_eb8735b7552a",
   "creator_id": "cap1_c2_1",
   "guess": "unsure",
   "model_score": null,
   "style_score": 0.5322,
   "combined_score": null,
   "label": "We couldn't fully check this text right now, so we can't say whether it was written by a person or with AI help. This is not an accusation. Please submit it again later for a full check.",
   "status": "decided",
   "degraded": true,
   "degraded_reason": "timeout",
   "error_type": "TimeoutError",
   "duration_ms": 10011.2,
   "text_chars": 430
  }
 }
}
```

## 3. Log failure

**Trial 1**

```json
{
 "submissions": [
  {
   "n": 1,
   "status": 503,
   "json": true,
   "content_id": null,
   "pass": true
  },
  {
   "n": 2,
   "status": 503,
   "json": true,
   "content_id": null,
   "pass": true
  },
  {
   "n": 3,
   "status": 503,
   "json": true,
   "content_id": null,
   "pass": true
  },
  {
   "n": 4,
   "status": 503,
   "json": true,
   "content_id": null,
   "pass": true
  },
  {
   "n": 5,
   "status": 503,
   "json": true,
   "content_id": null,
   "pass": true
  },
  {
   "n": 6,
   "status": 503,
   "json": true,
   "content_id": null,
   "pass": true
  },
  {
   "n": 7,
   "status": 503,
   "json": true,
   "content_id": null,
   "pass": true
  },
  {
   "n": 8,
   "status": 503,
   "json": true,
   "content_id": null,
   "pass": true
  },
  {
   "n": 9,
   "status": 503,
   "json": true,
   "content_id": null,
   "pass": true
  },
  {
   "n": 10,
   "status": 503,
   "json": true,
   "content_id": null,
   "pass": true
  }
 ],
 "console_reports": 10,
 "new_log_lines": 0,
 "real_output": {
  "response_status": 503,
  "response": {
   "error": "service_unavailable",
   "message": "We couldn't save this result, so we can't give you one right now. Please try again in a few minutes."
  },
  "console": [
   "Could not write a decision to the audit log"
  ]
 }
}
```

## 4. No HTML errors

**Trial 1**

```json
{
 "non_json": [],
 "requests": 72,
 "status_500": 0,
 "all_requests": [
  {
   "request": "attack EV01",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.4984,
    "content_id": "c_4aa2da39285f",
    "creator_id": "attacker_EV01_t1",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.1635,
    "style_score": 0.8333
   }
  },
  {
   "request": "attack EV02",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.5074,
    "content_id": "c_efd3a34989b3",
    "creator_id": "attacker_EV02_t1",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.5943,
    "style_score": 0.4206
   }
  },
  {
   "request": "attack EV03",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.5651,
    "content_id": "c_8c9b9303504f",
    "creator_id": "attacker_EV03_t1",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.6662,
    "style_score": 0.4639
   }
  },
  {
   "request": "attack EV04",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.6114,
    "content_id": "c_3525de01e03e",
    "creator_id": "attacker_EV04_t1",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.6114,
    "style_score": 0.8333
   }
  },
  {
   "request": "attack EV05",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.3044,
    "content_id": "c_10b400f7895b",
    "creator_id": "attacker_EV05_t1",
    "degraded": false,
    "guess": "human",
    "label": "We think this was probably written by a person.",
    "model_score": 0.3212,
    "style_score": 0.2875
   }
  },
  {
   "request": "attack EV06",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.4739,
    "content_id": "c_c7f64d58f818",
    "creator_id": "attacker_EV06_t1",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.5727,
    "style_score": 0.3752
   }
  },
  {
   "request": "attack EV07",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.5431,
    "content_id": "c_541a5b987421",
    "creator_id": "attacker_EV07_t1",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.5862,
    "style_score": 0.5
   }
  },
  {
   "request": "attack EV08",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.3726,
    "content_id": "c_99c908fd268b",
    "creator_id": "attacker_EV08_t1",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.2452,
    "style_score": 0.5
   }
  },
  {
   "request": "attack EV09",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.5548,
    "content_id": "c_73626794ffce",
    "creator_id": "attacker_EV09_t1",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.7042,
    "style_score": 0.5548
   }
  },
  {
   "request": "attack EV10",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.7144,
    "content_id": "c_055d93e08516",
    "creator_id": "attacker_EV10_t1",
    "degraded": false,
    "guess": "ai",
    "label": "This text has patterns we often see in AI-generated writing. This is a guess, not proof, and we can be wrong. If you wrote it yourself, you can appeal using your content ID and a person will review it.",
    "model_score": 0.9792,
    "style_score": 0.4495
   }
  },
  {
   "request": "attack FP01",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.5085,
    "content_id": "c_b6c1e388ccf7",
    "creator_id": "attacker_FP01_t1",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.6175,
    "style_score": 0.3994
   }
  },
  {
   "request": "attack FP02",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.5219,
    "content_id": "c_8822ccc0bef9",
    "creator_id": "attacker_FP02_t1",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.7387,
    "style_score": 0.5219
   }
  },
  {
   "request": "attack FP03",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.5919,
    "content_id": "c_1772258b2967",
    "creator_id": "attacker_FP03_t1",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.8051,
    "style_score": 0.5919
   }
  },
  {
   "request": "attack FP04",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.5079,
    "content_id": "c_a3344441c3d8",
    "creator_id": "attacker_FP04_t1",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.8329,
    "style_score": 0.5079
   }
  },
  {
   "request": "attack FP05",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.646,
    "content_id": "c_6981c6b3001d",
    "creator_id": "attacker_FP05_t1",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.8005,
    "style_score": 0.4915
   }
  },
  {
   "request": "attack FP06",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.5855,
    "content_id": "c_027491110b10",
    "creator_id": "attacker_FP06_t1",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.8814,
    "style_score": 0.2896
   }
  },
  {
   "request": "attack FP07",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.5519,
    "content_id": "c_8c432a9f1d9c",
    "creator_id": "attacker_FP07_t1",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.8816,
    "style_score": 0.2222
   }
  },
  {
   "request": "attack FP08",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.4112,
    "content_id": "c_fcf7707b673e",
    "creator_id": "attacker_FP08_t1",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.3223,
    "style_score": 0.5
   }
  },
  {
   "request": "attack PI01",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.5368,
    "content_id": "c_2b34e292719a",
    "creator_id": "attacker_PI01_t1",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.4625,
    "style_score": 0.6111
   }
  },
  {
   "request": "attack PI02",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.3244,
    "content_id": "c_b3d14d8c0b30",
    "creator_id": "attacker_PI02_t1",
    "degraded": false,
    "guess": "human",
    "label": "We think this was probably written by a person.",
    "model_score": 0.2044,
    "style_score": 0.4444
   }
  },
  {
   "request": "attack PI03",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.5943,
    "content_id": "c_10942a8d4a8a",
    "creator_id": "attacker_PI03_t1",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.5943,
    "style_score": 0.6438
   }
  },
  {
   "request": "attack PI04",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.4235,
    "content_id": "c_2a2bd2926542",
    "creator_id": "attacker_PI04_t1",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.4998,
    "style_score": 0.3472
   }
  },
  {
   "request": "attack PI05",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.57,
    "content_id": "c_00c3e765cb55",
    "creator_id": "attacker_PI05_t1",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.6401,
    "style_score": 0.5
   }
  },
  {
   "request": "attack PI06",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.4908,
    "content_id": "c_4f20ac3630ab",
    "creator_id": "attacker_PI06_t1",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.5583,
    "style_score": 0.4233
   }
  },
  {
   "request": "attack MF01",
   "status": 400,
   "json": true,
   "response": {
    "error": "bad_request",
    "message": "Send JSON with a non-empty \"text\"."
   }
  },
  {
   "request": "attack MF02",
   "status": 400,
   "json": true,
   "response": {
    "error": "text_too_short",
    "message": "Text is too short to check. Please send at least a few sentences."
   }
  },
  {
   "request": "attack MF03",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.25,
    "content_id": "c_460f815ce0b7",
    "creator_id": "attacker_MF03_t1",
    "degraded": false,
    "guess": "human",
    "label": "We think this was probably written by a person.",
    "model_score": 0.0,
    "style_score": 0.5
   }
  },
  {
   "request": "attack MF04",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.2556,
    "content_id": "c_88864a5854a5",
    "creator_id": "attacker_MF04_t1",
    "degraded": false,
    "guess": "human",
    "label": "We think this was probably written by a person.",
    "model_score": 0.0112,
    "style_score": 0.5
   }
  },
  {
   "request": "attack MF05",
   "status": 400,
   "json": true,
   "response": {
    "error": "text_too_short",
    "message": "Text is too short to check. Please send at least a few sentences."
   }
  },
  {
   "request": "attack MF06",
   "status": 400,
   "json": true,
   "response": {
    "error": "text_too_short",
    "message": "Text is too short to check. Please send at least a few sentences."
   }
  },
  {
   "request": "attack MF07",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.7032,
    "content_id": "c_0bd50f3acf99",
    "creator_id": "attacker_MF07_t1",
    "degraded": false,
    "guess": "ai",
    "label": "This text has patterns we often see in AI-generated writing. This is a guess, not proof, and we can be wrong. If you wrote it yourself, you can appeal using your content ID and a person will review it.",
    "model_score": 0.9064,
    "style_score": 0.5
   }
  },
  {
   "request": "attack MF08",
   "status": 400,
   "json": true,
   "response": {
    "error": "text_too_long",
    "message": "Text is over 20,000 characters. Please send a shorter piece."
   }
  },
  {
   "request": "attack RQ01",
   "status": 400,
   "json": true,
   "response": {
    "error": "bad_request",
    "message": "Send JSON with a non-empty \"text\"."
   }
  },
  {
   "request": "attack RQ02",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.3698,
    "content_id": "c_fd728b51460a",
    "creator_id": "unknown",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.2395,
    "style_score": 0.5
   }
  },
  {
   "request": "attack RQ03",
   "status": 400,
   "json": true,
   "response": {
    "error": "bad_request",
    "message": "Send JSON with a non-empty \"text\"."
   }
  },
  {
   "request": "attack RQ04",
   "status": 400,
   "json": true,
   "response": {
    "error": "bad_request",
    "message": "Send JSON with a non-empty \"text\"."
   }
  },
  {
   "request": "attack RQ05",
   "status": 400,
   "json": true,
   "response": {
    "error": "bad_request",
    "message": "Send JSON with a non-empty \"text\"."
   }
  },
  {
   "request": "attack RQ06",
   "status": 400,
   "json": true,
   "response": {
    "error": "bad_request",
    "message": "\"creator_id\" must be a non-empty string."
   }
  },
  {
   "request": "attack RQ07",
   "status": 400,
   "json": true,
   "response": {
    "error": "bad_request",
    "message": "Send a JSON object, like {\"text\": \"...\"}."
   }
  },
  {
   "request": "attack RQ08",
   "status": 400,
   "json": true,
   "response": {
    "error": "bad_request",
    "message": "Send JSON with a non-empty \"text\"."
   }
  },
  {
   "request": "attack RQ09",
   "status": 400,
   "json": true,
   "response": {
    "error": "bad_request",
    "message": "Send JSON with a non-empty \"text\"."
   }
  },
  {
   "request": "attack RQ10",
   "status": 429,
   "json": true,
   "response": {
    "error": "rate_limited",
    "limit": "5 per 1 minute",
    "message": "Too many submissions. Try again shortly."
   }
  },
  {
   "request": "attack RQ11",
   "status": 429,
   "json": true,
   "response": {
    "error": "rate_limited",
    "limit": "5 per 1 minute",
    "message": "Too many submissions. Try again shortly."
   }
  },
  {
   "request": "attack RQ12",
   "status": 400,
   "json": true,
   "response": {
    "error": "bad_request",
    "message": "Send JSON with a non-empty \"text\"."
   }
  },
  {
   "request": "attack FL01_01",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.2643,
    "content_id": "c_92c3a469c380",
    "creator_id": "attacker_flood_t1",
    "degraded": false,
    "guess": "human",
    "label": "We think this was probably written by a person.",
    "model_score": 0.0287,
    "style_score": 0.5
   }
  },
  {
   "request": "attack FL01_02",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.2643,
    "content_id": "c_01eb25f90291",
    "creator_id": "attacker_flood_t1",
    "degraded": false,
    "guess": "human",
    "label": "We think this was probably written by a person.",
    "model_score": 0.0287,
    "style_score": 0.5
   }
  },
  {
   "request": "attack FL01_03",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.2643,
    "content_id": "c_201de28b8db2",
    "creator_id": "attacker_flood_t1",
    "degraded": false,
    "guess": "human",
    "label": "We think this was probably written by a person.",
    "model_score": 0.0287,
    "style_score": 0.5
   }
  },
  {
   "request": "attack FL01_04",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.2643,
    "content_id": "c_5236f20220ee",
    "creator_id": "attacker_flood_t1",
    "degraded": false,
    "guess": "human",
    "label": "We think this was probably written by a person.",
    "model_score": 0.0287,
    "style_score": 0.5
   }
  },
  {
   "request": "attack FL01_05",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.2643,
    "content_id": "c_ff90e84bc60a",
    "creator_id": "attacker_flood_t1",
    "degraded": false,
    "guess": "human",
    "label": "We think this was probably written by a person.",
    "model_score": 0.0287,
    "style_score": 0.5
   }
  },
  {
   "request": "attack FL01_06",
   "status": 429,
   "json": true,
   "response": {
    "error": "rate_limited",
    "limit": "5 per 1 minute",
    "message": "Too many submissions. Try again shortly."
   }
  },
  {
   "request": "attack FL01_07",
   "status": 429,
   "json": true,
   "response": {
    "error": "rate_limited",
    "limit": "5 per 1 minute",
    "message": "Too many submissions. Try again shortly."
   }
  },
  {
   "request": "attack FL01_08",
   "status": 429,
   "json": true,
   "response": {
    "error": "rate_limited",
    "limit": "5 per 1 minute",
    "message": "Too many submissions. Try again shortly."
   }
  },
  {
   "request": "attack FL01_09",
   "status": 429,
   "json": true,
   "response": {
    "error": "rate_limited",
    "limit": "5 per 1 minute",
    "message": "Too many submissions. Try again shortly."
   }
  },
  {
   "request": "attack FL01_10",
   "status": 429,
   "json": true,
   "response": {
    "error": "rate_limited",
    "limit": "5 per 1 minute",
    "message": "Too many submissions. Try again shortly."
   }
  },
  {
   "request": "attack FL01_11",
   "status": 429,
   "json": true,
   "response": {
    "error": "rate_limited",
    "limit": "5 per 1 minute",
    "message": "Too many submissions. Try again shortly."
   }
  },
  {
   "request": "attack FL01_12",
   "status": 429,
   "json": true,
   "response": {
    "error": "rate_limited",
    "limit": "5 per 1 minute",
    "message": "Too many submissions. Try again shortly."
   }
  },
  {
   "request": "flood 1",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.5322,
    "content_id": "c_b5d80ae0ce14",
    "creator_id": "cap1_flood",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.8288,
    "style_score": 0.5322
   }
  },
  {
   "request": "flood 2",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.5322,
    "content_id": "c_11643dd0e855",
    "creator_id": "cap1_flood",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.8288,
    "style_score": 0.5322
   }
  },
  {
   "request": "flood 3",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.5322,
    "content_id": "c_942f7f8ddc85",
    "creator_id": "cap1_flood",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.8288,
    "style_score": 0.5322
   }
  },
  {
   "request": "flood 4",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.5322,
    "content_id": "c_5690c504f4ee",
    "creator_id": "cap1_flood",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.8288,
    "style_score": 0.5322
   }
  },
  {
   "request": "flood 5",
   "status": 200,
   "json": true,
   "response": {
    "confidence": 0.5322,
    "content_id": "c_08f6419fa766",
    "creator_id": "cap1_flood",
    "degraded": false,
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
    "model_score": 0.8288,
    "style_score": 0.5322
   }
  },
  {
   "request": "flood 6",
   "status": 429,
   "json": true,
   "response": {
    "error": "rate_limited",
    "limit": "5 per 1 minute",
    "message": "Too many submissions. Try again shortly."
   }
  },
  {
   "request": "flood 7",
   "status": 429,
   "json": true,
   "response": {
    "error": "rate_limited",
    "limit": "5 per 1 minute",
    "message": "Too many submissions. Try again shortly."
   }
  },
  {
   "request": "/appeal JSON array",
   "status": 400,
   "json": true,
   "response": {
    "error": "bad_request",
    "message": "Send a JSON object, like {\"content_id\": \"...\", \"reasoning\": \"...\"}."
   }
  },
  {
   "request": "/appeal unparseable",
   "status": 400,
   "json": true,
   "response": {
    "error": "bad_request",
    "message": "Send JSON with a non-empty \"content_id\"."
   }
  },
  {
   "request": "/appeal empty body",
   "status": 400,
   "json": true,
   "response": {
    "error": "bad_request",
    "message": "Send JSON with a non-empty \"content_id\"."
   }
  },
  {
   "request": "/appeal creator_id object",
   "status": 400,
   "json": true,
   "response": {
    "error": "bad_request",
    "message": "\"creator_id\" must be a non-empty string."
   }
  },
  {
   "request": "/appeal unknown content_id",
   "status": 404,
   "json": true,
   "response": {
    "error": "not_found",
    "message": "We couldn't find a submission with content ID c_000000000000. Please check the ID from your original result."
   }
  },
  {
   "request": "GET /nope",
   "status": 404,
   "json": true,
   "response": {
    "error": "not_found",
    "message": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."
   }
  },
  {
   "request": "GET /submit",
   "status": 405,
   "json": true,
   "response": {
    "error": "method_not_allowed",
    "message": "The method is not allowed for the requested URL."
   }
  },
  {
   "request": "GET /appeal",
   "status": 405,
   "json": true,
   "response": {
    "error": "method_not_allowed",
    "message": "The method is not allowed for the requested URL."
   }
  },
  {
   "request": "PUT /submit",
   "status": 405,
   "json": true,
   "response": {
    "error": "method_not_allowed",
    "message": "The method is not allowed for the requested URL."
   }
  }
 ]
}
```

## 5. Nothing else changes

**Trial 1**

```json
{
 "texts": [
  {
   "n": 1,
   "guess": "unsure",
   "confidence": 0.5322,
   "unit8_guess": "unsure",
   "unit8_confidence": 0.5322,
   "same": true
  },
  {
   "n": 2,
   "guess": "unsure",
   "confidence": 0.4542,
   "unit8_guess": "unsure",
   "unit8_confidence": 0.4542,
   "same": true
  },
  {
   "n": 3,
   "guess": "unsure",
   "confidence": 0.6139,
   "unit8_guess": "unsure",
   "unit8_confidence": 0.6139,
   "same": true
  },
  {
   "n": 4,
   "guess": "unsure",
   "confidence": 0.4865,
   "unit8_guess": "unsure",
   "unit8_confidence": 0.4865,
   "same": true
  },
  {
   "n": 5,
   "guess": "unsure",
   "confidence": 0.5166,
   "unit8_guess": "unsure",
   "unit8_confidence": 0.5166,
   "same": true
  },
  {
   "n": 6,
   "guess": "unsure",
   "confidence": 0.5556,
   "unit8_guess": "unsure",
   "unit8_confidence": 0.5556,
   "same": true
  },
  {
   "n": 7,
   "guess": "human",
   "confidence": 0.3144,
   "unit8_guess": "human",
   "unit8_confidence": 0.3144,
   "same": true
  },
  {
   "n": 8,
   "guess": "unsure",
   "confidence": 0.5082,
   "unit8_guess": "unsure",
   "unit8_confidence": 0.5082,
   "same": true
  },
  {
   "n": 9,
   "guess": "unsure",
   "confidence": 0.3574,
   "unit8_guess": "unsure",
   "unit8_confidence": 0.3574,
   "same": true
  },
  {
   "n": 10,
   "guess": "unsure",
   "confidence": 0.5543,
   "unit8_guess": "unsure",
   "unit8_confidence": 0.5543,
   "same": true
  }
 ],
 "real_output": {
  "response": {
   "confidence": 0.5322,
   "content_id": "c_9a99c978712c",
   "creator_id": "cap1_c5_1",
   "degraded": false,
   "guess": "unsure",
   "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
   "model_score": 0.8288,
   "style_score": 0.5322
  },
  "log_entry": {
   "timestamp": "2026-11-21T03:48:08+00:00",
   "content_id": "c_9a99c978712c",
   "creator_id": "cap1_c5_1",
   "guess": "unsure",
   "model_score": 0.8288,
   "style_score": 0.5322,
   "combined_score": 0.5322,
   "label": "We can't tell whether this was written by a person or with AI help. Parts of it read like both. This is not an accusation. If you wrote it yourself, you can tell us by appealing with your content ID.",
   "status": "decided",
   "duration_ms": 1677.5,
   "text_chars": 430
  }
 }
}
```
