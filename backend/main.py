"""
Sovereign AI Workbench — FastAPI Backend
Mock engine for SIH 2026 Demo | Team Code:201
All LLM calls are simulated — works 100% offline without GPU.
"""

import asyncio
import random
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from mock_llm import (
    classify_task, get_model_info, get_demo_response,
    get_react_loop, get_pii_check_result, get_rag_results
)
from mock_rag import get_all_documents, get_rag_stats, simulate_indexing
from mock_audit import generate_audit_logs, get_audit_summary

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
    scenario: Optional[str] = None  # pre-built demo scenario key


class AgentRunResponse(BaseModel):
    steps: list
    model_used: str
    task_type: str
    time_taken_ms: int
    outbound_bytes: int
    output_file: Optional[str]
    final_response: str


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


@app.post("/api/agent/run")
async def run_agent(request: AgentRunRequest):
    """
    Main agentic pipeline endpoint.
    Returns the full ReAct loop trace with simulated processing delays.
    """
    global _task_counter
    _task_counter += 1

    has_file = bool(request.file_name)
    task_type = classify_task(request.task, has_file)
    
    # Override task type for specific scenarios
    if request.scenario == "code":
        task_type = "code"
    elif request.scenario == "vision" or request.scenario == "analysis":
        task_type = "analysis"
    elif request.scenario == "rag":
        task_type = "rag"
    elif request.scenario == "text":
        task_type = "text"

    model_info = get_model_info(task_type)
    pii_result = get_pii_check_result()
    rag_result = get_rag_results(task_type)
    react_loop = get_react_loop(task_type)
    final_response = get_demo_response(task_type)
    output_file = _get_output_filename(request.output_format, task_type)
    
    # Simulate timing
    base_ms = random.randint(2800, 5400)
    
    # ─── Build step trace ─────────────────────────────────────────────────────

    rag_step = {
        "step": 3,
        "name": "RAG Retrieval",
        "icon": "📚",
        "status": "skipped" if not rag_result.get("retrieved") else "passed",
        "details": (
            f"RAG not applicable for {task_type} tasks"
            if not rag_result.get("retrieved")
            else f"{rag_result['chunks']} chunks retrieved from: {', '.join(rag_result['sources'])} | Similarity: {rag_result['top_similarity']} | Query: {rag_result['query_time_ms']}ms"
        ),
        "sub_items": [] if not rag_result.get("retrieved") else [
            f"🔍 Querying ChromaDB ({rag_result['collection']} collection)...",
            f"✓ Top match similarity: {rag_result['top_similarity']}",
            f"📄 Sources: {', '.join(rag_result['sources'])}"
        ]
    }

    steps = [
        {
            "step": 1,
            "name": "Security Check",
            "icon": "🔒",
            "status": "passed",
            "details": f"PII detected: None | {pii_result['entities_scanned']} entities scanned | RBAC check: Authorized ✓ | Input sanitized ✓",
            "sub_items": [
                f"🛡 PII scan: {pii_result['entities_scanned']} tokens checked — CLEAN",
                f"🔑 RBAC: User role authorized for {task_type} tasks",
                f"🧹 Input sanitization: Complete ({pii_result['scan_duration_ms']}ms)"
            ]
        },
        {
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
        },
        rag_step,
        {
            "step": 4,
            "name": "Agentic Processing (ReAct Loop)",
            "icon": "⚙️",
            "status": "passed",
            "details": f"ReAct loop completed | {len(react_loop)} iterations | Model: {model_info['model']}",
            "react_loop": react_loop,
            "sub_items": [f"{'💭 Thought' if 'thought' in item else '⚡ Action'}: {item.get('thought') or item.get('action')}" for item in react_loop[:3]]
        },
        {
            "step": 5,
            "name": "Validation & Safety Check",
            "icon": "✅",
            "status": "passed",
            "details": "Output validated | No sensitive data in output ✓ | Format verified ✓ | Content policy: PASS",
            "sub_items": [
                "🔍 Output PII scan: CLEAN",
                "📋 Format validation: PASS",
                "🛡 Content safety: COMPLIANT",
                f"📊 Output size: {random.randint(18, 210)} KB"
            ]
        },
        {
            "step": 6,
            "name": "Deliverable Ready",
            "icon": "📄",
            "status": "passed",
            "details": f"Output file: {output_file} | Encrypted with AES-256 | Stored in local vault",
            "output_file": output_file,
            "sub_items": [
                f"📁 File: {output_file}",
                "🔐 Encrypted: AES-256-GCM",
                "💾 Stored: Local secure vault",
                "📝 Audit entry: logged"
            ]
        }
    ]

    return {
        "steps": steps,
        "model_used": model_info["model"],
        "task_type": task_type,
        "time_taken_ms": base_ms,
        "outbound_bytes": 0,
        "output_file": output_file,
        "final_response": final_response
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
                    "name": "Qwen2.5-7B",
                    "type": "Text/Reasoning",
                    "status": "active",
                    "vram_gb": 5.2,
                    "vram_pct": 65,
                    "tasks_today": random.randint(14, 28),
                    "size": "7.2B params (Q4_K_M)"
                },
                {
                    "name": "Phi-3-Mini-4K",
                    "type": "Text/RAG",
                    "status": "active",
                    "vram_gb": 2.4,
                    "vram_pct": 30,
                    "tasks_today": random.randint(8, 18),
                    "size": "3.8B params (Q4_K_M)"
                },
                {
                    "name": "DeepSeek-Coder-V2-Lite",
                    "type": "Code",
                    "status": "active",
                    "vram_gb": 8.4,
                    "vram_pct": 85,
                    "tasks_today": random.randint(6, 14),
                    "size": "15.7B params (Q4_K_M)"
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
    
    return {
        "logs": logs,
        "total": len(logs),
        "summary": summary,
        "chain_verified": True,
        "verification_timestamp": datetime.now().isoformat()
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


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "outbound_bytes": 0, "timestamp": datetime.now().isoformat()}


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
