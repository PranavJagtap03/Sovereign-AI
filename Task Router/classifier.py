"""
Task classifier: decides which task_type a request belongs to.

Strategy:
1. Rule-based pass first (fast, deterministic, demo-safe — this is what you want
   Demo D to rely on so results are 100% reproducible).
2. If rules don't confidently match, fall back to a zero-shot prompt sent to a
   small local model (see classify_with_llm).

Keep the taxonomy small and demo-relevant. Extend TASK_TYPES + RULES together.
"""

import re
from typing import Optional, List

TASK_TYPES = ["coding", "document", "vision", "spreadsheet", "qa"]

# Order matters: more specific rules first. Each rule is (task_type, [patterns]).
RULES = [
    ("vision", [
        r"\.(png|jpe?g|tiff?|bmp)$",
        r"\bscanned\b", r"\bphotograph\b", r"\bimage\b", r"\bdrawing\b",
        r"\bP&ID\b", r"\bocr\b",
    ]),
    ("spreadsheet", [
        r"\.xlsx?$", r"\bspreadsheet\b", r"\bexcel\b", r"\bcompute\b.*\btotals?\b",
        r"\bformula\b", r"\bpivot table\b",
    ]),
    ("coding", [
        r"\bscript\b", r"\bfunction\b", r"\bdebug\b", r"\bwrite (a|the) (python|code)\b",
        r"\bexception\b", r"\btraceback\b", r"```",
    ]),
    ("document", [
        r"\bapproval note\b", r"\bboard (presentation|memo)\b", r"\bsummar(y|ise|ize)\b",
        r"\bdraft\b", r"\breport\b", r"\bletter\b",
    ]),
]


def classify_rule_based(prompt: str, attached_file: Optional[str] = None) -> Optional[str]:
    """
    Returns a task_type string if a rule confidently matches, else None
    (caller should fall back to the LLM classifier).
    """
    text = prompt.lower()

    # Attached file extension is the strongest signal — check first.
    if attached_file:
        fname = attached_file.lower()
        if re.search(r"\.(png|jpe?g|tiff?|bmp|pdf)$", fname):
            # PDFs could be scanned (vision) or text-based (document) — let rules on
            # the prompt text disambiguate; default scanned/image files to vision.
            if fname.endswith(".pdf") and "scan" not in text and "handwritten" not in text:
                pass  # fall through to text rules below
            else:
                return "vision"
        if re.search(r"\.xlsx?$|\.csv$", fname):
            return "spreadsheet"

    for task_type, patterns in RULES:
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return task_type

    return None


def classify_with_llm(prompt: str, small_model_call) -> str:
    """
    Fallback for ambiguous requests. `small_model_call` is a function
    (prompt: str) -> str that hits your smallest local model (e.g. via Ollama).

    Kept as a thin wrapper so you can swap the underlying call without touching
    router logic.
    """
    classifier_prompt = (
        "Classify the following user request into exactly one category: "
        f"{', '.join(TASK_TYPES)}. Respond with only the category word, nothing else.\n\n"
        f"Request: {prompt}"
    )
    result = small_model_call(classifier_prompt).strip().lower()
    for t in TASK_TYPES:
        if t in result:
            return t
    return "qa"  # ultimate fallback bucket


def classify(prompt: str, attached_file: Optional[str] = None,
             small_model_call=None) -> str:
    """Main entry point the router should call."""
    result = classify_rule_based(prompt, attached_file)
    if result:
        return result
    if small_model_call:
        return classify_with_llm(prompt, small_model_call)
    return "qa"
