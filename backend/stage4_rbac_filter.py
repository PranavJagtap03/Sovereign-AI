"""
Stage 4: Authorization & RBAC Filter — Sovereign AI Workbench

Compares the requesting user's role clearance against each retrieved document's
sensitivity classification. Fails closed — unrecognised sensitivity ranks as 999,
blocking access rather than granting it.

Source: check_access, CLEARANCE_SCALE, CLEARANCE_LEVELS, USER_CLEARANCE
        extracted from mock_rag_deprecated.py (unchanged logic, relocated here).
"""

from mock_rag_deprecated import (  # noqa: F401
    check_access,
    CLEARANCE_SCALE,
    CLEARANCE_LEVELS,
    USER_CLEARANCE,
)

__all__ = ["check_access", "CLEARANCE_SCALE", "CLEARANCE_LEVELS", "USER_CLEARANCE"]
