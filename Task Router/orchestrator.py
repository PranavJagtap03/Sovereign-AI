"""
Minimal agentic orchestrator — shows the actual hookup point between
Workstream 3 (agent loop) and Workstream 2 (task router).

This is intentionally a skeleton: the plan-then-execute loop and tool
dispatcher are here, but the tool implementations themselves (file read/write,
sandboxed code exec, spreadsheet ops, knowledge base search, doc generation)
are separate modules per Workstream 3.2 — stub them in as they land.

The one thing this file nails down: every time the agent needs a model
response, it goes through `RouterClient.route()`, not a direct model call.
That's what keeps model auto-selection working *inside* multi-step agent
tasks, not just for single-shot requests.
"""

import json
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from router_client import RouterClient


# ---------------------------------------------------------------------------
# Tool registry — orchestrator calls into these, keyed by name.
# Wire in real implementations from Workstream 3.2 here.
# ---------------------------------------------------------------------------

def tool_file_read(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def tool_file_write(path: str, content: str) -> str:
    with open(path, "w") as f:
        f.write(content)
    return f"wrote {len(content)} chars to {path}"


def tool_stub_not_implemented(**kwargs) -> str:
    return "TOOL NOT YET IMPLEMENTED — plug in Workstream 3.2 / 4 / 5 / 6 module here"


TOOLS: Dict[str, Callable] = {
    "file_read": tool_file_read,
    "file_write": tool_file_write,
    "code_execute": tool_stub_not_implemented,       # Workstream 3.2
    "vision_analyze": tool_stub_not_implemented,      # Workstream 4.2
    "knowledge_search": tool_stub_not_implemented,    # Workstream 6.2
    "generate_word": tool_stub_not_implemented,       # Workstream 5.1
    "generate_excel": tool_stub_not_implemented,      # Workstream 5.2
    "generate_ppt": tool_stub_not_implemented,        # Workstream 5.3
}


# ---------------------------------------------------------------------------
# Agent state
# ---------------------------------------------------------------------------

@dataclass
class AgentTask:
    goal: str
    max_steps: int = 8
    steps_taken: int = 0
    history: List[dict] = field(default_factory=list)   # trimmed/summarised as it grows
    done: bool = False
    final_output: Optional[str] = None


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class Orchestrator:
    def __init__(self, router: Optional[RouterClient] = None):
        self.router = router or RouterClient()

    def run(self, goal: str, task_type_hint: Optional[str] = None,
            attached_file: Optional[str] = None) -> AgentTask:
        task = AgentTask(goal=goal)

        while not task.done and task.steps_taken < task.max_steps:
            step_result = self._step(task, task_type_hint, attached_file)
            task.history.append(step_result)
            task.steps_taken += 1

            if step_result.get("stop"):
                task.done = True
                task.final_output = step_result.get("output")

        if not task.done:
            task.final_output = "max iterations exceeded without completion"

        return task

    def _step(self, task: AgentTask, task_type_hint: Optional[str],
              attached_file: Optional[str]) -> dict:
        """
        One plan-then-execute step:
        1. Build context from goal + history so far
        2. Ask a model (via router) what to do next: emit a structured
           {action, tool, args} or {action: "finish", output}
        3. Dispatch to the tool if needed
        4. Return the step's result to be appended to history
        """
        context_summary = self._summarise_history(task.history)

        planning_prompt = self._build_planning_prompt(task.goal, context_summary)

        # This is the hookup: routing decision + model call happens here,
        # not hardcoded to one model. Same router used for single-shot
        # requests is used for every step of a multi-step task.
        route_result = self.router.route(
            prompt=planning_prompt,
            task_type=task_type_hint,      # None on first call -> router classifies
            attached_file=attached_file if task.steps_taken == 0 else None,
        )

        if not route_result.ok:
            return {"stop": True, "output": f"router error: {route_result.error}"}

        action = self._parse_action(route_result.response)

        if action["action"] == "finish":
            return {
                "stop": True,
                "output": action.get("output", route_result.response),
                "model_used": route_result.model_used,
                "task_type": route_result.task_type,
            }

        # dispatch to tool
        tool_name = action.get("tool")
        tool_args = action.get("args", {})
        tool_fn = TOOLS.get(tool_name)

        if tool_fn is None:
            observation = f"unknown tool '{tool_name}'"
        else:
            try:
                observation = tool_fn(**tool_args)
            except Exception as e:
                observation = f"tool '{tool_name}' error: {e}"

        return {
            "stop": False,
            "action": action,
            "observation": observation,
            "model_used": route_result.model_used,
            "task_type": route_result.task_type,
        }

    def _build_planning_prompt(self, goal: str, context_summary: str) -> str:
        return (
            f"Goal: {goal}\n\n"
            f"Progress so far:\n{context_summary}\n\n"
            "Respond with a JSON object for your next action, one of:\n"
            '  {"action": "tool_call", "tool": "<tool_name>", "args": {...}}\n'
            '  {"action": "finish", "output": "<final result summary>"}\n'
            f"Available tools: {list(TOOLS.keys())}"
        )

    def _summarise_history(self, history: List[dict], max_entries: int = 6) -> str:
        """
        Context window manager (Workstream 3.3): keep the last N steps verbatim,
        collapse anything older into a one-line summary so long tasks don't blow
        the context window. Swap in a real summarisation call through the router
        if tasks regularly exceed max_entries.
        """
        if not history:
            return "(no steps taken yet)"
        recent = history[-max_entries:]
        lines = []
        for i, step in enumerate(recent):
            action = step.get("action", {})
            obs = step.get("observation", step.get("output", ""))
            lines.append(f"Step {i+1}: {action} -> {obs}")
        if len(history) > max_entries:
            lines.insert(0, f"...({len(history) - max_entries} earlier steps summarised)...")
        return "\n".join(lines)

    def _parse_action(self, model_response: str) -> dict:
        """Best-effort JSON parse of the model's action. Models won't always
        return clean JSON — this needs hardening once you're testing against
        real model output (strip markdown fences, retry-with-correction, etc.)."""
        text = model_response.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # model didn't return valid JSON -> treat as a finish with raw text
            return {"action": "finish", "output": model_response}


if __name__ == "__main__":
    # Manual smoke test — requires router.py running on localhost:8080
    # and Ollama serving the models in config/models.yaml
    orch = Orchestrator()
    result = orch.run("Summarise the key points of this inspection report and draft an approval note")
    print(json.dumps({
        "steps_taken": result.steps_taken,
        "done": result.done,
        "final_output": result.final_output,
    }, indent=2))
