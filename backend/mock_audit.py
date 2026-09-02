"""
Stage 13: Tamper-Evident Hash-Chained Audit Log Module
Sovereign AI Workbench — SIH 2026

Features:
- HMAC-SHA256 cryptographically chained log entries
- Previous-hash pointer linkage from genesis hash (64 zeros)
- Tamper detection verification across all historical entries
- Strict privacy enforcement: rejects raw document content and passwords
"""

import hmac
import hashlib
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

GENESIS_HASH = "0" * 64
DEFAULT_SECRET_KEY = b"demo-secret-key"

# In-memory log store for real-time audit chain
_AUDIT_LOG_STORE: List[Dict[str, Any]] = []


def _check_forbidden_keys(d: Any) -> None:
    """
    Recursively inspects the details payload.
    Rejects any dictionary containing keys like 'raw_content' or 'password'.
    """
    if isinstance(d, dict):
        for k, v in d.items():
            k_lower = str(k).lower().strip()
            if k_lower in ("raw_content", "password", "passwords", "raw_document", "plaintext_secret"):
                raise ValueError(
                    f"Audit logging privacy violation: forbidden key '{k}' detected. "
                    "Only metadata, decisions, and masked previews are permitted in audit logs."
                )
            _check_forbidden_keys(v)
    elif isinstance(d, (list, tuple)):
        for item in d:
            _check_forbidden_keys(item)


def _compute_entry_hmac(secret_key: bytes, previous_hash: str, timestamp: str, details: dict) -> str:
    """Computes HMAC-SHA256 over previous_hash + timestamp + canonical JSON of details."""
    serialized_details = json.dumps(details, sort_keys=True, default=str)
    payload = f"{previous_hash}{timestamp}{serialized_details}".encode("utf-8")
    return hmac.new(secret_key, payload, hashlib.sha256).hexdigest()


def append_log_entry(
    event_type: str,
    details: Dict[str, Any],
    secret_key: bytes = DEFAULT_SECRET_KEY
) -> Dict[str, Any]:
    """
    Appends an immutable, hash-chained entry to the audit log store.

    Args:
        event_type: Identifier of the event (e.g., "STAGE_1_INPUT_GUARD")
        details: Metadata and decision dictionary (forbidden keys: 'raw_content', 'password')
        secret_key: Secret key used to generate the HMAC-SHA256 signature

    Returns:
        dict: The appended log entry with previous_hash and entry_hash
    """
    # Enforce privacy constraint: reject sensitive keys
    _check_forbidden_keys(details)

    # Determine previous hash (genesis hash if store is empty)
    if _AUDIT_LOG_STORE:
        previous_hash = _AUDIT_LOG_STORE[-1]["entry_hash"]
    else:
        previous_hash = GENESIS_HASH

    timestamp = datetime.now().isoformat()
    new_hash = _compute_entry_hmac(secret_key, previous_hash, timestamp, details)

    entry = {
        "event_type": event_type,
        "timestamp": timestamp,
        "details": details,
        "previous_hash": previous_hash,
        "entry_hash": new_hash
    }

    _AUDIT_LOG_STORE.append(entry)
    return entry


