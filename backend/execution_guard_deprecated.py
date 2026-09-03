"""
Stages 9 & 10: Execution Guard — Sovereign AI Workbench
- Stage 9: Tool Call Validator (schema checks, path traversal, payload limits)
- Stage 10: Resource Budget & Execution Limiter (step caps, timeout monitoring)
"""

from typing import Dict, Any, Optional, List, Tuple

# Hard resource limits (Stage 10)
MAX_STEPS = 15
MAX_ELAPSED_MS = 30000  # 30 seconds

# Suspicious path traversal signatures (Stage 9)
SUSPICIOUS_PATH_PATTERNS = [
    "../",
    "..\\",
    "/etc/",
    "/etc",
    "c:\\windows",
    "c:/windows",
    "/windows",
    "/system32"
]

# Max allowed string length for tool arguments
MAX_STRING_LENGTH = 10000

# Allowed tools schema registry (Stage 9)
ALLOWED_TOOLS: Dict[str, Dict[str, Any]] = {
    "run_calculation": {
        "description": "Execute mathematical calculations",
        "allowed_args": {"expression", "precision", "variables"}
    },
    "search_knowledge_base": {
        "description": "Query local vector database / RAG index",
        "allowed_args": {"query", "top_k", "collection", "threshold", "filter"}
    },
    "generate_document": {
        "description": "Generate output deliverable documents",
        "allowed_args": {"file_name", "format", "content", "title", "sheets", "template"}
    },
    # Core Agentic ReAct tools
    "analyze_requirements": {
        "description": "Parse and structure task requirements",
        "allowed_args": {"task_description", "context"}
    },
    "generate_code_skeleton": {
        "description": "Generate code scaffolding and structure",
        "allowed_args": {"language", "libraries", "schema"}
    },
    "implement_core_logic": {
        "description": "Implement core algorithmic solution",
        "allowed_args": {"method", "threshold", "algorithm"}
    },
    "add_error_handling": {
        "description": "Inject defensive error handling",
        "allowed_args": set()
    },
    "add_cli_interface": {
        "description": "Add CLI entry points and argument parsing",
        "allowed_args": set()
    },
    "validate_code_syntax": {
        "description": "Validate syntax and lint compliance",
        "allowed_args": set()
    },
    "execute_in_sandbox": {
        "description": "Execute code inside gVisor container sandbox",
        "allowed_args": {"language", "code", "timeout"}
    },
    "OCR_Tool": {
        "description": "Extract text and elements from visual inputs",
        "allowed_args": {"file", "mode", "extract"}
    },
    "extract_tables": {
        "description": "Extract structured tables from document",
        "allowed_args": {"document", "method"}
    },
    "classify_defects": {
        "description": "Classify defect records by category/severity",
        "allowed_args": {"table_data", "schema"}
    },
    "generate_excel": {
        "description": "Create formatted multi-sheet Excel spreadsheet",
        "allowed_args": {"sheets", "format", "style"}
    },
    "RAG_search": {
        "description": "Search local documents with similarity retrieval",
        "allowed_args": {"query", "k"}
    },
    "structure_response": {
        "description": "Structure raw chunks into formatted output",
        "allowed_args": {"source_chunks", "format"}
    },
    "extract_thresholds": {
        "description": "Extract policy thresholds and authority limits",
        "allowed_args": {"policy_sections"}
    },
    "format_final_response": {
        "description": "Format final markdown deliverable with citations",
        "allowed_args": {"citations", "format"}
    },
    "ChromaDB_query": {
        "description": "Query internal ChromaDB vector store",
        "allowed_args": {"collection", "query", "k", "threshold"}
    },
    "generate_answer": {
        "description": "Synthesize grounded answer from context",
        "allowed_args": {"context", "grounding", "citations"}
    },
    "verify_hallucination_check": {
        "description": "Verify claims against retrieved sources",
        "allowed_args": {"answer", "sources"}
    },
    "classify_and_aggregate": {
        "description": "Aggregate and group records",
        "allowed_args": {"data", "by"}
    }
}


