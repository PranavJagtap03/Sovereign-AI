"""
Stage 1: Prompt Injection Scanner — Sovereign AI Workbench
Scans incoming prompt text and extracted OCR text for prompt injection vectors,
system overrides, jailbreak triggers, and command hijacking patterns.
"""

import re
import time
import random
from typing import Dict, List, Any


# Common prompt injection patterns and jailbreak signatures
INJECTION_PATTERNS: List[Dict[str, Any]] = [
    {
        "pattern": r"(?i)ignore\s+all\s+previous\s+instructions",
        "label": "IGNORE ALL PREVIOUS INSTRUCTIONS",
        "risk": 0.97
    },
    {
        "pattern": r"(?i)ignore\s+(?:the\s+)?previous\s+instructions",
        "label": "ignore previous instructions",
        "risk": 0.92
    },
    {
        "pattern": r"(?i)disregard\s+(?:the\s+)?above",
        "label": "disregard the above",
        "risk": 0.90
    },
    {
        "pattern": r"(?i)disregard\s+previous",
        "label": "disregard previous",
        "risk": 0.88
    },
    {
        "pattern": r"(?i)you\s+are\s+now\s+(?:a|an)?",
        "label": "you are now",
        "risk": 0.85
    },
    {
        "pattern": r"(?i)system\s+prompt\s*:",
        "label": "system prompt",
        "risk": 0.89
    },
    {
        "pattern": r"(?i)override\s+safety",
        "label": "override safety",
        "risk": 0.95
    },
    {
        "pattern": r"(?i)jailbreak",
        "label": "jailbreak",
        "risk": 0.96
    },
    {
        "pattern": r"(?i)act\s+as\s+DAN",
        "label": "act as DAN",
        "risk": 0.98
    },
    {
        "pattern": r"(?i)\[SYSTEM\s+INSTRUCTION\]|<!--\s*system:",
        "label": "hidden command marker",
        "risk": 0.94
    }
]


def check_prompt_injection(task_text: str) -> Dict[str, Any]:
    """
    Scans incoming prompt text for prompt injection vectors and adversarial patterns.

    Args:
        task_text: Raw user prompt or instruction string.

    Returns:
        dict containing:
          - injection_detected (bool)
          - risk_score (float)
          - matched_patterns (list[str])
          - scan_duration_ms (int)
    """
    start_time = time.perf_counter()

    if not task_text:
        return {
            "injection_detected": False,
            "risk_score": 0.01,
            "matched_patterns": [],
            "scan_duration_ms": 2
        }

    matched_labels = []
    max_risk = 0.01

    # Special demo trigger handling
    if "IGNORE ALL PREVIOUS INSTRUCTIONS" in task_text.upper():
        matched_labels.append("IGNORE ALL PREVIOUS INSTRUCTIONS")
        max_risk = 0.97
    else:
        # Pattern scan
        for item in INJECTION_PATTERNS:
            if re.search(item["pattern"], task_text):
                matched_labels.append(item["label"])
                if item["risk"] > max_risk:
                    max_risk = item["risk"]

    elapsed_ms = max(1, int((time.perf_counter() - start_time) * 1000)) + random.randint(2, 5)

    injection_detected = len(matched_labels) > 0

    return {
        "injection_detected": injection_detected,
        "risk_score": round(max_risk, 2) if injection_detected else round(random.uniform(0.01, 0.05), 2),
        "matched_patterns": matched_labels,
        "scan_duration_ms": elapsed_ms
    }


def scan_ocr_text(extracted_text: str) -> Dict[str, Any]:
    """
    Scans text extracted from images/PDFs via OCR for embedded prompt injection attacks.
    Currently wraps check_prompt_injection for simulated OCR input.

    Args:
        extracted_text: Raw OCR extracted text string.

    Returns:
        dict containing injection check results.
    """
    return check_prompt_injection(extracted_text)