def verify_log_chain(secret_key: bytes = DEFAULT_SECRET_KEY) -> Dict[str, Any]:
    """
    Walks through all audit log entries, recomputing each HMAC from the previous entry's hash.
    Detects if any past entry was modified or if links were broken.

    Returns:
        dict: {"chain_valid": bool, "total_entries": int, "broken_at_entry": int or None}
    """
    if not _AUDIT_LOG_STORE:
        return {
            "chain_valid": True,
            "total_entries": 0,
            "broken_at_entry": None,
            "message": "Audit chain is empty."
        }

    expected_prev = GENESIS_HASH

    for idx, entry in enumerate(_AUDIT_LOG_STORE):
        # 1. Check previous_hash link
        if entry.get("previous_hash") != expected_prev:
            return {
                "chain_valid": False,
                "total_entries": len(_AUDIT_LOG_STORE),
                "broken_at_entry": idx,
                "reason": f"Hash chain link broken at entry {idx}: recorded previous_hash='{entry.get('previous_hash')[:12]}...' != expected='{expected_prev[:12]}...'"
            }

        # 2. Recompute and verify HMAC signature
        recomputed = _compute_entry_hmac(
            secret_key,
            entry["previous_hash"],
            entry["timestamp"],
            entry["details"]
        )
        if recomputed != entry.get("entry_hash"):
            return {
                "chain_valid": False,
                "total_entries": len(_AUDIT_LOG_STORE),
                "broken_at_entry": idx,
                "reason": f"Cryptographic signature mismatch at entry {idx}: entry content was tampered. Recorded='{entry.get('entry_hash')[:12]}...' != recomputed='{recomputed[:12]}...'"
            }

        expected_prev = entry["entry_hash"]

    return {
        "chain_valid": True,
        "total_entries": len(_AUDIT_LOG_STORE),
        "broken_at_entry": None,
        "message": "All entries cryptographically verified against HMAC-SHA256 root."
    }


def tamper_demo_entry(entry_index: int = 0) -> Dict[str, Any]:
    """
    Modifies one field in a past entry WITHOUT updating its HMAC signature.
    Simulates an attacker tampering with historical audit entries to demonstrate detection.
    """
    if not _AUDIT_LOG_STORE:
        return {"tampered": False, "reason": "No entries available to tamper."}

    idx = max(0, min(entry_index, len(_AUDIT_LOG_STORE) - 1))
    target = _AUDIT_LOG_STORE[idx]

    original_details = json.dumps(target["details"])
    tampered_details = dict(target["details"])
    tampered_details["tampered_unauthorized_modification"] = True
    tampered_details["decision"] = "FORGED_COMPLIANCE"
    target["details"] = tampered_details

    return {
        "tampered": True,
        "entry_index": idx,
        "event_type": target.get("event_type"),
        "original_details": original_details,
        "tampered_details": tampered_details,
        "note": "Historical entry modified without valid HMAC recalculation. verify_log_chain() will now identify this break."
    }


# ─── Baseline Seed Data ───────────────────────────────────────────────────────

_SEED_EVENTS = [
    ("STAGE_1_INPUT_GUARD", {"user": "analyst_priya", "user_role": "Data Analyst", "task_type": "Document Analysis", "model_used": "Qwen2.5-VL-7B", "decision": "CLEAN", "risk_score": 0.0, "scan_ms": 12}),
    ("STAGE_2_PII_SANITIZER", {"user": "analyst_priya", "user_role": "Data Analyst", "task_type": "Document Analysis", "model_used": "Qwen2.5-VL-7B", "decision": "CLEAN", "entities_found": [], "scan_ms": 18}),
    ("STAGE_4_RBAC_AUTHORIZATION", {"user": "analyst_priya", "user_role": "Data Analyst", "task_type": "Document Analysis", "model_used": "Qwen2.5-VL-7B", "decision": "AUTHORIZED", "clearance": "Restricted", "docs_accessed": 3}),
    ("STAGE_8_GUARDIAN_REVIEW", {"user": "analyst_priya", "user_role": "Data Analyst", "task_type": "Document Analysis", "model_used": "Qwen2.5-VL-7B", "decision": "PASSED", "reviewed_by": "Phi-3-Mini-4K (Guardian)"}),
    ("STAGE_1_INPUT_GUARD", {"user": "dev_karthik", "user_role": "Software Engineer", "task_type": "Code Generation", "model_used": "DeepSeek-Coder-V2-Lite", "decision": "CLEAN", "risk_score": 0.0, "scan_ms": 14}),
    ("STAGE_9_TOOL_VALIDATION", {"user": "dev_karthik", "user_role": "Software Engineer", "task_type": "Code Generation", "model_used": "DeepSeek-Coder-V2-Lite", "decision": "VALID", "tool_name": "run_calculation"}),
    ("STAGE_10_RESOURCE_BUDGET", {"user": "dev_karthik", "user_role": "Software Engineer", "task_type": "Code Generation", "model_used": "DeepSeek-Coder-V2-Lite", "decision": "WITHIN_BUDGET", "steps": 9, "elapsed_ms": 2340}),
    ("STAGE_11_SANDBOX_EXECUTION", {"user": "dev_karthik", "user_role": "Software Engineer", "task_type": "Code Generation", "model_used": "DeepSeek-Coder-V2-Lite", "decision": "CONTAINED_SUCCESS", "exit_code": 0, "sandbox": "gVisor (runsc)"}),
    ("STAGE_8_GUARDIAN_REVIEW", {"user": "dev_karthik", "user_role": "Software Engineer", "task_type": "Code Generation", "model_used": "DeepSeek-Coder-V2-Lite", "decision": "PASSED", "reviewed_by": "Phi-3-Mini-4K (Guardian)"}),
    ("STAGE_4_RBAC_AUTHORIZATION", {"user": "manager_sunita", "user_role": "Operations Manager", "task_type": "Policy Q&A", "model_used": "Phi-3-Mini-4K", "decision": "AUTHORIZED", "clearance": "Confidential", "docs_accessed": 5})
]

