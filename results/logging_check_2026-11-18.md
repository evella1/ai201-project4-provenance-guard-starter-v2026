# Logging check — 2026-11-18

Produced by `python check_logging.py`: the real Flask app, in-process, against a
temporary audit log. Each failure is caused on purpose inside the script.

```
1 normal submit                  -> 200
2 appeal                         -> 200
3 empty text                     -> 400
4 too short                      -> 400
5 JSON array body                -> 400
6 unknown URL                    -> 404
7 wrong method (GET /submit)     -> 405
8 one over the minute limit      -> 429
9 model fails (degraded)         -> 200
10 unexpected crash (500)        -> 500
11 log can't be written (503)    -> 503
   new log lines during 11: 0 (reported on the console instead)

The log (selected fields):
{"timestamp": "2026-11-18T00:09:38+00:00", "status": "decided", "creator_id": "chk_ok", "guess": "ai", "duration_ms": 355.3, "text_chars": 153}
{"timestamp": "2026-11-18T00:09:38+00:00", "event": "appeal", "status": "under_review", "creator_id": "chk_ok", "duration_ms": 16.5}
{"timestamp": "2026-11-18T00:09:38+00:00", "event": "rejected", "status": "rejected", "creator_id": "chk_bad", "reason": "bad_request", "duration_ms": 0.9, "text_chars": 2}
{"timestamp": "2026-11-18T00:09:38+00:00", "event": "rejected", "status": "rejected", "creator_id": "chk_bad", "reason": "text_too_short", "duration_ms": 1.0, "text_chars": 2}
{"timestamp": "2026-11-18T00:09:38+00:00", "event": "rejected", "status": "rejected", "creator_id": "unknown", "reason": "bad_request", "duration_ms": 0.4}
{"timestamp": "2026-11-18T00:09:38+00:00", "event": "rejected", "status": "rejected", "creator_id": "unknown", "reason": "not_found", "http_status": 404, "duration_ms": 0.1}
{"timestamp": "2026-11-18T00:09:38+00:00", "event": "rejected", "status": "rejected", "creator_id": "unknown", "reason": "method_not_allowed", "http_status": 405, "duration_ms": 0.1}
{"timestamp": "2026-11-18T00:09:38+00:00", "status": "decided", "creator_id": "chk_flood", "guess": "ai", "duration_ms": 145.4, "text_chars": 153}
{"timestamp": "2026-11-18T00:09:38+00:00", "status": "decided", "creator_id": "chk_flood", "guess": "ai", "duration_ms": 160.7, "text_chars": 153}
{"timestamp": "2026-11-18T00:09:38+00:00", "status": "decided", "creator_id": "chk_flood", "guess": "ai", "duration_ms": 179.9, "text_chars": 153}
{"timestamp": "2026-11-18T00:09:39+00:00", "status": "decided", "creator_id": "chk_flood", "guess": "ai", "duration_ms": 156.1, "text_chars": 153}
{"timestamp": "2026-11-18T00:09:39+00:00", "status": "decided", "creator_id": "chk_flood", "guess": "ai", "duration_ms": 160.2, "text_chars": 153}
{"timestamp": "2026-11-18T00:09:39+00:00", "event": "rejected", "status": "rejected", "creator_id": "chk_flood", "reason": "rate_limited", "duration_ms": 1.2, "text_chars": 153}
{"timestamp": "2026-11-18T00:09:39+00:00", "status": "decided", "creator_id": "chk_model", "guess": "unsure", "degraded_reason": "model_error", "error_type": "RuntimeError", "duration_ms": 6.3, "text_chars": 153}
{"timestamp": "2026-11-18T00:09:39+00:00", "event": "error", "status": "error", "error_type": "RuntimeError", "duration_ms": 160.3, "text_chars": 153}

Full entries: a decision, a rate limit, a degraded decision, a crash:
{"timestamp": "2026-11-18T00:09:38+00:00", "content_id": "c_bfec4ac9c7ec", "creator_id": "chk_ok", "guess": "ai", "model_score": 0.8492, "style_score": 0.5, "combined_score": 0.6746, "label": "This text has patterns we often see in AI-generated writing. This is a guess, not proof, and we can be wrong. If you wrote it yourself, you can appeal using your content ID and a person will review it.", "status": "decided", "duration_ms": 355.3, "text_chars": 153}
{"timestamp": "2026-11-18T00:09:39+00:00", "creator_id": "chk_flood", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute", "duration_ms": 1.2, "text_chars": 153}
{"timestamp": "2026-11-18T00:09:39+00:00", "content_id": "c_3be57816dfb5", "creator_id": "chk_model", "guess": "unsure", "model_score": null, "style_score": 0.5, "combined_score": null, "label": "We couldn't fully check this text right now, so we can't say whether it was written by a person or with AI help. This is not an accusation. Please submit it again later for a full check.", "status": "decided", "degraded": true, "degraded_reason": "model_error", "error_type": "RuntimeError", "duration_ms": 6.3, "text_chars": 153}
{"timestamp": "2026-11-18T00:09:39+00:00", "event": "error", "status": "error", "route": "/submit", "error_type": "RuntimeError", "detail": "simulated bug", "duration_ms": 160.3, "text_chars": 153}
```

Console output for case 11 (the log itself failed, so the report goes to the server terminal):

```
ERROR in app: Could not write a decision to the audit log
...
OSError: Simulated fault: the audit log could not be written (AI201_FAULT=log_error).
```
