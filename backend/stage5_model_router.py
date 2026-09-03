"""
Stage 5: Local Model Selection & Routing — Sovereign AI Workbench

Re-exports get_model_info and MODEL_ROUTING from task_router.py.
No logic lives here — task_router.py is the single source of truth shared by
Stage 3 (classification) and Stage 5 (model selection) without duplication.
"""

from task_router import get_model_info, MODEL_ROUTING  # noqa: F401

__all__ = ["get_model_info", "MODEL_ROUTING"]
