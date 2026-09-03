"""
Router client — the ONLY thing the orchestrator needs to import to use the
task router. Keeps the orchestrator decoupled from router internals: if the
router's URL, retry policy, or response shape changes, only this file changes.

Usage from orchestrator code:

    from router_client import RouterClient

    router = RouterClient()
    result = router.route("Write a script that parses this CSV...")
    print(result.model_used, result.task_type, result.response)
"""

from dataclasses import dataclass
from typing import Optional
import time
import httpx


ROUTER_BASE_URL = "http://localhost:8080"


@dataclass
class RouteResult:
    task_type: str
    model_used: str
    response: str
    fallback_triggered: bool
    latency_ms: float
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.model_used != "none"


class RouterClient:
    def __init__(self, base_url: str = ROUTER_BASE_URL, timeout: float = 90.0,
                 max_retries: int = 2, retry_backoff_s: float = 1.5):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff_s = retry_backoff_s

    def route(self, prompt: str, task_type: Optional[str] = None,
              attached_file: Optional[str] = None,
              context: Optional[str] = None) -> RouteResult:
        """
        Send a task to the router and get back which model handled it and its
        response. Retries on connection errors (router not up yet / restarting)
        but NOT on model errors (those are the router's own fallback's job).
        """
        payload = {"prompt": prompt}
        if task_type:
            payload["task_type"] = task_type
        if attached_file:
            payload["attached_file"] = attached_file
        if context:
            payload["context"] = context

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = httpx.post(f"{self.base_url}/route", json=payload, timeout=self.timeout)
                resp.raise_for_status()
                data = resp.json()
                return RouteResult(
                    task_type=data["task_type"],
                    model_used=data["model_used"],
                    response=data["response"],
                    fallback_triggered=data["fallback_triggered"],
                    latency_ms=data["latency_ms"],
                )
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                last_error = str(e)
                if attempt < self.max_retries:
                    time.sleep(self.retry_backoff_s * (attempt + 1))
                    continue
            except httpx.HTTPStatusError as e:
                last_error = f"router returned {e.response.status_code}: {e.response.text}"
                break

        return RouteResult(
            task_type=task_type or "unknown", model_used="none", response="",
            fallback_triggered=False, latency_ms=0.0, error=last_error,
        )

    def task_types(self) -> list:
        """What task types the router currently supports — useful for the agent's
        planning step to know what kinds of subtasks it can dispatch."""
        try:
            resp = httpx.get(f"{self.base_url}/task-types", timeout=10.0)
            resp.raise_for_status()
            return resp.json()["task_types"]
        except Exception:
            return []

    def recent_decisions(self, limit: int = 10) -> list:
        """For the UI transparency panel, or for the agent to self-inspect its
        own recent routing history."""
        try:
            resp = httpx.get(f"{self.base_url}/route-log", params={"limit": limit}, timeout=10.0)
            resp.raise_for_status()
            return resp.json()["decisions"]
        except Exception:
            return []
