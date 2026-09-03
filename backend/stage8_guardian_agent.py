"""
Stage 8: Guardian Agent Independent Review — Sovereign AI Workbench

Provides dual-model verification for high-impact claims using an architecturally
distinct model family (Phi-3-Mini-4K) separate from primary task models to avoid
correlated blind spots and enforce human-in-the-loop governance.

IMPORTANT: Guardian logic is intentionally left unchanged — wiring to a real Ollama
call requires explicit confirmation from the project owner before implementation.

Source: guardian_review, GUARDIAN_MODEL from guardian_deprecated.py (zero logic changes).
"""

from guardian_deprecated import guardian_review, GUARDIAN_MODEL  # noqa: F401

__all__ = ["guardian_review", "GUARDIAN_MODEL"]
