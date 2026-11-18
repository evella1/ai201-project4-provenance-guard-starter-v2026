#!/usr/bin/env python3
"""
Check the structured logging: every kind of run and failure leaves a record.

    python check_logging.py

Runs the real Flask app in-process (Flask's test client) against a TEMPORARY
audit log, so logs/audit.jsonl is not touched. Eleven cases: a normal
submission, an appeal, three kinds of bad input, an unknown URL, a wrong
method, a rate limit, a model failure (degraded), an unexpected crash (500)
and a log that can't be written (503).

The failures are caused on purpose by swapping a function for one that raises,
only inside this script, and put back straight after.
"""

import json
import tempfile
from pathlib import Path

import config

KEYS = ("timestamp", "event", "status", "creator_id", "guess", "reason", "http_status",
        "degraded_reason", "error_type", "duration_ms", "text_chars")

TEXT = ("Today, I went to see my friend at a coffee shop. We ordered pastries and coffee. "
        "We had some good chat about what we've been up to in the last few weeks.")


def _raise(message):
    def fail(_text):
        raise RuntimeError(message)
    return fail


def main():
    tmp = Path(tempfile.mkdtemp())
    config.LOG_DIR = tmp
    config.AUDIT_LOG = tmp / "audit.jsonl"

    import detector
    import stylometry
    from app import app

    detector.warm_up()
    c = app.test_client()

    def show(name, r):
        print(f"{name:32s} -> {r.status_code}")
        return r

    r = show("1 normal submit", c.post("/submit", json={"text": TEXT, "creator_id": "chk_ok"}))
    cid = r.get_json()["content_id"]
    show("2 appeal", c.post("/appeal", json={"content_id": cid, "reasoning": "I wrote it."}))
    show("3 empty text", c.post("/submit", json={"text": "  ", "creator_id": "chk_bad"}))
    show("4 too short", c.post("/submit", json={"text": "hi", "creator_id": "chk_bad"}))
    show("5 JSON array body", c.post("/submit", json=[1, 2]))
    show("6 unknown URL", c.get("/nope"))
    show("7 wrong method (GET /submit)", c.get("/submit"))
    for _ in range(config.RATE_LIMIT_PER_MINUTE + 1):
        r = c.post("/submit", json={"text": TEXT, "creator_id": "chk_flood"})
    show("8 one over the minute limit", r)

    orig = detector.model_signal
    detector.model_signal = _raise("simulated model crash")
    show("9 model fails (degraded)", c.post("/submit", json={"text": TEXT, "creator_id": "chk_model"}))
    detector.model_signal = orig

    orig = stylometry.style_signal
    stylometry.style_signal = _raise("simulated bug")
    show("10 unexpected crash (500)", c.post("/submit", json={"text": TEXT, "creator_id": "chk_crash"}))
    stylometry.style_signal = orig

    before = len(config.AUDIT_LOG.read_text(encoding="utf-8").splitlines())
    config.FAULT = "log_error"
    show("11 log can't be written (503)", c.post("/submit", json={"text": TEXT, "creator_id": "chk_log"}))
    config.FAULT = "none"
    after = len(config.AUDIT_LOG.read_text(encoding="utf-8").splitlines())
    print(f"   new log lines during 11: {after - before} (reported on the console instead)")

    lines = config.AUDIT_LOG.read_text(encoding="utf-8").splitlines()
    print("\nThe log (selected fields):")
    for line in lines:
        e = json.loads(line)
        print(json.dumps({k: e[k] for k in KEYS if k in e}, ensure_ascii=False))
    print("\nFull entries: a decision, a rate limit, a degraded decision, a crash:")
    for line in lines:
        e = json.loads(line)
        if (e.get("creator_id") == "chk_ok" and e.get("status") == "decided") \
                or e.get("reason") == "rate_limited" or e.get("degraded") or e.get("event") == "error":
            print(line)


if __name__ == "__main__":
    main()
