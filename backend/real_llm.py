"""
Real Local LLM Inference Engine (Ollama + DeepSeek-R1)
Runs alongside mock_llm.py without replacing it.
Provides live local GPU inference via Ollama daemon.
"""

import urllib.request
import urllib.error
import json
import time
import re
import base64
import os
from pathlib import Path
from typing import Dict, Any

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "deepseek-r1:latest"
DEFAULT_VISION_MODEL = "qwen2.5vl:7b"


def check_ollama_health() -> bool:
    """
    Pings http://localhost:11434/api/tags with a 2s timeout
    to confirm Ollama daemon is up before attempting real inference.
    """
    try:
        req = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/tags",
            headers={"User-Agent": "SovereignAI-Workbench/1.0"}
        )
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def call_ollama(
    prompt: str,
    model: str = DEFAULT_MODEL,
    timeout_s: int = 60
) -> Dict[str, Any]:
    """
    Calls local Ollama instance for DeepSeek-R1 inference.
    Splits out the <think>...</think> reasoning trace from the final answer.
    Wrapped in try/except — fails closed gracefully without crashing.
    """
    start_time = time.perf_counter()
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "SovereignAI-Workbench/1.0"}
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as response:
            if response.status != 200:
                return {
                    "success": False,
                    "error": f"Ollama HTTP {response.status}: {response.reason}"
                }
            raw_data = json.loads(response.read().decode("utf-8"))
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)

            # Extract reasoning trace and final answer
            raw_resp = raw_data.get("response", "")
            raw_thinking = raw_data.get("thinking", "")

            reasoning_trace = ""
            final_answer = ""

            if raw_thinking:
                reasoning_trace = raw_thinking.strip()
                final_answer = raw_resp.strip()
            elif "<think>" in raw_resp and "</think>" in raw_resp:
                match = re.search(r"<think>(.*?)</think>(.*)", raw_resp, re.DOTALL)
                if match:
                    reasoning_trace = match.group(1).strip()
                    final_answer = match.group(2).strip()
                else:
                    final_answer = raw_resp.strip()
            elif "</think>" in raw_resp:
                parts = raw_resp.split("</think>", 1)
                reasoning_trace = parts[0].replace("<think>", "").strip()
                final_answer = parts[1].strip()
            else:
                final_answer = raw_resp.strip()

            return {
                "success": True,
                "reasoning_trace": reasoning_trace,
                "final_answer": final_answer,
                "model_used": raw_data.get("model", model),
                "inference_time_ms": elapsed_ms
            }

    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"Ollama connection error: {e.reason}"
        }
    except TimeoutError:
        return {
            "success": False,
            "error": f"Ollama request timed out after {timeout_s}s"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Ollama inference exception: {str(e)}"
        }


def call_ollama_vision(
    image_path: str,
    prompt: str,
    model: str = DEFAULT_VISION_MODEL,
    timeout_s: int = 60
) -> Dict[str, Any]:
    """
    Calls local Ollama instance for Qwen2.5-VL vision inference with an image.
    Reads the image file, base64-encodes it, POSTs to http://localhost:11434/api/generate
    with {"model": model, "prompt": prompt, "images": [base64_string], "stream": False}.
    Wrapped in try/except — fails closed gracefully without crashing.
    """
    start_time = time.perf_counter()

    # Resolve image to base64
    b64_image = None
    try:
        # Check if already a base64 data URI
        if image_path.startswith("data:image"):
            b64_image = image_path.split(",", 1)[1].strip()
        else:
            resolved_path = None
            candidates = [
                image_path,
                os.path.join(os.path.dirname(__file__), image_path),
                os.path.join(os.path.dirname(__file__), "test_files", os.path.basename(image_path)),
                os.path.join(os.path.dirname(__file__), "outputs", os.path.basename(image_path)),
            ]
            for c in candidates:
                if os.path.exists(c) and os.path.isfile(c):
                    resolved_path = c
                    break

            # If it's a PDF filename, check if a corresponding PNG exists in test_files
            if not resolved_path and image_path.lower().endswith(".pdf"):
                stem = Path(image_path).stem
                pdf_png_candidates = [
                    os.path.join(os.path.dirname(__file__), "test_files", f"{stem}.png"),
                    os.path.join(os.path.dirname(__file__), "test_files", "pump_defect_report.png"),
                    os.path.join(os.path.dirname(__file__), "test_files", "sample_inspection_report.png"),
                ]
                for p in pdf_png_candidates:
                    if os.path.exists(p) and os.path.isfile(p):
                        resolved_path = p
                        break

            if not resolved_path or not os.path.exists(resolved_path):
                return {
                    "success": False,
                    "error": f"Image file not found: {image_path}"
                }

            with open(resolved_path, "rb") as f:
                b64_image = base64.b64encode(f.read()).decode("utf-8")

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to read/encode image: {str(e)}"
        }

    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "images": [b64_image],
        "stream": False
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "SovereignAI-Workbench/1.0"}
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as response:
            if response.status != 200:
                return {
                    "success": False,
                    "error": f"Ollama HTTP {response.status}: {response.reason}"
                }
            raw_data = json.loads(response.read().decode("utf-8"))
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            final_answer = raw_data.get("response", "").strip()

            return {
                "success": True,
                "final_answer": final_answer,
                "model_used": raw_data.get("model", model),
                "inference_time_ms": elapsed_ms
            }

    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"Ollama connection error: {e.reason}"
        }
    except TimeoutError:
        return {
            "success": False,
            "error": f"Ollama request timed out after {timeout_s}s"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Ollama vision inference exception: {str(e)}"
        }


def call_ollama_with_base64(
    prompt: str,
    image_base64: str,
    model: str = DEFAULT_VISION_MODEL,
    timeout_s: int = 60
) -> dict:
    """
    Calls local Ollama instance for vision inference with a pre-decoded base64 image.

    This is a thin wrapper around the Ollama /api/generate multimodal endpoint for
    callers (e.g. stage7_primary_agent) that already have a base64 string from
    request.file_data, bypassing the filesystem path-resolution logic in
    call_ollama_vision().

    Args:
        prompt:       Text prompt to accompany the image.
        image_base64: Raw base64-encoded image string (no data URI prefix needed).
        model:        Ollama vision model tag (default: qwen2.5vl:7b).
        timeout_s:    Request timeout in seconds (default: 60).

    Returns:
        dict: Same shape as call_ollama_vision() — keys: success, final_answer,
              model_used, inference_time_ms (on success) or error (on failure).
    """
    # Strip data URI prefix if accidentally included
    if image_base64.startswith("data:image"):
        image_base64 = image_base64.split(",", 1)[1].strip()

    start_time = time.perf_counter()
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "images": [image_base64],
        "stream": False
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "SovereignAI-Workbench/1.0"}
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as response:
            if response.status != 200:
                return {
                    "success": False,
                    "error": f"Ollama HTTP {response.status}: {response.reason}"
                }
            raw_data = json.loads(response.read().decode("utf-8"))
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return {
                "success": True,
                "final_answer": raw_data.get("response", "").strip(),
                "model_used": raw_data.get("model", model),
                "inference_time_ms": elapsed_ms
            }

    except urllib.error.URLError as e:
        return {"success": False, "error": f"Ollama connection error: {e.reason}"}
    except TimeoutError:
        return {"success": False, "error": f"Ollama request timed out after {timeout_s}s"}
    except Exception as e:
        return {"success": False, "error": f"Ollama base64 vision exception: {str(e)}"}

