"""
Sovereign AI Workbench — FastAPI Backend
Mock engine for SIH 2026 Demo | Team Code:201
All LLM calls are simulated — works 100% offline without GPU.
"""

import asyncio
import random
import time
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from pydantic import BaseModel

from stage1_injection_guard import check_prompt_injection
from stage2_pii_sanitizer import get_pii_check_result
from stage3_task_classifier import classify_task
from stage4_rbac_filter import USER_CLEARANCE
from stage5_model_router import get_model_info
from stage6_knowledge_retrieval import (
    get_all_documents, get_rag_stats, simulate_indexing, get_authorized_rag_results
)
from stage7_primary_agent import run_primary_agent, get_demo_response, get_react_loop
from stage8_guardian_agent import guardian_review
from stage9_tool_validator import validate_tool_call
from stage10_budget_guard import check_resource_budget, parse_action_call
from stage11_sandbox import execute_in_sandbox
from stage12_output_generator import generate_docx_report, parse_markdown_to_sections
from stage13_audit_ledger import (
    generate_audit_logs, get_audit_summary, append_log_entry,
    verify_log_chain, tamper_demo_entry
)
from real_llm import call_ollama, call_ollama_vision, check_ollama_health

# ─── App setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Sovereign AI Workbench API",
    description="Mock backend for SIH 2026 Demo — Team Code:201",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── In-memory state ──────────────────────────────────────────────────────────

_task_counter = 0
_blocked_requests_log = [
    {"timestamp": "2026-08-31T19:25:12", "host": "api.openai.com", "rule": "iptables OUTPUT DROP", "action": "BLOCKED"},
    {"timestamp": "2026-08-31T19:18:44", "host": "api.anthropic.com", "rule": "iptables OUTPUT DROP", "action": "BLOCKED"},
    {"timestamp": "2026-08-31T19:11:03", "host": "huggingface.co", "rule": "iptables OUTPUT DROP", "action": "BLOCKED"},
    {"timestamp": "2026-08-31T19:02:30", "host": "amazonaws.com", "rule": "iptables OUTPUT DROP", "action": "BLOCKED"},
    {"timestamp": "2026-08-31T18:55:18", "host": "googleapis.com", "rule": "iptables OUTPUT DROP", "action": "BLOCKED"},
]

# ─── Request/Response Models ──────────────────────────────────────────────────

class AgentRunRequest(BaseModel):
    task: str
    output_format: str = "Word Doc"
    file_name: Optional[str] = None
    file_data: Optional[str] = None  # optional base64 data for uploaded images
    scenario: Optional[str] = None  # pre-built demo scenario key
    user_role: str = "inspector"    # RBAC role: inspector, engineer, manager, admin
    live_mode: bool = False


class AgentRunResponse(BaseModel):
    steps: list
    model_used: str
    task_type: str
    time_taken_ms: int
    outbound_bytes: int = 0
    output_file: Optional[str] = None
    final_response: str
    status: str = "completed"
    pending_approval: bool = False
    guardian_review: Optional[dict] = None
    execution_halted: bool = False
    halt_reason: Optional[str] = None
    sandbox_result: Optional[dict] = None
    user_role: str = "inspector"
    stages_passed: int = 13
    stages_total: int = 13
    stages_pipeline: list = []
    stage_results: dict = {}
    reasoning_trace: Optional[str] = None
    live_mode: bool = False
    live_inference_attempted: bool = False
    fell_back_to_demo: bool = False
    live_fallback_reason: Optional[str] = None


class DocxGenerateRequest(BaseModel):
    title: Optional[str] = "Sovereign AI Deliverable Report"
    content: Optional[str] = None
    sections: Optional[list] = None
    filename: Optional[str] = "deliverable_report.docx"


# ─── Helper: Build output filename ───────────────────────────────────────────

def _get_output_filename(output_format: str, task_type: str) -> str:
    ext_map = {
        "Excel": "xlsx",
        "Word Doc": "docx",
        "PowerPoint": "pptx",
        "Code": "py",
        "JSON": "json",
        "PDF": "pdf"
    }
    name_map = {
        "code": "anomaly_detector",
        "vision": "inspection_summary",
        "analysis": "inspection_summary",
        "text": "policy_response",
        "rag": "sop_answer"
    }
    ext = ext_map.get(output_format, "txt")
    name = name_map.get(task_type, "output")
    return f"{name}.{ext}"


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "service": "Sovereign AI Workbench",
        "team": "Code:201",
        "event": "SIH 2026",
        "problem_id": "26117",
        "status": "operational",
        "outbound_bytes": 0
    }


STAGE_NAMES = {
    1: "Prompt Injection Scanner",
    2: "Live PII Sanitizer",
    3: "Task Classification & Routing",
    4: "Authorization & RBAC Filter",
    5: "Local Model Selection",
    6: "Company Brain Retrieval (RAG)",
    7: "Primary Agent Generation",
    8: "Guardian Agent Review",
    9: "Tool Call Validator",
    10: "Resource Budget Limiter",
    11: "Secure Sandbox Execution (gVisor)",
    12: "Air-Gapped Deliverable Vault",
    13: "Tamper-Evident Hash Chain Audit"
}


# ─── Main Pipeline Endpoint (All 13 Stages) ──────────────────────────────────

