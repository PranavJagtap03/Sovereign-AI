"""
Stage 9: Tool Call Validator — Sovereign AI Workbench

Validates every tool invocation in the ReAct loop against an authorized schema
registry before execution. Blocks path traversal attacks (../, /etc/),
oversized payloads, and calls to tools not in the allowed registry.

Source: validate_tool_call, ALLOWED_TOOLS, parse_action_call
        from execution_guard_deprecated.py (unchanged logic, relocated here).
"""

from execution_guard_deprecated import (  # noqa: F401
    validate_tool_call,
    ALLOWED_TOOLS,
    SUSPICIOUS_PATH_PATTERNS,
    MAX_STRING_LENGTH,
)

__all__ = [
    "validate_tool_call",
    "ALLOWED_TOOLS",
    "SUSPICIOUS_PATH_PATTERNS",
    "MAX_STRING_LENGTH",
]
