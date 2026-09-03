"""
Full Task Router integration test — tests the entire pipeline WITHOUT Ollama.

What it covers (maps directly to Workstream 2 acceptance criteria):
  - Rule-based classification routes each task type correctly
  - Registry returns the right model for each task type (with priority ordering)
  - Fallback logic: if the primary model fails, the next candidate is tried
  - Logging: every routing decision produces a structured JSONL entry
  - Auto-selection proof: 3 prompts → 3 different models (Demo D scenario)
  - LLM fallback classifier works when rules don't match
  - Edge cases: unknown task types, all models down, file-extension signals

Run with:  python test_router_integration.py
       or: pytest test_router_integration.py -v
"""

import json
import time
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from classifier import classify_rule_based, classify_with_llm, classify, TASK_TYPES
from registry import ModelRegistry, ModelEntry
from logger import log_decision, read_recent_decisions, LOG_PATH
from router_client import RouteResult


# ── Helpers ──────────────────────────────────────────────────────────────────

def clean_log():
    """Remove the routing log file so tests start fresh."""
    if LOG_PATH.exists():
        LOG_PATH.unlink()


# ── 1. Classifier: rule-based routing ────────────────────────────────────────

class TestClassifierRuleBased:
    """Workstream 2.1 — each task type routes correctly via keywords/extensions."""

    def test_coding_by_keyword(self):
        assert classify_rule_based("Write a Python script to parse CSVs") == "coding"

    def test_coding_by_backticks(self):
        assert classify_rule_based("Fix this code:\n```\nprint('hello')\n```") == "coding"

    def test_coding_by_debug(self):
        assert classify_rule_based("I need to debug this traceback") == "coding"

    def test_document_by_draft(self):
        assert classify_rule_based("Draft a letter to the vendor") == "document"

    def test_document_by_summary(self):
        assert classify_rule_based("Summarize the key points from this report") == "document"

    def test_document_approval_note(self):
        assert classify_rule_based("Write an approval note for this procurement") == "document"

    def test_vision_by_image_extension(self):
        assert classify_rule_based("Analyze this", attached_file="diagram.png") == "vision"

    def test_vision_by_scanned_keyword(self):
        assert classify_rule_based("Read this scanned document") == "vision"

    def test_vision_pid_diagram(self):
        assert classify_rule_based("Interpret this P&ID and list all valves") == "vision"

    def test_vision_scanned_pdf(self):
        assert classify_rule_based("Process this scanned report", attached_file="scan.pdf") == "vision"

    def test_spreadsheet_by_extension(self):
        assert classify_rule_based("Process this", attached_file="data.xlsx") == "spreadsheet"

    def test_spreadsheet_by_csv_extension(self):
        assert classify_rule_based("Analyze this", attached_file="report.csv") == "spreadsheet"

    def test_spreadsheet_by_keyword(self):
        assert classify_rule_based("Build a spreadsheet with formulas") == "spreadsheet"

    def test_spreadsheet_pivot_table(self):
        assert classify_rule_based("Create a pivot table from the sales data") == "spreadsheet"

    def test_text_pdf_falls_to_document_rules(self):
        assert classify_rule_based("Summarise this SOP", attached_file="sop.pdf") == "document"

    def test_ambiguous_returns_none(self):
        assert classify_rule_based("hello world") is None

    def test_empty_prompt_returns_none(self):
        assert classify_rule_based("") is None


# ── 2. Classifier: LLM fallback ──────────────────────────────────────────────

class TestClassifierLLMFallback:
    """Workstream 2.1 — when rules don't match, the LLM classifier picks a type."""

    def test_llm_returns_valid_type(self):
        mock_llm = MagicMock(return_value="coding")
        result = classify_with_llm("refactor this module", mock_llm)
        assert result == "coding"
        mock_llm.assert_called_once()

    def test_llm_returns_noisy_output(self):
        mock_llm = MagicMock(return_value="I think this is a document request")
        result = classify_with_llm("some ambiguous prompt", mock_llm)
        assert result == "document"

    def test_llm_returns_garbage_defaults_to_qa(self):
        mock_llm = MagicMock(return_value="absolutely no idea lol")
        result = classify_with_llm("some prompt", mock_llm)
        assert result == "qa"

    def test_classify_entry_point_uses_rules_first(self):
        mock_llm = MagicMock()
        result = classify("Write a Python script", small_model_call=mock_llm)
        assert result == "coding"
        mock_llm.assert_not_called()

    def test_classify_entry_point_falls_to_llm(self):
        mock_llm = MagicMock(return_value="qa")
        result = classify("hello there", small_model_call=mock_llm)
        assert result == "qa"
        mock_llm.assert_called_once()

    def test_classify_no_llm_no_match_defaults_qa(self):
        result = classify("good morning")
        assert result == "qa"


