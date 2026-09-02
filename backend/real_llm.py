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
from typing import Dict, Any

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "deepseek-r1:latest"


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