def validate_tool_call(tool_name: str, tool_args: dict) -> Dict[str, Any]:
    """
    Stage 9: Tool Call Validator.
    Validates tool invocation against allowed schemas and checks for malicious patterns:
    - Path traversal attacks (../, /etc/, C:\\Windows)
    - Oversized payloads (> 10000 chars)
    - Unexpected/unauthorized arguments

    Args:
        tool_name: Identifier of the requested tool
        tool_args: Dictionary of keyword arguments provided to the tool

    Returns:
        dict: {"valid": bool, "reason": Optional[str]}
    """
    if tool_name not in ALLOWED_TOOLS:
        return {
            "valid": False,
            "reason": f"Unauthorized tool invocation: '{tool_name}' is not in allowed tools registry"
        }

    schema = ALLOWED_TOOLS[tool_name]
    allowed_args = schema.get("allowed_args", set())

    # Check for unexpected arguments
    unexpected = set(tool_args.keys()) - allowed_args
    if unexpected:
        return {
            "valid": False,
            "reason": f"Unexpected argument(s) for tool '{tool_name}': {', '.join(sorted(unexpected))}"
        }

    # Deep inspect values for path traversal and length limits
    def _inspect_value(arg_name: str, val: Any) -> Optional[str]:
        if isinstance(val, str):
            if len(val) > MAX_STRING_LENGTH:
                return f"Oversized string in argument '{arg_name}' ({len(val)} chars, limit {MAX_STRING_LENGTH})"
            val_lower = val.lower()
            for pattern in SUSPICIOUS_PATH_PATTERNS:
                if pattern in val_lower:
                    return f"Suspicious path traversal pattern detected in argument '{arg_name}': '{val}'"
        elif isinstance(val, dict):
            for sub_k, sub_v in val.items():
                err = _inspect_value(f"{arg_name}.{sub_k}", sub_v)
                if err:
                    return err
        elif isinstance(val, (list, tuple)):
            for idx, item in enumerate(val):
                err = _inspect_value(f"{arg_name}[{idx}]", item)
                if err:
                    return err
        return None

    for k, v in tool_args.items():
        err = _inspect_value(k, v)
        if err:
            return {
                "valid": False,
                "reason": err
            }

    return {
        "valid": True,
        "reason": None
    }


def check_resource_budget(step_count: int, elapsed_ms: int) -> Dict[str, Any]:
    """
    Stage 10: Resource Budget & Execution Limiter.
    Enforces maximum step limits (limit 15) and execution timeout (limit 30000ms).

    Args:
        step_count: Current number of ReAct loop iterations executed
        elapsed_ms: Total milliseconds elapsed since task start

    Returns:
        dict: {"within_budget": bool, "reason": Optional[str]}
    """
    if step_count > MAX_STEPS:
        return {
            "within_budget": False,
            "reason": f"Resource budget exceeded: {step_count} steps (limit {MAX_STEPS}) — possible infinite loop, task halted"
        }

    if elapsed_ms > MAX_ELAPSED_MS:
        return {
            "within_budget": False,
            "reason": f"Resource budget exceeded: {elapsed_ms}ms elapsed (limit {MAX_ELAPSED_MS}ms) — task timeout, task halted"
        }

    return {
        "within_budget": True,
        "reason": None
    }


def parse_action_call(action_str: str) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Parses action strings from ReAct loop into (tool_name, tool_args) tuples.
    Handles chained calls ('toolA() + toolB()'), keyword arguments, and identifier tokens.
    """
    calls = []
    current_call = []
    paren_depth = 0

    for char in action_str:
        if char == "(":
            paren_depth += 1
            current_call.append(char)
        elif char == ")":
            paren_depth = max(0, paren_depth - 1)
            current_call.append(char)
        elif char == "+" and paren_depth == 0:
            calls.append("".join(current_call).strip())
            current_call = []
        else:
            current_call.append(char)

    if current_call:
        calls.append("".join(current_call).strip())

    results = []
    for call in calls:
        call = call.strip()
        if not call:
            continue
        if "(" in call and call.endswith(")"):
            tool_name = call[:call.index("(")].strip()
            inside = call[call.index("(") + 1:-1].strip()
            args = {}
            if inside:
                try:
                    expr = f"dict({inside})"
                    evaluated = eval(expr, {"__builtins__": {}}, {})
                    if isinstance(evaluated, dict):
                        args = evaluated
                except Exception:
                    for item in inside.split(","):
                        item = item.strip()
                        if "=" in item:
                            k, v = item.split("=", 1)
                            args[k.strip()] = v.strip().strip("'\"")
                        elif item:
                            allowed = ALLOWED_TOOLS.get(tool_name, {}).get("allowed_args", set())
                            if item in allowed:
                                args[item] = item
                            elif allowed:
                                first_key = sorted(list(allowed))[0]
                                args[first_key] = item.strip("'\"")
                            else:
                                args[item] = item
            results.append((tool_name, args))
        else:
            results.append((call.strip(), {}))

    return results