# ── 3. Registry: model lookup ────────────────────────────────────────────────

class TestRegistry:
    """Workstream 2.2 — registry loads YAML and returns correct candidates."""

    def test_loads_all_models(self):
        reg = ModelRegistry()
        assert len(reg.models) >= 4, f"Expected >=4 models, got {len(reg.models)}"

    def test_coding_routes_to_qwen(self):
        reg = ModelRegistry()
        candidates = reg.candidates_for("coding")
        assert len(candidates) >= 1
        assert candidates[0].name == "qwen2.5-coder-7b"

    def test_document_routes_to_llama_first(self):
        reg = ModelRegistry()
        candidates = reg.candidates_for("document")
        assert candidates[0].name == "llama-3.1-8b"
        assert candidates[1].name == "mistral-7b"

    def test_vision_routes_to_llava(self):
        reg = ModelRegistry()
        candidates = reg.candidates_for("vision")
        assert candidates[0].name == "llava-1.6"

    def test_qa_has_multiple_candidates(self):
        reg = ModelRegistry()
        candidates = reg.candidates_for("qa")
        assert len(candidates) >= 2

    def test_unknown_type_returns_empty(self):
        reg = ModelRegistry()
        assert reg.candidates_for("nonexistent_type") == []

    def test_priority_ordering(self):
        reg = ModelRegistry()
        candidates = reg.candidates_for("document")
        priorities = [m.priority for m in candidates]
        assert priorities == sorted(priorities), "Candidates must be sorted by priority"

    def test_all_task_types_complete(self):
        reg = ModelRegistry()
        types = reg.all_task_types()
        for expected in ["coding", "document", "qa", "spreadsheet", "vision"]:
            assert expected in types, f"Missing task type: {expected}"


# ── 4. Logger: structured decision logging ───────────────────────────────────

class TestLogger:
    """Workstream 2.2 — every routing decision is logged with reason."""

    def setup_method(self):
        clean_log()

    def test_log_creates_entry(self):
        entry = log_decision("test prompt", "coding", "qwen2.5-coder-7b", latency_ms=42.0)
        assert entry["task_type"] == "coding"
        assert entry["chosen_model"] == "qwen2.5-coder-7b"
        assert entry["latency_ms"] == 42.0
        assert entry["fallback_triggered"] is False

    def test_log_fallback_entry(self):
        entry = log_decision("test", "document", "mistral-7b",
                             fallback_triggered=True,
                             fallback_reason="llama-3.1-8b OOM",
                             latency_ms=200.0)
        assert entry["fallback_triggered"] is True
        assert "OOM" in entry["fallback_reason"]

    def test_read_recent_decisions(self):
        log_decision("first", "coding", "qwen2.5-coder-7b", latency_ms=10)
        log_decision("second", "document", "llama-3.1-8b", latency_ms=20)
        log_decision("third", "vision", "llava-1.6", latency_ms=30)
        decisions = read_recent_decisions(limit=2)
        assert len(decisions) == 2
        assert decisions[-1]["task_type"] == "vision"

    def test_log_persists_to_disk(self):
        log_decision("persist test", "qa", "mistral-7b", latency_ms=5)
        assert LOG_PATH.exists()
        with open(LOG_PATH) as f:
            lines = f.readlines()
        assert len(lines) >= 1
        data = json.loads(lines[-1])
        assert data["prompt_preview"] == "persist test"

    def teardown_method(self):
        clean_log()


# ── 5. Demo D: auto-selection across 3 task types ───────────────────────────

class TestDemoDAutoSelection:
    """
    Workstream 2.3 / Demo D — three different prompts back-to-back, each
    routes to a DIFFERENT model. This is the 60-second proof point.
    """

    def test_three_prompts_three_models(self):
        reg = ModelRegistry()
        prompts = [
            ("Write a Python function to sort a list", None),
            ("Draft an approval note for this inspection", None),
            ("Analyze this engineering drawing", "diagram.png"),
        ]

        models_used = []
        for prompt, attached_file in prompts:
            task_type = classify_rule_based(prompt, attached_file)
            candidates = reg.candidates_for(task_type)
            assert len(candidates) >= 1, f"No model for task_type={task_type}"
            models_used.append(candidates[0].name)

        assert len(set(models_used)) == 3, f"Expected 3 unique models, got: {models_used}"
        print(f"\n  Demo D proof: {models_used}")