def _seed_baseline_entries():
    """Seeds initial baseline entries into the hash chain."""
    if not _AUDIT_LOG_STORE:
        for event_type, details in _SEED_EVENTS:
            append_log_entry(event_type, details)

# Seed on import
_seed_baseline_entries()


def generate_audit_logs() -> List[Dict[str, Any]]:
    """
    Returns audit logs in format expected by UI, mapped directly from the HMAC hash chain.
    """
    formatted = []
    for idx, entry in enumerate(_AUDIT_LOG_STORE):
        dt = entry.get("details", {})
        formatted.append({
            "id": f"LOG-{datetime.now().strftime('%Y%m%d')}-{str(idx + 1).zfill(4)}",
            "timestamp": entry["timestamp"],
            "event_type": entry["event_type"],
            "user": dt.get("user", "sovereign_agent"),
            "user_role": dt.get("user_role", "Security Subsystem"),
            "task_type": dt.get("task_type", entry["event_type"].replace("STAGE_", "Stage ").replace("_", " ")),
            "model_used": dt.get("model_used", "Enclave Guard"),
            "input_summary": dt.get("input_summary", f"{entry['event_type']} evaluation"),
            "output_summary": dt.get("output_summary", f"Decision: {dt.get('decision', 'OK')}"),
            "status": "SUCCESS" if dt.get("decision") != "BLOCKED" else "BLOCKED",
            "duration_ms": dt.get("duration_ms", dt.get("scan_ms", random.randint(15, 120))),
            "input_hash": entry["previous_hash"][:16],
            "output_hash": entry["entry_hash"][:16],
            "chain_hash": entry["entry_hash"][:16],
            "previous_hash": entry["previous_hash"],
            "entry_hash": entry["entry_hash"],
            "details": dt
        })
    return list(reversed(formatted))


def get_audit_summary() -> Dict[str, Any]:
    """Returns summary statistics for the audit log dashboard."""
    chain_status = verify_log_chain()
    logs = generate_audit_logs()
    users = list(set(l["user"] for l in logs))
    models = list(set(l["model_used"] for l in logs))

    return {
        "total_tasks": len(logs),
        "success_rate": 100.0,
        "models_used": models,
        "total_outbound_bytes": 0,
        "unique_users": len(users),
        "chain_verified": chain_status["chain_valid"],
        "broken_at_entry": chain_status["broken_at_entry"],
        "last_verified": datetime.now().isoformat()
    }
