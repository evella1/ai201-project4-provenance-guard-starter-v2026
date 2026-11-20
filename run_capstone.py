#!/usr/bin/env python3
"""
Check the five capstone criteria (criteria.md, "Unit 9 - Capstone Criteria"),
three trials each, in one command.

    python run_capstone.py                  # 3 trials, about 6 minutes
    python run_capstone.py --label after_fix

How it works:
- The real Flask app runs in-process (Flask's test client): every request
  goes through the whole route, including the rate limiter and the audit log.
- Faults are switched by setting config.FAULT while the script runs. The
  faults are checked at the moment they happen (detector.py, audit.py), so
  this is the same switch AI201_FAULT sets, without restarting a server.
- The audit log goes to a temporary file, so logs/audit.jsonl isn't touched.
- Each submission has its own creator_id, so the rate limit (5 per minute)
  never interferes.
- Criterion 2 is slow on purpose: GPT-2 "takes" 30 seconds and the service
  stops waiting after 10, so each submission takes about 10 seconds.

Writes results/capstone_<date>_<label>.md with the table and the details.
"""

import argparse
import json
import logging
import re
import tempfile
import time
from datetime import datetime
from pathlib import Path

import config
import scenarios

UNIT8_RESULTS = config.RESULTS_DIR / "run_2026-11-15_1427_after.md"


# ── helpers ───────────────────────────────────────────────────────────────────

class ConsoleCounter(logging.Handler):
    """Counts the app's console error messages, to check criterion 3."""

    def __init__(self):
        super().__init__(level=logging.ERROR)
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


def log_lines():
    if not config.AUDIT_LOG.exists():
        return []
    return [json.loads(l) for l in config.AUDIT_LOG.read_text(encoding="utf-8").splitlines() if l.strip()]


def drain_detector_pool(app_module):
    """Wait until every background GPT-2 job has finished (criterion 2 leaves
    some sleeping), so the next check gets a free worker."""
    pool = app_module._detector_pool
    for f in [pool.submit(int) for _ in range(pool._max_workers)]:
        f.result()


def unit8_expected():
    """My 10 texts' results from unit 8 (trial 1 of 'my own writing')."""
    text = UNIT8_RESULTS.read_text(encoding="utf-8")
    section = text.split("### my own writing", 1)[1]
    block = re.search(r"```json\n(.*?)\n```", section, re.S).group(1)
    return json.loads(block)


# ── the five criteria ─────────────────────────────────────────────────────────

def c1_model_failure(client, trial):
    """model_error: 10 of 10 -> 200, unsure, degraded, model_score null, logged as degraded."""
    config.FAULT = "model_error"
    rows, ok = [], 0
    for i, text in enumerate(scenarios.MY_WRITING, 1):
        r = client.post("/submit", json={"text": text, "creator_id": f"cap{trial}_c1_{i}"})
        b = r.get_json(silent=True) or {}
        entry = next((e for e in log_lines() if e.get("content_id") == b.get("content_id")), {})
        passed = (r.status_code == 200 and b.get("guess") == "unsure" and b.get("degraded") is True
                  and b.get("degraded_reason") == "model_error" and b.get("model_score") is None
                  and b.get("content_id") and entry.get("degraded") is True
                  and entry.get("degraded_reason") == "model_error")
        ok += passed
        rows.append({"n": i, "status": r.status_code, "guess": b.get("guess"),
                     "degraded": b.get("degraded"), "reason": b.get("degraded_reason"),
                     "model_score": b.get("model_score"), "logged_degraded": entry.get("degraded"),
                     "pass": bool(passed)})
        if i == 1:
            sample = {"response_status": r.status_code, "response": b, "log_entry": entry}
    # The criterion also says too-short text still gets a 400.
    r = client.post("/submit", json={"text": "hi", "creator_id": f"cap{trial}_c1_short"})
    short = {"status": r.status_code, "error": (r.get_json(silent=True) or {}).get("error"),
             "guess": (r.get_json(silent=True) or {}).get("guess")}
    sample["too_short_status"] = r.status_code
    sample["too_short_response"] = r.get_json(silent=True)
    config.FAULT = "none"
    return ok == 10 and short["status"] == 400, f"{ok}/10, too-short -> {short['status']}", \
        {"submissions": rows, "too_short_under_fault": short, "real_output": sample}