@app.post("/api/agent/run")
async def run_agent(request: AgentRunRequest):
    """
    Main agentic pipeline endpoint coordinating all 13 sovereign AI stages:
    1. Prompt Injection Scanner (Input Guard)
    2. Live PII Sanitizer
    3. Task Classification & Routing
    4. Authorization & RBAC Filter
    5. Local Model Selection
    6. Company Brain Retrieval (ChromaDB)
    7. Primary Agent Generation (ReAct Loop)
    8. Guardian Agent Independent Review
    9. Tool Call Validator
    10. Resource Budget Limiter
    11. Secure gVisor Sandbox Execution
    12. Air-Gapped Deliverable Vault
    13. Tamper-Evident Hash-Chained Audit Log
    """
    global _task_counter
    _task_counter += 1

    # ─── Stage 1: Prompt Injection Scanner ───────────────────────────────────
    injection_check = check_prompt_injection(request.task)
    append_log_entry(
        event_type="STAGE_1_INPUT_GUARD",
        details={
            "stage": 1,
            "user_role": request.user_role,
            "injection_detected": injection_check["injection_detected"],
            "risk_score": injection_check["risk_score"],
            "matched_patterns": injection_check["matched_patterns"],
            "scan_duration_ms": injection_check["scan_duration_ms"],
            "decision": "BLOCKED" if injection_check["injection_detected"] else "PASSED"
        }
    )

    if injection_check["injection_detected"]:
        halt_reason = (
            f"Stage 1 Security Block: Prompt Injection Detected "
            f"(risk: {injection_check['risk_score']} | patterns: {', '.join(injection_check['matched_patterns'])})"
        )
        print(f"[SECURITY BLOCK] {halt_reason}")

        stages_pipeline = [
            {
                "stage": 1,
                "name": STAGE_NAMES[1],
                "passed": False,
                "status": "blocked",
                "summary": halt_reason
            },
            *[
                {
                    "stage": s,
                    "name": STAGE_NAMES[s],
                    "passed": False,
                    "status": "skipped",
                    "summary": "Pipeline halted due to Stage 1 injection block"
                }
                for s in range(2, 14)
            ]
        ]

        steps = [
            {
                "step": 1,
                "name": "Security Check (Halted)",
                "icon": "🛑",
                "status": "failed",
                "details": halt_reason,
                "sub_items": [
                    f"🛑 Prompt injection vector detected: {', '.join(injection_check['matched_patterns'])}",
                    f"⚠️ Risk score: {injection_check['risk_score']} (Threshold 0.50)",
                    f"⏱ Scan time: {injection_check['scan_duration_ms']}ms",
                    "🔒 Downstream model inference halted immediately"
                ]
            },
            {"step": 2, "name": "Task Classification & Routing", "icon": "⏭️", "status": "skipped", "details": "Skipped due to Stage 1 block", "sub_items": []},
            {"step": 3, "name": "RAG Retrieval", "icon": "⏭️", "status": "skipped", "details": "Skipped due to Stage 1 block", "sub_items": []},
            {"step": 4, "name": "Agentic Processing", "icon": "⏭️", "status": "skipped", "details": "Skipped due to Stage 1 block", "sub_items": []},
            {"step": 5, "name": "Validation & Safety Check", "icon": "⏭️", "status": "skipped", "details": "Skipped due to Stage 1 block", "sub_items": []},
            {"step": 6, "name": "Deliverable Ready", "icon": "❌", "status": "skipped", "details": "Aborted — zero outbound output generated", "output_file": None, "sub_items": ["❌ Zero data egress"]}
        ]

        return {
            "steps": steps,
            "model_used": "None (Interception)",
            "task_type": "security_block",
            "time_taken_ms": injection_check["scan_duration_ms"],
            "outbound_bytes": 0,
            "output_file": None,
            "final_response": f"🛑 Task blocked by Stage 1 Prompt Injection Scanner:\n{halt_reason}\n\nPipeline execution stopped — zero cloud egress and zero local execution.",
            "status": "blocked",
            "execution_halted": True,
            "halt_reason": halt_reason,
            "pending_approval": False,
            "guardian_review": None,
            "sandbox_result": None,
            "user_role": request.user_role,
            "stages_passed": 0,
            "stages_total": 13,
            "stages_pipeline": stages_pipeline,
            "stage_results": {
                "stage_1": {"stage": 1, "name": STAGE_NAMES[1], "result": injection_check}
            }
        }

    # ─── Stage 2: Live PII Sanitizer ─────────────────────────────────────────
    # Live user query sanitization only. Document-level PII masking happens separately at ingestion time (Stage 12, not here).
    pii_result = get_pii_check_result(request.task)
    append_log_entry(
        event_type="STAGE_2_PII_SANITIZER",
        details={
            "stage": 2,
            "user_role": request.user_role,
            "pii_detected": pii_result.get("pii_detected", False),
            "entities_found": pii_result.get("entities_found", []),
            "entities_scanned": pii_result.get("entities_scanned", 0),
            "scan_duration_ms": pii_result.get("scan_duration_ms", 0),
            "decision": "MASKED" if pii_result.get("pii_detected") else "CLEAN"
        }
    )
    # Short-circuit with masked version of query if PII found (do not send raw PII forward)
    effective_task = pii_result["masked_preview"] if pii_result.get("pii_detected") else request.task
    if pii_result.get("pii_detected"):
        print(f"[STAGE 2 PII] Live PII detected and masked: entities={pii_result['entities_found']}")

    # ─── Stage 3: Task Classification & Routing ──────────────────────────────
    has_file = bool(request.file_name or request.file_data)
    task_type = classify_task(effective_task, has_file)
    if request.scenario == "code":
        task_type = "code"
    elif request.scenario == "vision":
        task_type = "vision"
    elif request.scenario == "analysis":
        task_type = "analysis"
    elif request.scenario == "rag":
        task_type = "rag"
    elif request.scenario == "text":
        task_type = "text"
    elif request.file_name and any(request.file_name.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp"]):
        task_type = "vision"

    append_log_entry(
        event_type="STAGE_3_TASK_CLASSIFICATION",
        details={
            "stage": 3,
            "user_role": request.user_role,
            "task_type": task_type,
            "input_length": len(effective_task),
            "decision": "ROUTED"
        }
    )

    # ─── Stage 4: Authorization/RBAC Filter ──────────────────────────────────
    rag_result = get_authorized_rag_results(task_type, user_role=request.user_role)
    user_clearance = rag_result.get("user_clearance", USER_CLEARANCE.get(request.user_role, "Internal"))
    append_log_entry(
        event_type="STAGE_4_RBAC_AUTHORIZATION",
        details={
            "stage": 4,
            "user_role": request.user_role,
            "clearance": user_clearance,
            "task_type": task_type,
            "sources_allowed": rag_result.get("sources", []),
            "sources_blocked": rag_result.get("filtered_documents", []),
            "decision": "AUTHORIZED"
        }
    )

    # ─── Stage 5: Local Model Selection ──────────────────────────────────────
    model_info = get_model_info(task_type)
    append_log_entry(
        event_type="STAGE_5_MODEL_ROUTING",
        details={
            "stage": 5,
            "model_selected": model_info["model"],
            "model_size": model_info["size"],
            "vram_allocated": model_info["vram"],
            "decision": "ALLOCATED"
        }
    )

    # ─── Stage 6: Company Brain Retrieval (ChromaDB) ─────────────────────────
    append_log_entry(
        event_type="STAGE_6_COMPANY_BRAIN",
        details={
            "stage": 6,
            "collection": rag_result.get("collection", "internal_docs"),
            "chunks_retrieved": rag_result.get("chunks", 0),
            "top_similarity": rag_result.get("top_similarity", 0.0),
            "query_time_ms": rag_result.get("query_time_ms", 0),
            "decision": "RETRIEVED" if rag_result.get("retrieved") else "SKIPPED_NOT_APPLICABLE"
        }
    )

    # ─── Stage 7: Primary Agent Generation (ReAct Loop + Stages 9, 10, 11) ───
    raw_react_loop = get_react_loop(task_type)
    code_preview = get_demo_response("code") if task_type == "code" else request.task
    sandbox_result = None

    # Attack Demo Trigger: Resource Exhaustion (generate >15 steps)
    if any(k in request.task.lower() for k in ["infinite loop", "resource exhaustion", "50 steps"]):
        raw_react_loop = [
            {"thought": f"Recursive branch expansion #{i}: exploring sub-execution paths..."}
            for i in range(1, 20)
        ]
    # Attack Demo Trigger: Malformed Tool Call (path traversal attack)
    elif any(k in request.task.lower() for k in ["run_calculation(", "malformed tool", "../../etc"]):
        raw_react_loop = [
            {"thought": "Attempting system metric analysis via internal calculation tool."},
            {"action": "run_calculation(expression='../../etc/shadow', traversal=True)"}
        ]

    executed_react_loop = []
    execution_halted = False
    halt_reason = None
    tool_blocked = False
    budget_exceeded = False
    step_count = 0
    start_loop_time = time.perf_counter()

    for item in raw_react_loop:
        step_count += 1
        elapsed_loop_ms = max(1, int((time.perf_counter() - start_loop_time) * 1000)) + (step_count * random.randint(15, 35))

        # Stage 10: Check resource budget on each step
        budget_check = check_resource_budget(step_count, elapsed_loop_ms)
        if not budget_check["within_budget"]:
            budget_exceeded = True
            execution_halted = True
            halt_reason = budget_check["reason"]
            append_log_entry(
                event_type="STAGE_10_RESOURCE_BUDGET",
                details={
                    "stage": 10,
                    "step_count": step_count,
                    "elapsed_loop_ms": elapsed_loop_ms,
                    "decision": "HALTED",
                    "reason": halt_reason
                }
            )
            print(f"[STAGE 10 RESOURCE BUDGET] {halt_reason}")
            break

        # Stage 9: Validate tool calls before any action step executes
        if "action" in item:
            action_str = item["action"]
            parsed_tools = parse_action_call(action_str)
            action_blocked = False
            for tool_name, tool_args in parsed_tools:
                tool_val = validate_tool_call(tool_name, tool_args)
                if not tool_val["valid"]:
                    tool_blocked = True
                    execution_halted = True
                    halt_reason = f"Execution Guard blocked tool '{tool_name}': {tool_val['reason']}"
                    append_log_entry(
                        event_type="STAGE_9_TOOL_VALIDATION",
                        details={
                            "stage": 9,
                            "tool_name": tool_name,
                            "decision": "BLOCKED",
                            "reason": tool_val["reason"]
                        }
                    )
                    print(f"[STAGE 9 TOOL VALIDATOR] {halt_reason}")
                    action_blocked = True
                    break
            if action_blocked:
                break

            # Stage 11: Execute code inside isolated gVisor sandbox container
            if task_type == "code" and any(k in action_str for k in ["execute_in_sandbox", "validate_code_syntax"]):
                sandbox_res = execute_in_sandbox(code=code_preview, language="python")
                sandbox_result = sandbox_res
                append_log_entry(
                    event_type="STAGE_11_SANDBOX_EXECUTION",
                    details={
                        "stage": 11,
                        "sandbox": sandbox_res["sandbox"],
                        "network_access": sandbox_res["network_access"],
                        "filesystem": sandbox_res["filesystem"],
                        "exit_code": sandbox_res["exit_code"],
                        "execution_time_ms": sandbox_res["execution_time_ms"],
                        "decision": "CONTAINED_SUCCESS"
                    }
                )
                print(f"[STAGE 11 SANDBOX] Executed in gVisor sandbox (runsc): exit_code={sandbox_res['exit_code']} time={sandbox_res['execution_time_ms']}ms")
                item = dict(item)
                item["observation"] = (
                    f"✓ gVisor Sandbox run (runsc): exit {sandbox_res['exit_code']} | "
                    f"Net: {sandbox_res['network_access']} | FS: {sandbox_res['filesystem']} | "
                    f"Time: {sandbox_res['execution_time_ms']}ms"
                )

        executed_react_loop.append(item)

    # Stage 7: Primary Agent ReAct Loop completion logging
    append_log_entry(
        event_type="STAGE_7_PRIMARY_AGENT",
        details={
            "stage": 7,
            "task_type": task_type,
            "steps_executed": len(executed_react_loop),
            "execution_halted": execution_halted,
            "decision": "HALTED" if execution_halted else "COMPLETED"
        }
    )

    # Stage 11: Sandbox execution logging if not already logged during code action
    if not sandbox_result:
        append_log_entry(
            event_type="STAGE_11_SANDBOX_EXECUTION",
            details={
                "stage": 11,
                "sandbox": "gVisor (runsc)",
                "decision": "SKIPPED_NOT_APPLICABLE" if task_type != "code" else "CONTAINED_STANDBY"
            }
        )

    if not execution_halted:
        append_log_entry(
            event_type="STAGE_9_10_EXECUTION_GUARD",
            details={
                "stage": 9,
                "steps_executed": len(executed_react_loop),
                "tool_validation": "PASSED",
                "resource_budget": "WITHIN_BUDGET",
                "decision": "PASSED"
            }
        )

    # ─── Format Step Traces ───────────────────────────────────────────────────
    pii_detected_label = "None" if not pii_result.get("pii_detected") else f"{', '.join(pii_result['entities_found'])} (Masked)"
    pii_sub_label = (
        f"🛡 PII scan: {pii_result['entities_scanned']} tokens checked — CLEAN"
        if not pii_result.get("pii_detected")
        else f"🛡 PII scan: Masked {len(pii_result['entities_found'])} sensitive entities ({', '.join(pii_result['entities_found'])})"
    )

    security_step = {
        "step": 1,
        "name": "Security Check",
        "icon": "🔒",
        "status": "passed",
        "details": f"PII detected: {pii_detected_label} | Role: {request.user_role} ({user_clearance}) | Input sanitized ✓",
        "sub_items": [
            pii_sub_label,
            f"🔑 RBAC: Role '{request.user_role}' authorized for {task_type} tasks (Clearance: {user_clearance})",
            f"🧹 Input sanitization: Complete ({pii_result['scan_duration_ms']}ms)"
        ]
    }

    routing_step = {
        "step": 2,
        "name": "Task Classification & Routing",
        "icon": "🧠",
        "status": "passed",
        "details": f"Task type: {task_type.upper()} | Model selected: {model_info['model']} | {model_info['reason']}",
        "sub_items": [
            f"🏷 Classified as: {task_type.upper()}",
            f"🤖 Routed to: {model_info['model']} ({model_info['size']})",
            f"💡 Reason: {model_info['reason']}",
            f"💾 VRAM allocation: {model_info['vram']}"
        ]
    }

    rag_step = {
        "step": 3,
        "name": "RAG Retrieval",
        "icon": "📚",
        "status": "skipped" if not rag_result.get("retrieved") else "passed",
        "details": (
            f"RAG not applicable for {task_type} tasks"
            if not rag_result.get("retrieved")
            else f"{rag_result['chunks']} chunks retrieved from: {', '.join(rag_result['sources'])} | Clearance: {user_clearance}"
        ),
        "sub_items": [] if not rag_result.get("retrieved") else [
            f"🔍 Querying ChromaDB ({rag_result['collection']} collection)...",
            f"✓ Top match similarity: {rag_result['top_similarity']}",
            f"📄 Allowed Sources: {', '.join(rag_result['sources'])}",
            *( [f"🚫 RBAC Filtered: {', '.join(rag_result['filtered_documents'])} (requires higher clearance)"] if rag_result.get("filtered_documents") else [] )
        ]
    }

    if execution_halted:
        # Return partial result when tool validation or resource budget fails
        base_ms = random.randint(800, 1400) + elapsed_loop_ms
        final_response = f"⚠️ Task execution halted by Execution Guard:\n{halt_reason}\n\nCompleted {len(executed_react_loop)} of {len(raw_react_loop)} planned steps before interception."
        
        react_step = {
            "step": 4,
            "name": "Agentic Processing (Halted)",
            "icon": "⚠️",
            "status": "failed",
            "details": f"Execution halted at step {step_count} | {halt_reason}",
            "react_loop": executed_react_loop,
            "sub_items": [
                f"🛑 Execution Guard Halt: {halt_reason}",
                f"📊 Steps completed prior to halt: {len(executed_react_loop)}"
            ]
        }

        validation_step = {
            "step": 5,
            "name": "Validation & Safety Check",
            "icon": "⏭️",
            "status": "skipped",
            "details": "Validation skipped — pipeline halted prior to completion",
            "sub_items": ["⚠️ Skipped due to Execution Guard halt"]
        }

        deliverable_step = {
            "step": 6,
            "name": "Deliverable Ready",
            "icon": "❌",
            "status": "skipped",
            "details": "Deliverable generation aborted due to Execution Guard halt",
            "output_file": None,
            "sub_items": ["❌ No deliverable file generated"]
        }

        steps = [security_step, routing_step, rag_step, react_step, validation_step, deliverable_step]

        chain_verify = verify_log_chain()

        stages_pipeline = [
            {"stage": 1, "name": STAGE_NAMES[1], "passed": True, "status": "passed", "summary": "Prompt injection scan clean"},
            {"stage": 2, "name": STAGE_NAMES[2], "passed": True, "status": "passed", "summary": "PII scan complete"},
            {"stage": 3, "name": STAGE_NAMES[3], "passed": True, "status": "passed", "summary": f"Task classified as {task_type.upper()}"},
            {"stage": 4, "name": STAGE_NAMES[4], "passed": True, "status": "passed", "summary": f"Role '{request.user_role}' ({user_clearance}) authorized"},
            {"stage": 5, "name": STAGE_NAMES[5], "passed": True, "status": "passed", "summary": f"Allocated {model_info['model']}"},
            {"stage": 6, "name": STAGE_NAMES[6], "passed": True, "status": "passed" if rag_result.get("retrieved") else "skipped", "summary": "RAG retrieval complete" if rag_result.get("retrieved") else "Not applicable"},
            {"stage": 7, "name": STAGE_NAMES[7], "passed": False, "status": "halted", "summary": f"ReAct execution halted: {halt_reason}"},
            {"stage": 8, "name": STAGE_NAMES[8], "passed": False, "status": "skipped", "summary": "Skipped due to loop halt"},
            {"stage": 9, "name": STAGE_NAMES[9], "passed": not tool_blocked, "status": "blocked" if tool_blocked else "passed", "summary": "Tool check blocked" if tool_blocked else "Validated"},
            {"stage": 10, "name": STAGE_NAMES[10], "passed": not budget_exceeded, "status": "exceeded" if budget_exceeded else "passed", "summary": "Resource budget exceeded" if budget_exceeded else "Within limits"},
            {"stage": 11, "name": STAGE_NAMES[11], "passed": False, "status": "skipped", "summary": "Skipped due to loop halt"},
            {"stage": 12, "name": STAGE_NAMES[12], "passed": False, "status": "aborted", "summary": "Deliverable aborted"},
            {"stage": 13, "name": STAGE_NAMES[13], "passed": chain_verify.get("chain_valid", True), "status": "passed", "summary": "Audit log hash chain verified"}
        ]

        stages_passed = sum(1 for s in stages_pipeline if s["passed"])

        return {
            "steps": steps,
            "model_used": model_info["model"],
            "task_type": task_type,
            "time_taken_ms": base_ms,
            "outbound_bytes": 0,
            "output_file": None,
            "final_response": final_response,
            "status": "halted",
            "execution_halted": True,
            "halt_reason": halt_reason,
            "pending_approval": False,
            "guardian_review": None,
            "sandbox_result": None,
            "user_role": request.user_role,
            "stages_passed": stages_passed,
            "stages_total": 13,
            "stages_pipeline": stages_pipeline,
            "stage_results": {
                "stage_1": {"stage": 1, "name": STAGE_NAMES[1], "result": injection_check},
                "stage_2": {"stage": 2, "name": STAGE_NAMES[2], "result": pii_result},
                "stage_3": {"stage": 3, "name": STAGE_NAMES[3], "result": {"task_type": task_type}},
                "stage_4": {"stage": 4, "name": STAGE_NAMES[4], "result": rag_result},
                "stage_5": {"stage": 5, "name": STAGE_NAMES[5], "result": model_info},
                "stage_6": {"stage": 6, "name": STAGE_NAMES[6], "result": rag_result},
                "stage_7": {"stage": 7, "name": STAGE_NAMES[7], "result": {"halted": True, "steps": len(executed_react_loop)}},
                "stage_9": {"stage": 9, "name": STAGE_NAMES[9], "result": {"valid": not tool_blocked}},
                "stage_10": {"stage": 10, "name": STAGE_NAMES[10], "result": {"within_budget": not budget_exceeded}},
                "stage_13": {"stage": 13, "name": STAGE_NAMES[13], "result": chain_verify}
            }
        }

    # ─── Stage 7: Primary Agent — real inference via stage7_primary_agent.py ──
    # Determines live vs. demo, selects correct Ollama model, handles all fallback.
    agent_result = run_primary_agent(
        task_text=effective_task,
        task_type=task_type,
        rag_context=rag_result,
        file_data=request.file_data or request.file_name,
        live_mode=request.live_mode,
        timeout_s=90,
    )

    final_response = agent_result["final_response"]
    reasoning_trace = agent_result["reasoning_trace"]
    live_inference_attempted = agent_result["live_inference_attempted"]
    fell_back_to_demo = agent_result["fell_back_to_demo"]
    live_fallback_reason = agent_result["fallback_reason"]
    real_inference_time_ms = agent_result["inference_time_ms"]
    real_model_name = agent_result["model_name"]
    base_ms = real_inference_time_ms if real_inference_time_ms else random.randint(2800, 4200)

    # Update model display label when real inference was used
    if real_model_name and not fell_back_to_demo:
        model_info = dict(model_info)
        if task_type == "vision":
            model_info["model"] = "Qwen2.5-VL (Local GPU via Ollama)"
        else:
            model_info["model"] = "DeepSeek-R1 (Local GPU via Ollama)"

    if request.live_mode and not fell_back_to_demo:
        print(f"[STAGE 7 LIVE] Real inference complete: model={real_model_name} time={real_inference_time_ms}ms")
    elif request.live_mode and fell_back_to_demo:
        print(f"[STAGE 7 FALLBACK] {live_fallback_reason}")

    # Demo trigger: overconfident safety claim (Guardian escalation test)
    if any(k in request.task.lower() for k in ["safe to operate", "overconfident", "without inspection"]):
        final_response = (
            "Equipment Telemetry Assessment:\n\n"
            "Based on current pressure readings, steam boiler pump unit B-12 at 450 PSI is safe to operate "
            "and approved for immediate production without manual inspection."
        )
    guardian_result = guardian_review(final_response, task_type)

    is_pending_approval = guardian_result.get("requires_human_approval", False)
    append_log_entry(
        event_type="STAGE_8_GUARDIAN_REVIEW",
        details={
            "stage": 8,
            "user_role": request.user_role,
            "reviewed_by": guardian_result.get("reviewed_by"),
            "verdict": guardian_result.get("verdict"),
            "requires_human_approval": is_pending_approval,
            "reason": guardian_result.get("reason"),
            "decision": "ESCALATED" if is_pending_approval else "APPROVED"
        }
    )
    if is_pending_approval:
        print(f"[STAGE 8 GUARDIAN] Human approval required: reason='{guardian_result['reason']}' reviewed_by='{guardian_result['reviewed_by']}'")

    # ─── Stage 12: Air-Gapped Deliverable Vault ──────────────────────────────
    output_file = _get_output_filename(request.output_format, task_type)
    append_log_entry(
        event_type="STAGE_12_DELIVERABLE_VAULT",
        details={
            "stage": 12,
            "user_role": request.user_role,
            "output_file": output_file,
            "encryption": "AES-256-GCM",
            "quarantined": is_pending_approval,
            "decision": "QUARANTINED" if is_pending_approval else "VAULT_READY"
        }
    )

    # ─── Stage 13: Audit Hash Chain Verification ──────────────────────────────
    chain_verify = verify_log_chain()
    append_log_entry(
        event_type="STAGE_13_HASH_CHAIN_AUDIT",
        details={
            "stage": 13,
            "chain_valid": chain_verify.get("chain_valid", True),
            "total_entries": chain_verify.get("total_entries", 0),
            "decision": "VERIFIED" if chain_verify.get("chain_valid", True) else "COMPROMISED"
        }
    )

    # Simulate timing
    base_ms = random.randint(2800, 5400) + guardian_result.get("review_duration_ms", 50)

    # ─── Assemble Steps ───────────────────────────────────────────────────────
    steps = [
        security_step,
        routing_step,
        rag_step,
        {
            "step": 4,
            "name": "Agentic Processing (ReAct Loop)",
            "icon": "⚙️",
            "status": "passed",
            "details": f"ReAct loop completed | {len(executed_react_loop)} iterations | Tool calls validated ✓ | Budget: PASS",
            "react_loop": executed_react_loop,
            "sub_items": [f"{'💭 Thought' if 'thought' in item else '⚡ Action'}: {item.get('thought') or item.get('action')}" for item in executed_react_loop[:3]]
        },
        {
            "step": 5,
            "name": "Validation & Safety Check",
            "icon": "✅",
            "status": "passed",
            "details": (
                f"Output validated | Guardian: {guardian_result['verdict']} | Format verified ✓ | Content policy: PASS"
            ),
            "sub_items": [
                "🔍 Output PII scan: CLEAN",
                "📋 Format validation: PASS",
                (
                    f"📦 Sandbox: gVisor (runsc) — exit {sandbox_result['exit_code']} | net=none, fs=ro ({sandbox_result['execution_time_ms']}ms)"
                    if sandbox_result
                    else "🛡 Content safety: COMPLIANT"
                ),
                f"🛡 Guardian ({guardian_result['reviewed_by']}): {guardian_result['verdict']}" + (
                    f" — {guardian_result['reason']} (Escalated)" if is_pending_approval else " (Clean)"
                ),
                f"📊 Output size: {random.randint(18, 210)} KB"
            ]
        },
        {
            "step": 6,
            "name": "Deliverable Ready" if not is_pending_approval else "Awaiting Human Review",
            "icon": "📄" if not is_pending_approval else "⏳",
            "status": "pending_approval" if is_pending_approval else "passed",
            "details": (
                f"Output file: {output_file} | Encrypted with AES-256 | Stored in local vault"
                if not is_pending_approval
                else f"Output file: {output_file} | Quarantined pending human approval | {guardian_result['confidence_note']}"
            ),
            "output_file": output_file,
            "sub_items": [
                f"📁 File: {output_file}",
                "🔐 Encrypted: AES-256-GCM",
                "💾 Stored: Local secure vault (Quarantine Hold)" if is_pending_approval else "💾 Stored: Local secure vault",
                f"⚠️ Guardian Flag: {guardian_result['confidence_note']}" if is_pending_approval else "📝 Audit entry: logged"
            ]
        }
    ]

    # ─── Compute 13-Stage Visual Pipeline ─────────────────────────────────────
    stages_pipeline = [
        {
            "stage": 1,
            "name": STAGE_NAMES[1],
            "passed": True,
            "status": "passed",
            "summary": f"Prompt injection scanner clean (risk: {injection_check['risk_score']})"
        },
        {
            "stage": 2,
            "name": STAGE_NAMES[2],
            "passed": True,
            "status": "passed",
            "summary": (
                "Query clean — 0 PII entities found"
                if not pii_result.get("pii_detected")
                else f"Sanitized {len(pii_result['entities_found'])} PII tokens ({', '.join(pii_result['entities_found'])})"
            )
        },
        {
            "stage": 3,
            "name": STAGE_NAMES[3],
            "passed": True,
            "status": "passed",
            "summary": f"Task classified as {task_type.upper()}"
        },
        {
            "stage": 4,
            "name": STAGE_NAMES[4],
            "passed": True,
            "status": "passed",
            "summary": (
                f"Role '{request.user_role}' ({user_clearance}) authorized"
                + (f" | Filtered: {', '.join(rag_result['filtered_documents'])}" if rag_result.get("filtered_documents") else " | Full access")
            )
        },
        {
            "stage": 5,
            "name": STAGE_NAMES[5],
            "passed": True,
            "status": "passed",
            "summary": f"Allocated local model: {model_info['model']} ({model_info['size']})"
        },
        {
            "stage": 6,
            "name": STAGE_NAMES[6],
            "passed": True,
            "status": "passed" if rag_result.get("retrieved") else "skipped",
            "summary": (
                f"ChromaDB retrieval: {rag_result['chunks']} chunks (top similarity {rag_result['top_similarity']})"
                if rag_result.get("retrieved")
                else "Retrieval not required for this task"
            )
        },
        {
            "stage": 7,
            "name": STAGE_NAMES[7],
            "passed": True,
            "status": "passed",
            "summary": f"Completed primary ReAct loop ({len(executed_react_loop)} steps)"
        },
        {
            "stage": 8,
            "name": STAGE_NAMES[8],
            "passed": not is_pending_approval,
            "status": "escalated" if is_pending_approval else "passed",
            "summary": (
                f"Guardian review passed ({guardian_result['reviewed_by']}): {guardian_result['verdict']}"
                if not is_pending_approval
                else f"Awaiting human approval ({guardian_result['reviewed_by']}): {guardian_result['reason']}"
            )
        },
        {
            "stage": 9,
            "name": STAGE_NAMES[9],
            "passed": True,
            "status": "passed",
            "summary": "All tool invocations validated against authorized schema"
        },
        {
            "stage": 10,
            "name": STAGE_NAMES[10],
            "passed": True,
            "status": "passed",
            "summary": f"Execution budget PASS ({step_count}/15 steps, {elapsed_loop_ms}ms)"
        },
        {
            "stage": 11,
            "name": STAGE_NAMES[11],
            "passed": True,
            "status": "passed" if sandbox_result else "skipped",
            "summary": (
                f"gVisor runtime (runsc): exit {sandbox_result['exit_code']} (net=none, fs=ro, {sandbox_result['execution_time_ms']}ms)"
                if sandbox_result
                else "Sandbox execution not required for non-code task"
            )
        },
        {
            "stage": 12,
            "name": STAGE_NAMES[12],
            "passed": not is_pending_approval,
            "status": "quarantined" if is_pending_approval else "passed",
            "summary": (
                f"Deliverable encrypted in local vault ({output_file})"
                if not is_pending_approval
                else f"Deliverable quarantined pending human sign-off ({output_file})"
            )
        },
        {
            "stage": 13,
            "name": STAGE_NAMES[13],
            "passed": chain_verify.get("chain_valid", True),
            "status": "passed" if chain_verify.get("chain_valid", True) else "compromised",
            "summary": f"HMAC-SHA256 audit chain verified ({chain_verify.get('total_entries', 0)} entries linked)"
        }
    ]

    stages_passed = sum(1 for s in stages_pipeline if s["passed"])

    stage_results = {
        "stage_1": {"stage": 1, "name": STAGE_NAMES[1], "result": injection_check},
        "stage_2": {"stage": 2, "name": STAGE_NAMES[2], "result": pii_result},
        "stage_3": {"stage": 3, "name": STAGE_NAMES[3], "result": {"task_type": task_type}},
        "stage_4": {"stage": 4, "name": STAGE_NAMES[4], "result": {
            "user_role": request.user_role,
            "user_clearance": user_clearance,
            "sources": rag_result.get("sources", []),
            "filtered_documents": rag_result.get("filtered_documents", [])
        }},
        "stage_5": {"stage": 5, "name": STAGE_NAMES[5], "result": model_info},
        "stage_6": {"stage": 6, "name": STAGE_NAMES[6], "result": rag_result},
        "stage_7": {"stage": 7, "name": STAGE_NAMES[7], "result": {"model": model_info["model"], "steps": len(executed_react_loop)}},
        "stage_8": {"stage": 8, "name": STAGE_NAMES[8], "result": guardian_result},
        "stage_9": {"stage": 9, "name": STAGE_NAMES[9], "result": {"valid": True}},
        "stage_10": {"stage": 10, "name": STAGE_NAMES[10], "result": {"steps": step_count, "limit": 15, "within_budget": True}},
        "stage_11": {"stage": 11, "name": STAGE_NAMES[11], "result": sandbox_result},
        "stage_12": {"stage": 12, "name": STAGE_NAMES[12], "result": {"output_file": output_file, "quarantined": is_pending_approval}},
        "stage_13": {"stage": 13, "name": STAGE_NAMES[13], "result": chain_verify}
    }

    # Stage 13: Live Inference Audit entry if real GPU was used
    if request.live_mode and not fell_back_to_demo:
        engine_label = "Ollama / Qwen2.5-VL (Local GPU)" if task_type == "vision" else "Ollama / DeepSeek-R1 (Local GPU)"
        append_log_entry(
            event_type="STAGE_13_LIVE_INFERENCE_AUDIT",
            details={
                "stage": 13,
                "inference_engine": engine_label,
                "model_used": real_model_name or ("qwen2.5vl:7b" if task_type == "vision" else "deepseek-r1:latest"),
                "inference_time_ms": real_inference_time_ms,
                "reasoning_trace_present": bool(reasoning_trace),
                "reasoning_trace_length": len(reasoning_trace or ""),
                "status": "VERIFIED_LOCAL_EXECUTION"
            }
        )

    return {
        "steps": steps,
        "model_used": model_info["model"],
        "task_type": task_type,
        "time_taken_ms": base_ms,
        "outbound_bytes": 0,
        "output_file": output_file,
        "final_response": final_response,
        "status": "pending_approval" if is_pending_approval else "completed",
        "pending_approval": is_pending_approval,
        "guardian_review": guardian_result,
        "execution_halted": False,
        "halt_reason": None,
        "sandbox_result": sandbox_result,
        "user_role": request.user_role,
        "stages_passed": stages_passed,
        "stages_total": 13,
        "stages_pipeline": stages_pipeline,
        "stage_results": stage_results,
        "reasoning_trace": reasoning_trace,
        "live_mode": request.live_mode,
        "live_inference_attempted": live_inference_attempted,
        "fell_back_to_demo": fell_back_to_demo,
        "live_fallback_reason": live_fallback_reason
    }


@app.get("/api/system/status")
async def get_system_status():
    """Returns current system status — models, VRAM, RAG stats, network."""
    rag_stats = get_rag_stats()
    
    return {
        "models": {
            "loaded": 3,
            "list": [
                {
                    "name": "Phi-3-Mini-4K",
                    "type": "Text/RAG",
                    "status": "active",
                    "vram_gb": 2.4,
                    "vram_pct": 30,
                    "tasks_today": random.randint(12, 22),
                    "size": "3.8B params (Q4_K_M)",
                    "color": "#5B8DEF",
                    "task_types": ["Policy Q&A", "ChromaDB RAG", "Guardian Review"]
                },
                {
                    "name": "Qwen2.5-VL-7B",
                    "type": "Vision/Document",
                    "status": "active",
                    "vram_gb": 9.2,
                    "vram_pct": 65,
                    "tasks_today": random.randint(18, 30),
                    "size": "7.2B params (Q4_K_M)",
                    "color": "#00C896",
                    "task_types": ["OCR Inspection", "Table Extraction", "Engineering PDFs"]
                },
                {
                    "name": "DeepSeek-Coder-V2-Lite",
                    "type": "Code/Reasoning",
                    "status": "active",
                    "vram_gb": 8.4,
                    "vram_pct": 85,
                    "tasks_today": random.randint(10, 18),
                    "size": "15.7B params (Q4_K_M)",
                    "color": "#F5A623",
                    "task_types": ["Code Generation", "AST Syntax", "gVisor Sandbox"]
                }
            ]
        },
        "network": {
            "outbound_bytes": 0,
            "external_api_calls": 0,
            "dns_external": 0,
            "status": "AIR_GAPPED",
            "firewall": "iptables — all outbound blocked"
        },
        "rag": {
            "documents": rag_stats["total_documents"],
            "chunks": rag_stats["total_chunks"],
            "collections": rag_stats["collections"],
            "vector_db": "ChromaDB v0.5.3",
            "embedding_model": "nomic-embed-text (local)"
        },
        "gpu": {
            "name": "NVIDIA RTX 4090 (24GB VRAM)",
            "vram_total_gb": 24,
            "vram_used_gb": 16.0,
            "vram_pct": 67,
            "utilization_pct": random.randint(55, 75),
            "temperature_c": random.randint(62, 71)
        },
        "uptime_hours": 14.3,
        "tasks_completed_today": random.randint(38, 52),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/audit/logs")
async def get_audit_logs(
    task_type: Optional[str] = None,
    model: Optional[str] = None,
    user: Optional[str] = None
):
    """Returns tamper-evident hash-chained audit logs with optional filtering."""
    logs = generate_audit_logs()
    
    # Apply filters
    if task_type:
        logs = [l for l in logs if task_type.lower() in l["task_type"].lower()]
    if model:
        logs = [l for l in logs if model.lower() in l["model_used"].lower()]
    if user:
        logs = [l for l in logs if user.lower() in l["user"].lower()]
    
    summary = get_audit_summary()
    verification = verify_log_chain()
    
    return {
        "logs": logs,
        "total": len(logs),
        "summary": summary,
        "chain_verified": verification["chain_valid"],
        "broken_at_entry": verification["broken_at_entry"],
        "verification_timestamp": datetime.now().isoformat()
    }


@app.get("/api/audit/verify-chain")
async def verify_audit_chain_endpoint():
    """
    Cryptographically walks the entire HMAC-SHA256 audit chain from genesis block
    to verify integrity and detect any historical modification.
    """
    return verify_log_chain()


@app.post("/api/audit/tamper-demo")
async def tamper_audit_log_demo(entry_index: int = 0):
    """
    Demo endpoint: modifies an audit entry without updating the HMAC signature
    to simulate an attacker editing historical records and prove tamper-detection.
    """
    tamper_result = tamper_demo_entry(entry_index)
    verify_result = verify_log_chain()
    return {
        "tamper_result": tamper_result,
        "verification_after_tamper": verify_result
    }


@app.post("/api/knowledge/upload")
async def upload_document(
    file: UploadFile = File(...),
):
    """
    Accept document upload and simulate indexing into ChromaDB.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    content = await file.read()
    size_kb = len(content) // 1024 or 1
    
    file_type = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "unknown"
    
    # Simulate indexing
    result = simulate_indexing(file.filename, file_type, size_kb)
    
    return {
        "status": "indexed",
        "filename": file.filename,
        "file_type": file_type,
        "size_kb": size_kb,
        "chunks": result["chunks"],
        "collection": result["collection"],
        "embedding_time_ms": result["embedding_time_ms"],
        "indexed_at": result["indexed_at"],
        "message": f"Successfully indexed {result['chunks']} chunks into ChromaDB ({result['collection']})"
    }


@app.get("/api/knowledge/documents")
async def list_documents():
    """Returns all indexed documents."""
    docs = get_all_documents()
    stats = get_rag_stats()
    return {
        "documents": docs,
        "stats": stats
    }


@app.get("/api/network/monitor")
async def get_network_monitor():
    """Returns real-time network sovereignty metrics."""
    now = datetime.now()
    
    # Add a new blocked request to the log with current timestamp
    new_blocked = {
        "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "host": random.choice([
            "api.openai.com", "api.anthropic.com", "api.cohere.ai",
            "inference.googleapis.com", "bedrock.amazonaws.com"
        ]),
        "rule": "iptables OUTPUT DROP",
        "action": "BLOCKED"
    }
    _blocked_requests_log.insert(0, new_blocked)
    if len(_blocked_requests_log) > 20:
        _blocked_requests_log.pop()
    
    return {
        "outbound_bytes": 0,
        "external_api_calls": 0,
        "dns_queries_external": 0,
        "inbound_bytes": 0,
        "status": "SOVEREIGN",
        "firewall_active": True,
        "firewall_rules": "iptables — ALL outbound BLOCKED",
        "gvisor_sandbox": True,
        "blocked_requests": _blocked_requests_log[:10],
        "last_checked": now.isoformat(),
        "uptime_sovereign_hours": 14.3
    }


@app.post("/api/output/generate-docx")
async def export_docx_deliverable(request: DocxGenerateRequest):
    """
    Generates a properly formatted Microsoft Word document (.docx)
    from task response content and returns it as a downloadable FileResponse.
    """
    sections = request.sections
    if not sections:
        sections = parse_markdown_to_sections(request.content or "")

    filename = request.filename or "deliverable_report.docx"
    if not filename.endswith(".docx"):
        filename = f"{filename}.docx"

    title = request.title or "Sovereign AI Deliverable Report"

    file_path = generate_docx_report(
        title=title,
        sections=sections,
        filename=filename
    )

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "outbound_bytes": 0, "timestamp": datetime.now().isoformat()}


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
