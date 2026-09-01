"""
Mock Audit Log Module
Generates realistic, tamper-evident hash-chained audit log entries.
"""

import hashlib
import json
import random
from datetime import datetime, timedelta

# ─── Dummy audit entries ──────────────────────────────────────────────────────

_BASE_ENTRIES = [
    {
        "user": "analyst_priya",
        "user_role": "Data Analyst",
        "task_type": "Document Analysis",
        "model_used": "Qwen2.5-VL-7B",
        "input_summary": "Equipment_Inspection_Q2.pdf (24 pages)",
        "output_summary": "inspection_summary.xlsx (3 sheets)",
        "duration_ms": 4230,
        "status": "SUCCESS",
        "rag_used": True,
        "rbac_role": "analyst",
        "output_format": "Excel"
    },
    {
        "user": "dev_karthik",
        "user_role": "Software Engineer",
        "task_type": "Code Generation",
        "model_used": "DeepSeek-Coder-V2-Lite",
        "input_summary": "JSON sensor log parser with anomaly detection",
        "output_summary": "anomaly_detector.py (89 lines)",
        "duration_ms": 3890,
        "status": "SUCCESS",
        "rag_used": False,
        "rbac_role": "developer",
        "output_format": "Code"
    },
    {
        "user": "manager_sunita",
        "user_role": "Operations Manager",
        "task_type": "Policy Q&A",
        "model_used": "Phi-3-Mini-4K",
        "input_summary": "High-value procurement approval process query",
        "output_summary": "Structured 5-step approval process with thresholds",
        "duration_ms": 2710,
        "status": "SUCCESS",
        "rag_used": True,
        "rbac_role": "manager",
        "output_format": "Word Doc"
    },
    {
        "user": "analyst_rajan",
        "user_role": "Quality Analyst",
        "task_type": "Document Drafting",
        "model_used": "Qwen2.5-7B",
        "input_summary": "Approval note from Safety_Policy_2025.docx",
        "output_summary": "Approval note draft (1,240 words)",
        "duration_ms": 3140,
        "status": "SUCCESS",
        "rag_used": True,
        "rbac_role": "analyst",
        "output_format": "Word Doc"
    },
    {
        "user": "dev_meera",
        "user_role": "ML Engineer",
        "task_type": "Code Generation",
        "model_used": "DeepSeek-Coder-V2-Lite",
        "input_summary": "REST API client for internal data pipeline",
        "output_summary": "api_client.py (134 lines) with unit tests",
        "duration_ms": 5120,
        "status": "SUCCESS",
        "rag_used": False,
        "rbac_role": "developer",
        "output_format": "Code"
    },
    {
        "user": "admin_vikram",
        "user_role": "System Administrator",
        "task_type": "Document Analysis",
        "model_used": "Qwen2.5-VL-7B",
        "input_summary": "Network_Topology_Diagram.png",
        "output_summary": "Topology analysis report — 12 nodes identified",
        "duration_ms": 2890,
        "status": "SUCCESS",
        "rag_used": False,
        "rbac_role": "admin",
        "output_format": "JSON"
    },
    {
        "user": "analyst_priya",
        "user_role": "Data Analyst",
        "task_type": "Data Extraction",
        "model_used": "Qwen2.5-7B",
        "input_summary": "QC_Checklist.xlsx — extract failed items",
        "output_summary": "Failed items report: 7 items flagged",
        "duration_ms": 1980,
        "status": "SUCCESS",
        "rag_used": True,
        "rbac_role": "analyst",
        "output_format": "Excel"
    },
    {
        "user": "manager_anand",
        "user_role": "Department Manager",
        "task_type": "Policy Q&A",
        "model_used": "Phi-3-Mini-4K",
        "input_summary": "Leave encashment policy query",
        "output_summary": "Leave policy clarification with section references",
        "duration_ms": 1640,
        "status": "SUCCESS",
        "rag_used": True,
        "rbac_role": "manager",
        "output_format": "Word Doc"
    },
    {
        "user": "dev_karthik",
        "user_role": "Software Engineer",
        "task_type": "Code Review",
        "model_used": "DeepSeek-Coder-V2-Lite",
        "input_summary": "data_pipeline.py (230 lines) — review request",
        "output_summary": "Code review: 4 issues flagged, 2 security warnings",
        "duration_ms": 4560,
        "status": "SUCCESS",
        "rag_used": False,
        "rbac_role": "developer",
        "output_format": "Code"
    },
    {
        "user": "analyst_rajan",
        "user_role": "Quality Analyst",
        "task_type": "Document Analysis",
        "model_used": "Qwen2.5-VL-7B",
        "input_summary": "Safety_Audit_Report_Aug2026.pdf",
        "output_summary": "Safety audit summary: 14 observations, 3 non-conformances",
        "duration_ms": 5870,
        "status": "SUCCESS",
        "rag_used": True,
        "rbac_role": "analyst",
        "output_format": "Word Doc"
    }
]

# ─── Hash-chain generation ────────────────────────────────────────────────────

def _compute_hash(entry: dict, previous_hash: str) -> str:
    """Compute SHA-256 hash for tamper-evident chain."""
    content = json.dumps({
        "timestamp": entry["timestamp"],
        "user": entry["user"],
        "task_type": entry["task_type"],
        "input_summary": entry["input_summary"],
        "previous_hash": previous_hash
    }, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()


def _compute_input_hash(input_summary: str) -> str:
    """Compute input content hash."""
    return hashlib.sha256(f"input:{input_summary}".encode()).hexdigest()[:16]


def _compute_output_hash(output_summary: str) -> str:
    """Compute output content hash."""
    return hashlib.sha256(f"output:{output_summary}".encode()).hexdigest()[:16]


def generate_audit_logs() -> list:
    """Generate a list of hash-chained audit log entries."""
    logs = []
    now = datetime.now()
    previous_hash = "0000000000000000"  # Genesis block
    
    # Generate timestamps going backwards in time
    timestamps = []
    current_time = now - timedelta(hours=2)
    for i in range(len(_BASE_ENTRIES)):
        timestamps.append(current_time)
        current_time -= timedelta(minutes=random.randint(8, 45))
    timestamps.reverse()
    
    for i, (entry, ts) in enumerate(zip(_BASE_ENTRIES, timestamps)):
        entry_with_ts = {
            **entry,
            "id": f"LOG-{now.strftime('%Y%m%d')}-{str(i+1).zfill(4)}",
            "timestamp": ts.isoformat(timespec='seconds'),
            "input_hash": _compute_input_hash(entry["input_summary"]),
            "output_hash": _compute_output_hash(entry["output_summary"]),
            "outbound_bytes": 0,
            "session_id": f"sess_{random.randint(100000, 999999)}"
        }
        
        chain_hash = _compute_hash(entry_with_ts, previous_hash)
        entry_with_ts["chain_hash"] = chain_hash[:16]
        entry_with_ts["previous_hash"] = previous_hash[:16]
        previous_hash = chain_hash
        
        logs.append(entry_with_ts)
    
    return list(reversed(logs))  # Most recent first


def get_audit_summary() -> dict:
    """Return audit statistics."""
    logs = generate_audit_logs()
    return {
        "total_tasks": len(logs),
        "success_rate": 100.0,
        "models_used": list(set(l["model_used"] for l in logs)),
        "total_outbound_bytes": 0,
        "unique_users": len(set(l["user"] for l in logs)),
        "chain_verified": True,
        "last_verified": datetime.now().isoformat()
    }