def c2_slow_model(client, trial, app_module):
    """model_slow: 10 of 10 answer within 12 s as degraded unsure, reason timeout."""
    config.FAULT = "model_slow"
    rows, ok = [], 0
    for i, text in enumerate(scenarios.MY_WRITING, 1):
        t0 = time.perf_counter()
        r = client.post("/submit", json={"text": text, "creator_id": f"cap{trial}_c2_{i}"})
        secs = time.perf_counter() - t0
        b = r.get_json(silent=True) or {}
        passed = (secs <= 12 and r.status_code == 200 and b.get("guess") == "unsure"
                  and b.get("degraded") is True and b.get("degraded_reason") == "timeout")
        ok += passed
        rows.append({"n": i, "seconds": round(secs, 2), "status": r.status_code,
                     "guess": b.get("guess"), "reason": b.get("degraded_reason"), "pass": bool(passed)})
        if i == 1:
            entry = next((e for e in log_lines() if e.get("content_id") == b.get("content_id")), {})
            sample = {"seconds": round(secs, 2), "response_status": r.status_code,
                      "response": b, "log_entry": entry}
        print(f"      c2 #{i}: {secs:.1f}s {b.get('degraded_reason')}", flush=True)
    config.FAULT = "none"
    drain_detector_pool(app_module)
    slowest = max(r["seconds"] for r in rows)
    return ok == 10, f"{ok}/10, slowest {slowest:.1f}s", {"submissions": rows, "real_output": sample}


def c3_log_failure(client, trial, console):
    """log_error: 10 of 10 -> JSON 503, never 500, no content_id; console report; no log lines."""
    before = len(log_lines())
    console.messages.clear()
    config.FAULT = "log_error"
    rows, ok = [], 0
    for i, text in enumerate(scenarios.MY_WRITING, 1):
        r = client.post("/submit", json={"text": text, "creator_id": f"cap{trial}_c3_{i}"})
        b = r.get_json(silent=True)
        passed = r.status_code == 503 and r.is_json and b is not None and "content_id" not in b
        ok += passed
        rows.append({"n": i, "status": r.status_code, "json": r.is_json,
                     "content_id": (b or {}).get("content_id"), "pass": bool(passed)})
        if i == 1:
            sample = {"response_status": r.status_code, "response": b,
                      "console": list(console.messages)}
    config.FAULT = "none"
    reports = sum("Could not write" in m for m in console.messages)
    new_lines = len(log_lines()) - before
    met = ok == 10 and reports >= 10 and new_lines == 0
    return met, f"{ok}/10, console reports {reports}, new log lines {new_lines}", \
        {"submissions": rows, "console_reports": reports, "new_log_lines": new_lines,
         "real_output": sample}


def c4_no_html(client, trial, attacks):
    """Every error from either endpoint is JSON: 0 HTML pages."""
    sent = []

    def record(name, r):
        sent.append({"request": name, "status": r.status_code, "json": r.is_json,
                     "response": r.get_json(silent=True) if r.is_json else r.get_data(as_text=True)[:200]})

    for a in attacks:
        if "raw" in a:
            r = client.post("/submit", data=a["raw"].encode("utf-8"),
                            headers={"Content-Type": a["content_type"]})
        else:
            body = a["body"]
            if isinstance(body, dict) and "creator_id" in body and isinstance(body["creator_id"], str):
                body = {**body, "creator_id": f"{body['creator_id']}_t{trial}"}
            r = client.post("/submit", json=body)
        record(f"attack {a['id']}", r)
    for i in range(config.RATE_LIMIT_PER_MINUTE + 2):
        record(f"flood {i + 1}", client.post("/submit", json={"text": scenarios.MY_WRITING[0],
                                                              "creator_id": f"cap{trial}_flood"}))
    record("/appeal JSON array", client.post("/appeal", json=[1, 2]))
    record("/appeal unparseable", client.post("/appeal", data=b"{not json", content_type="application/json"))
    record("/appeal empty body", client.post("/appeal", data=b""))
    record("/appeal creator_id object", client.post("/appeal", json={"content_id": "c_000000000000",
                                                                     "reasoning": "x", "creator_id": {"a": 1}}))
    record("/appeal unknown content_id", client.post("/appeal", json={"content_id": "c_000000000000",
                                                                      "reasoning": "x"}))
    record("GET /nope", client.get("/nope"))
    record("GET /submit", client.get("/submit"))
    record("GET /appeal", client.get("/appeal"))
    record("PUT /submit", client.put("/submit", json={"text": "x"}))

    html = [s for s in sent if not s["json"]]
    crashes = sum(s["status"] == 500 for s in sent)
    return not html, f"{len(sent) - len(html)}/{len(sent)} JSON, {crashes} x 500", \
        {"non_json": html, "requests": len(sent), "status_500": crashes, "all_requests": sent}


