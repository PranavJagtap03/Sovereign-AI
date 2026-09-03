"""
Task Router — Sovereign AI Workbench
Stage 3 / Stage 5 shared module.

Provides deterministic keyword/heuristic task classification (NOT an LLM call —
classification must be instant) and real model-to-task routing reflecting the two
actually-pulled Ollama models: deepseek-r1:latest and qwen2.5vl:7b.

Exported by:
  stage3_task_classifier.py  (re-export, no duplication)
  stage5_model_router.py     (re-export, no duplication)
"""

from typing import Optional, Dict

# ─── Real model-to-task routing ──────────────────────────────────────────────
# Reflects the two Ollama models actually pulled on this machine.
# reason/vram/size kept so main.py display text does not break.

MODEL_ROUTING: Dict[str, Dict[str, str]] = {
    "text": {
        "model": "deepseek-r1:latest",
        "engine": "ollama",
        "reason": "General text, summarisation, and structured writing tasks",
        "vram": "~14 GB",
        "size": "~32B params (Q4_K_M)"
    },
    "code": {
        "model": "deepseek-r1:latest",
        "engine": "ollama",
        "reason": "Code generation, algorithmic reasoning, and syntax analysis",
        "vram": "~14 GB",
        "size": "~32B params (Q4_K_M)"
    },
    "analysis": {
        "model": "deepseek-r1:latest",
        "engine": "ollama",
        "reason": "Document analysis, table comprehension, and structured output",
        "vram": "~14 GB",
        "size": "~32B params (Q4_K_M)"
    },
    "rag": {
        "model": "deepseek-r1:latest",
        "engine": "ollama",
        "reason": "RAG retrieval-grounded Q&A with sovereign knowledge base",
        "vram": "~14 GB",
        "size": "~32B params (Q4_K_M)"
    },
    "vision": {
        "model": "qwen2.5vl:7b",
        "engine": "ollama",
        "reason": "Multimodal vision task — image/PDF visual understanding and OCR",
        "vram": "~6.8 GB",
        "size": "7.6B params (Q4_K_M)"
    },
}

# Image file extensions that force vision routing regardless of text keywords
_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff"}


def classify_task(
    task_text: str,
    has_file: bool = False,
    file_type: Optional[str] = None
) -> str:
    """
    Stage 3: Task Classification & Routing.

    Deterministic keyword/heuristic classification — NOT an LLM call.
    Classification must be instant; this is routing logic, not content generation.

    Priority order:
    1. file_type indicating an image → vision (overrides text keywords)
    2. Code generation keywords → code
    3. Vision / document-visual keywords → vision
    4. RAG / policy Q&A keywords → rag
    5. Analysis signals or has_file → analysis
    6. Default → text

    Args:
        task_text: The (already PII-sanitized) user query string.
        has_file: True if a file attachment is present.
        file_type: File extension or MIME suffix (e.g. ".png", "pdf").
                   If this indicates an image, routes to vision regardless of keywords.

    Returns:
        str: One of "text", "code", "analysis", "rag", "vision".
    """
    # 1. File type hard-overrides — images always go to vision
    if file_type:
        normalised = file_type.lower().strip()
        if not normalised.startswith("."):
            normalised = f".{normalised}"
        if normalised in _IMAGE_EXTENSIONS:
            return "vision"

    text_lower = (task_text or "").lower()

    # 2. Code generation signals
    code_keywords = [
        "code", "script", "function", "python", "program", "write a",
        "implement", "algorithm", "parse", "class", "module", "api",
        "json parser", "data parser"
    ]
    if any(w in text_lower for w in code_keywords):
        return "code"

    # 3. Vision / document-visual signals
    vision_keywords = [
        "image", "diagram", "scan", "ocr", "visual", "chart", "photo",
        "drawing", "figure", "extract from", "inspection report", "engineering report"
    ]
    if any(w in text_lower for w in vision_keywords) or (
        has_file and "excel" in text_lower
    ):
        return "vision"

    # 4. RAG / policy Q&A signals
    rag_keywords = [
        "according to", "what is the", "policy", "sop", "approval process",
        "procedure", "regulation", "guideline", "based on", "from our", "answer"
    ]
    if any(w in text_lower for w in rag_keywords):
        return "rag"

    # 5. Analysis signals or generic file attachment
    if has_file or any(
        w in text_lower for w in ["analyze", "analysis", "report", "summary", "excel", "defect"]
    ):
        return "analysis"

    # 6. Default
    return "text"


def get_model_info(task_type: str) -> dict:
    """
    Stage 5: Local Model Selection.

    Returns the routing entry for the given task type.
    Falls back to 'text' routing if task_type is unrecognised.

    Args:
        task_type: One of "text", "code", "analysis", "rag", "vision".

    Returns:
        dict with keys: model, engine, reason, vram, size.
    """
    return MODEL_ROUTING.get(task_type, MODEL_ROUTING["text"])
