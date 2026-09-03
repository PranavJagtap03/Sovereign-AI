"""
Task Router API.

POST /route  -> classify + dispatch a request to the right local model
GET  /route-log -> recent routing decisions, for the UI transparency panel
GET  /task-types -> what task types are currently supported (from registry)

Run with:
    uvicorn router:app --host 0.0.0.0 --port 8080

This talks to Ollama by default (http://localhost:11434/api/generate). Swap
`call_model` if you're using vLLM or a different runtime.
"""

import time
from typing import Optional

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

from classifier import classify
from registry import ModelRegistry
from logger import log_decision, read_recent_decisions

app = FastAPI(title="Task Router")
registry = ModelRegistry()


class RouteRequest(BaseModel):
    prompt: str
    task_type: Optional[str] = None       # caller can force a task type; else we classify
    attached_file: Optional[str] = None    # filename, used as a classification signal
    context: Optional[str] = None


class RouteResponse(BaseModel):
    task_type: str
    model_used: str
    response: str
    fallback_triggered: bool
    latency_ms: float


def call_model(endpoint: str, model_name: str, prompt: str, timeout: float = 60.0) -> str:
    """
    Thin wrapper around the inference runtime. Swap this body for vLLM's API
    shape if that's what you're running — nothing else in the router changes.
    """
    resp = httpx.post(
        f"{endpoint}/api/generate",
        json={"model": model_name, "prompt": prompt, "stream": False},
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json().get("response", "")


def small_model_classifier_call(prompt: str) -> str:
    """Used by classify() as the zero-shot fallback when rules don't match."""
    candidates = registry.candidates_for("qa")
    if not candidates:
        return "qa"
    fastest = candidates[0]
    try:
        return call_model(fastest.endpoint, fastest.name, prompt, timeout=15.0)
    except Exception:
        return "qa"


@app.post("/route", response_model=RouteResponse)
def route(req: RouteRequest):
    start = time.time()

    task_type = req.task_type or classify(
        req.prompt, req.attached_file, small_model_call=small_model_classifier_call
    )

    candidates = registry.candidates_for(task_type)
    if not candidates:
        # No model registered for this task type at all — fall back to qa bucket.
        candidates = registry.candidates_for("qa")
        task_type = "qa"

    fallback_triggered = False
    fallback_reason = None
    last_error = None
    result_text = None
    model_used = None

    for i, model in enumerate(candidates):
        try:
            result_text = call_model(model.endpoint, model.name, req.prompt)
            model_used = model.name
            if i > 0:
                fallback_triggered = True
                fallback_reason = f"primary model(s) failed: {last_error}"
            break
        except Exception as e:
            last_error = str(e)
            continue

    latency_ms = (time.time() - start) * 1000

    if result_text is None:
        # every candidate failed
        log_decision(req.prompt, task_type, None, fallback_triggered=True,
                     fallback_reason=f"all candidates failed: {last_error}",
                     latency_ms=latency_ms)
        return RouteResponse(
            task_type=task_type, model_used="none", response=f"Error: {last_error}",
            fallback_triggered=True, latency_ms=latency_ms,
        )

    log_decision(req.prompt, task_type, model_used, fallback_triggered, fallback_reason, latency_ms)

    return RouteResponse(
        task_type=task_type,
        model_used=model_used,
        response=result_text,
        fallback_triggered=fallback_triggered,
        latency_ms=latency_ms,
    )


@app.get("/route-log")
def route_log(limit: int = 20):
    return {"decisions": read_recent_decisions(limit)}


@app.get("/task-types")
def task_types():
    return {"task_types": registry.all_task_types()}


@app.post("/reload-registry")
def reload_registry():
    """Hot-reload models.yaml without restarting the service — handy when demoing
    'we can add a new model without redesigning the system.'"""
    registry.load()
    return {"status": "reloaded", "models": [m.name for m in registry.models]}
