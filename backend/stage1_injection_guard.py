"""
Stage 1: Prompt Injection Scanner — Sovereign AI Workbench

Scans incoming prompt text and extracted OCR text for prompt injection vectors,
system overrides, jailbreak triggers, and command hijacking patterns.

Source: input_guard_deprecated.py (unchanged logic, relocated here).
"""

from input_guard_deprecated import check_prompt_injection, scan_ocr_text  # noqa: F401

__all__ = ["check_prompt_injection", "scan_ocr_text"]
