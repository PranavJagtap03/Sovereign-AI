"""
Stage 3: Task Classification & Routing — Sovereign AI Workbench

Re-exports classify_task and get_model_info from task_router.py.
No logic lives here — task_router.py is the single source of truth so that
Stage 3 and Stage 5 share the same implementation without duplication.
"""

from task_router import classify_task, get_model_info  # noqa: F401

__all__ = ["classify_task", "get_model_info"]