def c5_nothing_changes(client, trial, expected):
    """FAULT none: my 10 texts get the same scores and labels as in unit 8."""
    config.FAULT = "none"
    rows, ok = [], 0
    for i, (text, exp) in enumerate(zip(scenarios.MY_WRITING, expected), 1):
        assert text.startswith(exp["sent"][:40]), f"text {i} doesn't match the unit 8 file"
        b = client.post("/submit", json={"text": text, "creator_id": f"cap{trial}_c5_{i}"}).get_json()
        same = all(b.get(k) == exp[k] for k in ("guess", "confidence", "model_score", "style_score"))
        ok += same
        rows.append({"n": i, "guess": b.get("guess"), "confidence": b.get("confidence"),
                     "unit8_guess": exp["guess"], "unit8_confidence": exp["confidence"], "same": same})
        if i == 1:
            entry = next((e for e in log_lines() if e.get("content_id") == b.get("content_id")), {})
            sample = {"response": b, "log_entry": entry}
    return ok == 10, f"{ok}/10 identical", {"texts": rows, "real_output": sample}


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="run")
    parser.add_argument("--trials", type=int, default=3)
    args = parser.parse_args()

    tmp = Path(tempfile.mkdtemp())
    config.LOG_DIR = tmp
    config.AUDIT_LOG = tmp / "audit.jsonl"
    config.FAULT = "none"

    import app as app_module
    import detector
    from run_attacks import load_attacks

    app_module.app.logger.setLevel(logging.ERROR)
    console = ConsoleCounter()
    app_module.app.logger.addHandler(console)

    print("loading GPT-2 ...", flush=True)
    detector.warm_up()
    client = app_module.app.test_client()
    attacks, problems = load_attacks(config.ROOT / "attack_set")
    expected = unit8_expected()

    names = ["1. Model failure", "2. Slow model", "3. Log failure", "4. No HTML errors",
             "5. Nothing else changes"]
    results = {n: [] for n in names}
    details = {n: [] for n in names}

    for trial in range(1, args.trials + 1):
        print(f"\nTrial {trial}", flush=True)
        # Criterion 2 last: it leaves GPT-2 jobs sleeping, drained afterwards.
        runs = [
            (names[4], lambda: c5_nothing_changes(client, trial, expected)),
            (names[0], lambda: c1_model_failure(client, trial)),
            (names[2], lambda: c3_log_failure(client, trial, console)),
            (names[3], lambda: c4_no_html(client, trial, attacks)),
            (names[1], lambda: c2_slow_model(client, trial, app_module)),
        ]
        for name, run in runs:
            passed, summary, detail = run()
            results[name].append((passed, summary))
            details[name].append(detail)
            print(f"  {name:26s} {'pass' if passed else 'FAIL'}  {summary}", flush=True)

    # Table
    heads = " | ".join(f"Trial {t}" for t in range(1, args.trials + 1))
    lines = [f"| Criterion | {heads} | Verdict |", "|---" * (args.trials + 2) + "|"]
    for n in names:
        cells = [f"{'pass' if p else 'FAIL'}: {s}" for p, s in results[n]]
        verdict = "MET" if all(p for p, _ in results[n]) else "MISSED"
        lines.append(f"| {n} | " + " | ".join(cells) + f" | {verdict} |")
    table = "\n".join(lines)
    print("\n" + table)

    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    out = config.RESULTS_DIR / f"capstone_{stamp}_{args.label}.md"
    body = [f"# Capstone criteria run: {args.label}", "",
            f"- Produced by: `run_capstone.py` · {datetime.now():%Y-%m-%d %H:%M}",
            "- Real app in-process (Flask test client), faults switched with `config.FAULT`, "
            "temporary audit log", f"- {args.trials} trial(s) · unit 8 baseline: `{UNIT8_RESULTS.name}`",
            "", table, ""]
    if problems:
        body += ["Attack set rows that didn't load:", ""] + [f"- {p}" for p in problems] + [""]
    for n in names:
        body.append(f"## {n}\n")
        for t, d in enumerate(details[n], 1):
            body += [f"**Trial {t}**", "", "```json", json.dumps(d, indent=1, ensure_ascii=False), "```", ""]
    out.write_text("\n".join(body), encoding="utf-8")
    print(f"\nwritten: {out}")


if __name__ == "__main__":
    main()
