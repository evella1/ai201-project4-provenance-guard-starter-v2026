#!/usr/bin/env python3
"""
Measure the cost of one run: seconds of compute on this machine.

There is no API and no tokens to pay for: GPT-2 runs locally. So the real
cost of a submission is the time and CPU it takes. This script sends the same
text through /submit ten times and reports the average.

    python measure_cost.py              # 10 runs
    python measure_cost.py --runs 20

How it measures:
- It runs the real Flask app in-process (Flask's test client), so every run
  goes through the whole /submit route: validation, GPT-2, the style signal,
  the combining rule, the label and the audit log write.
- The audit log goes to a temporary file, so logs/audit.jsonl is not touched.
- GPT-2 is loaded once before timing (as `python app.py` does at startup), and
  that one-time load is reported separately.
- Per run it records wall-clock time (time.perf_counter) and CPU time used by
  this process (time.process_time). CPU time can be higher than wall time,
  because torch uses several CPU cores at once.
- Each run uses its own creator_id, so the rate limit (5 per minute) never
  interferes with the measurement.
"""

import argparse
import os
import platform
import statistics
import sys
import tempfile
import time
from pathlib import Path

import config

# Same text as the README's sample run: 89 words, a typical short submission.
TEXT = (
    "Today, I went to see my friend at a coffee shop. We ordered pastries and coffee. "
    "Unfortunately the coffee came with extra sugar, which I didn't ask for. I almost asked "
    "for a refund but held back seeing how busy the baristas were. We had some good chat "
    "about what we've been up to in the last few weeks. She told me she's been working out "
    "a lot. I found that inspiring and I signed up for a gym the next day. We'll see how it goes."
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=10)
    args = parser.parse_args()

    # Temporary audit log, so the real one stays clean.
    tmp = Path(tempfile.mkdtemp())
    config.LOG_DIR = tmp
    config.AUDIT_LOG = tmp / "audit.jsonl"

    import torch
    import detector
    from app import app

    print(f"machine: {platform.processor() or platform.machine()}, {os.cpu_count()} logical CPUs")
    print(f"python {platform.python_version()}, torch {torch.__version__} "
          f"({torch.get_num_threads()} threads), model {config.DETECTOR_MODEL}")
    print(f"text: {len(TEXT)} characters, {len(TEXT.split())} words")
    print()

    t0 = time.perf_counter()
    detector.warm_up()
    print(f"one-time model load: {time.perf_counter() - t0:.2f} s")
    print()

    client = app.test_client()
    walls, cpus = [], []
    for i in range(1, args.runs + 1):
        w0, c0 = time.perf_counter(), time.process_time()
        r = client.post("/submit", json={"text": TEXT, "creator_id": f"cost_{i}"})
        wall, cpu = time.perf_counter() - w0, time.process_time() - c0
        body = r.get_json()
        if r.status_code != 200 or body.get("degraded"):
            sys.exit(f"run {i}: unexpected answer {r.status_code} {body}")
        walls.append(wall)
        cpus.append(cpu)
        print(f"  run {i:2d}: {wall * 1000:7.1f} ms wall, {cpu * 1000:7.1f} ms CPU  ({body['guess']})")

    print()
    print(f"average over {args.runs} runs: {statistics.mean(walls) * 1000:.1f} ms wall, "
          f"{statistics.mean(cpus) * 1000:.1f} ms CPU")
    print(f"wall: min {min(walls) * 1000:.1f} ms, max {max(walls) * 1000:.1f} ms, "
          f"median {statistics.median(walls) * 1000:.1f} ms")


if __name__ == "__main__":
    main()
