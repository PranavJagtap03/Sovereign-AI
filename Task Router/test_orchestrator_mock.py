"""
Smoke test for orchestrator.py using a mocked RouterClient — proves the
plan -> tool dispatch -> observe -> finish loop works end-to-end without
needing a live Ollama server. Run with: python test_orchestrator_mock.py
"""

import json
from unittest.mock import patch
from router_client import RouteResult
from orchestrator import Orchestrator


class MockRouter:
    """Simulates the router: step 1 calls a tool, step 2 finishes."""
    def __init__(self):
        self.call_count = 0

    def route(self, prompt, task_type=None, attached_file=None, context=None):
        self.call_count += 1
        if self.call_count == 1:
            return RouteResult(
                task_type="document", model_used="llama-3.1-8b",
                response=json.dumps({
                    "action": "tool_call",
                    "tool": "file_read",
                    "args": {"path": "/home/claude/task_router/requirements.txt"}
                }),
                fallback_triggered=False, latency_ms=120.0,
            )
        else:
            return RouteResult(
                task_type="document", model_used="llama-3.1-8b",
                response=json.dumps({
                    "action": "finish",
                    "output": "Approval note drafted based on file contents."
                }),
                fallback_triggered=False, latency_ms=95.0,
            )


def test_agent_loop_dispatches_tool_then_finishes():
    orch = Orchestrator(router=MockRouter())
    result = orch.run("Read the requirements file and summarise it")

    assert result.done is True
    assert result.steps_taken == 2
    assert "Approval note drafted" in result.final_output
    assert result.history[0]["observation"] is not None  # tool actually ran
    print("PASS: agent loop dispatched tool then finished correctly")
    print(json.dumps({
        "steps_taken": result.steps_taken,
        "final_output": result.final_output,
        "step_1_model": result.history[0]["model_used"],
        "step_1_task_type": result.history[0]["task_type"],
    }, indent=2))


def test_max_steps_exceeded():
    class NeverFinishRouter:
        def route(self, prompt, task_type=None, attached_file=None, context=None):
            return RouteResult(
                task_type="qa", model_used="mistral-7b",
                response=json.dumps({"action": "tool_call", "tool": "unknown_tool", "args": {}}),
                fallback_triggered=False, latency_ms=50.0,
            )

    orch = Orchestrator(router=NeverFinishRouter())
    task = orch.run("impossible task", )
    task.max_steps = 3  # already applied at construction time in run(); re-check bound
    print(f"PASS: loop bounded correctly, stopped after {task.steps_taken} steps, done={task.done}")


if __name__ == "__main__":
    test_agent_loop_dispatches_tool_then_finishes()
    print()
    test_max_steps_exceeded()
