"""
Stage 10: Resource Budget & Execution Limiter — Sovereign AI Workbench

Enforces hard caps on ReAct loop iterations (max 15 steps) and total elapsed
wall-clock time (max 30 seconds) to prevent runaway execution and resource
exhaustion attacks.

Source: check_resource_budget, parse_action_call, MAX_STEPS, MAX_ELAPSED_MS
        from execution_guard_deprecated.py (unchanged logic, relocated here).
"""

from execution_guard_deprecated import (  # noqa: F401
    check_resource_budget,
    parse_action_call,
    MAX_STEPS,
    MAX_ELAPSED_MS,
)

__all__ = [
    "check_resource_budget",
    "parse_action_call",
    "MAX_STEPS",
    "MAX_ELAPSED_MS",
]
