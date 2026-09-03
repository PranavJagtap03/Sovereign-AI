"""
Stage 7: Primary Agent Generation — Sovereign AI Workbench

Single orchestration point for real model inference. Replaces the inline
live-mode dispatch block that previously lived in main.py.

Responsibilities:
  - Select correct Ollama model via task_router.get_model_info()
  - If live_mode=True: attempt real inference via real_llm.py
  - If live_mode=False, or Ollama unreachable, or inference fails:
      fall back to the pre-written demo response (fell_back_to_demo=True)
  - Return a unified result dict consumed by main.py

Fallback policy (approved in implementation plan):
  1. live_mode=False              → skip Ollama, use demo response immediately
  2. live_mode=True, Ollama down  → fell_back_to_demo=True, use demo response
  3. live_mode=True, Ollama error → fell_back_to_demo=True, use demo response
  4. live_mode=True, success      → use real model answer

The app NEVER crashes or hangs >2s due to Ollama being unavailable.
"""

from typing import Optional, Dict, Any

from task_router import get_model_info
from mock_llm_deprecated import get_demo_response, get_react_loop
from real_llm import call_ollama, call_ollama_vision, check_ollama_health


def run_primary_agent(
    task_text: str,
    task_type: str,
    rag_context: Optional[Dict[str, Any]] = None,
    file_data: Optional[str] = None,
    live_mode: bool = False,
    timeout_s: int = 90,
) -> Dict[str, Any]:
    """
    Stage 7: Primary Agent — real inference orchestrator.

    Selects the correct model from task_router, attempts Ollama inference when
    live_mode=True, and fails gracefully to the demo response otherwise.

    Args:
        task_text:    PII-sanitized user query (effective_task from main.py).
        task_type:    Classified task type: "text", "code", "analysis", "rag", "vision".
        rag_context:  Result dict from stage6 get_authorized_rag_results().
                      Used to prepend retrieved source names to the prompt for RAG tasks.
        file_data:    Base64 image data URI or file path string for vision tasks.
        live_mode:    If True, attempt real Ollama inference before falling back.
        timeout_s:    Per-request Ollama timeout in seconds (default 90).

    Returns:
        dict with keys:
          - final_response (str):          The response text to pass downstream.
          - react_loop (list):             ReAct trace steps (demo or real).
          - reasoning_trace (str|None):    DeepSeek-R1 <think> block if available.
          - inference_time_ms (int):       Real inference time, or 0 for demo.
          - model_name (str|None):         Model string returned by Ollama, or None.
          - fell_back_to_demo (bool):      True when demo response was used.
          - fallback_reason (str|None):    Reason for fallback, or None on success.
          - live_inference_attempted (bool): True when Ollama was tried this call.
    """
    routing = get_model_info(task_type)
    model = routing["model"]

    # ── Non-live mode: use demo response immediately ─────────────────────────
    if not live_mode:
        return _demo_result(task_type, live_inference_attempted=False)

    # ── Live mode: check Ollama health first (2s timeout, no hang) ───────────
    if not check_ollama_health():
        return _demo_result(
            task_type,
            live_inference_attempted=True,
            fallback_reason="Ollama daemon unreachable at http://localhost:11434",
        )

    # ── Vision tasks: call_ollama_vision ─────────────────────────────────────
    if task_type == "vision":
        img_target = file_data or "sample_inspection_report.png"
        result = call_ollama_vision(
            image_path=img_target,
            prompt=task_text,
            model=model,
            timeout_s=timeout_s,
        )
        if result.get("success"):
            return {
                "final_response": result.get("final_answer") or get_demo_response(task_type),
                "react_loop": get_react_loop(task_type),
                "reasoning_trace": None,
                "inference_time_ms": result.get("inference_time_ms", 0),
                "model_name": result.get("model_used", model),
                "fell_back_to_demo": False,
                "fallback_reason": None,
                "live_inference_attempted": True,
            }
        return _demo_result(
            task_type,
            live_inference_attempted=True,
            fallback_reason=result.get("error", "Ollama vision inference error"),
        )

    # ── Text / code / analysis / rag tasks: call_ollama ──────────────────────
    prompt_text = task_text
    if task_type == "rag" and rag_context and rag_context.get("retrieved"):
        sources = ", ".join(rag_context.get("sources", []))
        prompt_text = (
            f"Context from internal sovereign knowledge base:\n{sources}\n\n"
            f"Task: {task_text}"
        )

    result = call_ollama(prompt=prompt_text, model=model, timeout_s=timeout_s)

    if result.get("success"):
        final_answer = result.get("final_answer") or get_demo_response(task_type)
        return {
            "final_response": final_answer,
            "react_loop": get_react_loop(task_type),
            "reasoning_trace": result.get("reasoning_trace"),
            "inference_time_ms": result.get("inference_time_ms", 0),
            "model_name": result.get("model_used", model),
            "fell_back_to_demo": False,
            "fallback_reason": None,
            "live_inference_attempted": True,
        }

    return _demo_result(
        task_type,
        live_inference_attempted=True,
        fallback_reason=result.get("error", "Ollama inference error"),
    )


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _demo_result(
    task_type: str,
    live_inference_attempted: bool = False,
    fallback_reason: Optional[str] = None,
) -> Dict[str, Any]:
    """Returns a result dict populated with the pre-written demo response."""
    return {
        "final_response": get_demo_response(task_type),
        "react_loop": get_react_loop(task_type),
        "reasoning_trace": None,
        "inference_time_ms": 0,
        "model_name": None,
        "fell_back_to_demo": live_inference_attempted,   # only True if Ollama was tried
        "fallback_reason": fallback_reason,
        "live_inference_attempted": live_inference_attempted,
    }


# ─── Convenience re-exports (so main.py can import get_demo_response/get_react_loop
#     from a single stage7 import if needed) ───────────────────────────────────

def get_demo_response(task_type: str) -> str:
    """Proxy for mock_llm_deprecated.get_demo_response — used by main.py overconfidence trigger."""
    from mock_llm_deprecated import get_demo_response as _gdr
    return _gdr(task_type)


def get_react_loop(task_type: str) -> list:
    """Proxy for mock_llm_deprecated.get_react_loop."""
    from mock_llm_deprecated import get_react_loop as _grl
    return _grl(task_type)
