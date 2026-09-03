"""
Structured logging for routing decisions.

Every decision gets a timestamped JSON entry: what came in, what task type was
detected, which model was picked and why, whether a fallback fired. This is what
the frontend's agent transparency panel (Workstream 7.2) polls, and what makes
Demo D ("send 3 prompts, watch it pick a different model each time") credible.
"""

import json
import time
from pathlib import Path
from typing import Optional

LOG_PATH = Path(__file__).parent / "routing_log.jsonl"


def log_decision(
    prompt_preview: str,
    task_type: str,
    chosen_model: Optional[str],
    fallback_triggered: bool = False,
    fallback_reason: Optional[str] = None,
    latency_ms: Optional[float] = None,
):
    entry = {
        "timestamp": time.time(),
        "iso_time": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "prompt_preview": prompt_preview[:120],
        "task_type": task_type,
        "chosen_model": chosen_model,
        "fallback_triggered": fallback_triggered,
        "fallback_reason": fallback_reason,
        "latency_ms": latency_ms,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def read_recent_decisions(limit: int = 20):
    """Used by the /route-log API endpoint for the UI sidebar."""
    if not LOG_PATH.exists():
        return []
    with open(LOG_PATH, "r") as f:
        lines = f.readlines()[-limit:]
    return [json.loads(line) for line in lines]