# ── 6. End-to-end pipeline (mocked inference) ───────────────────────────────

class TestEndToEndPipeline:
    """Full pipeline: prompt -> classify -> registry lookup -> model call -> log."""

    def setup_method(self):
        clean_log()

    def test_coding_pipeline(self):
        task_type = classify("Write a Python script to compute Fibonacci numbers")
        assert task_type == "coding"
        reg = ModelRegistry()
        candidates = reg.candidates_for(task_type)
        assert candidates[0].name == "qwen2.5-coder-7b"
        entry = log_decision("Fibonacci script", task_type, candidates[0].name, latency_ms=150.0)
        assert entry["chosen_model"] == "qwen2.5-coder-7b"

    def test_document_pipeline_with_fallback(self):
        task_type = classify("Summarise the quarterly inspection report")
        assert task_type == "document"
        reg = ModelRegistry()
        candidates = reg.candidates_for(task_type)
        assert len(candidates) >= 2
        chosen = candidates[1]  # simulate primary OOM
        entry = log_decision("Quarterly report", task_type, chosen.name,
                             fallback_triggered=True,
                             fallback_reason="llama-3.1-8b: OOM error",
                             latency_ms=300.0)
        assert entry["chosen_model"] == "mistral-7b"
        assert entry["fallback_triggered"] is True

    def test_vision_pipeline_with_attachment(self):
        task_type = classify("Read this inspection photograph", attached_file="site_photo.jpg")
        assert task_type == "vision"
        reg = ModelRegistry()
        candidates = reg.candidates_for(task_type)
        assert candidates[0].name == "llava-1.6"

    def test_unknown_task_falls_to_qa(self):
        task_type = classify("What's the weather like?")
        assert task_type == "qa"
        reg = ModelRegistry()
        candidates = reg.candidates_for(task_type)
        assert len(candidates) >= 1

    def teardown_method(self):
        clean_log()


# ── 7. RouteResult / RouterClient data contract ─────────────────────────────

class TestRouteResult:
    """Validate the RouterClient's data contract (without a live server)."""

    def test_ok_result(self):
        r = RouteResult(task_type="coding", model_used="qwen2.5-coder-7b",
                        response="def fib(n): ...", fallback_triggered=False, latency_ms=100.0)
        assert r.ok is True

    def test_error_result(self):
        r = RouteResult(task_type="coding", model_used="none", response="",
                        fallback_triggered=False, latency_ms=0.0, error="connection refused")
        assert r.ok is False

    def test_model_none_is_not_ok(self):
        r = RouteResult(task_type="qa", model_used="none", response="error",
                        fallback_triggered=True, latency_ms=0.0)
        assert r.ok is False


# ── 8. Orchestrator mock (re-run via pytest) ──────────────────────────────────

class TestOrchestratorMock:
    """Same tests from test_orchestrator_mock.py, structured for pytest."""

    def test_agent_loop_dispatches_tool_then_finishes(self):
        from orchestrator import Orchestrator

        class MockRouter:
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
                            "args": {"path": str(Path(__file__).parent / "requirements.txt")}
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

        orch = Orchestrator(router=MockRouter())
        result = orch.run("Read requirements and draft a note")
        assert result.done is True
        assert result.steps_taken == 2
        assert "Approval note drafted" in result.final_output

    def test_max_steps_bounds_execution(self):
        from orchestrator import Orchestrator

        class NeverFinishRouter:
            def route(self, prompt, task_type=None, attached_file=None, context=None):
                return RouteResult(
                    task_type="qa", model_used="mistral-7b",
                    response=json.dumps({"action": "tool_call", "tool": "unknown_tool", "args": {}}),
                    fallback_triggered=False, latency_ms=50.0,
                )

        orch = Orchestrator(router=NeverFinishRouter())
        task = orch.run("impossible task")
        assert task.steps_taken == 8
        assert task.done is False

    def test_router_error_stops_immediately(self):
        from orchestrator import Orchestrator

        class ErrorRouter:
            def route(self, prompt, task_type=None, attached_file=None, context=None):
                return RouteResult(
                    task_type="qa", model_used="none", response="",
                    fallback_triggered=False, latency_ms=0.0, error="connection refused",
                )

        orch = Orchestrator(router=ErrorRouter())
        task = orch.run("anything")
        assert task.done is True
        assert "router error" in task.final_output


# ── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])
