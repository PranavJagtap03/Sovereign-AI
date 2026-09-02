"""
Mock RAG (Retrieval-Augmented Generation) Module
Simulates ChromaDB document retrieval with Stage 4 (RBAC Filter) and Stage 6 (Company Brain Retrieval).
"""

from datetime import datetime, timedelta
import random
from typing import Optional, List, Dict, Any

# ─── Stage 4: Authorization / RBAC Clearance Hierarchy ────────────────────────

CLEARANCE_SCALE: List[str] = [
    "Internal",
    "Restricted",
    "Confidential",
    "Highly Confidential"
]

CLEARANCE_LEVELS: Dict[str, int] = {level: idx for idx, level in enumerate(CLEARANCE_SCALE)}

USER_CLEARANCE: Dict[str, str] = {
    "inspector": "Internal",
    "engineer": "Restricted",
    "manager": "Confidential",
    "admin": "Highly Confidential"
}


def check_access(user_role: str, doc_sensitivity: str) -> bool:
    """
    Stage 4: Authorization / RBAC Filter check.
    Compares user role clearance level against document sensitivity.
    Returns True if user clearance is greater than or equal to document sensitivity.
    Fails closed (default rank = 999) if sensitivity is unrecognized.
    """
    user_clearance = USER_CLEARANCE.get(user_role.lower(), user_role.title() if user_role.title() in CLEARANCE_LEVELS else "Internal")
    user_rank = CLEARANCE_LEVELS.get(user_clearance, 0)

    # Normalize sensitivity and fail closed to prevent privilege escalation
    normalized_sensitivity = (doc_sensitivity or "").strip().title()
    doc_rank = CLEARANCE_LEVELS.get(normalized_sensitivity, CLEARANCE_LEVELS.get(doc_sensitivity, 999))
    return user_rank >= doc_rank


# ─── Document Store (Stage 6 + Sensitivity & PII Metadata) ───────────────────

MOCK_DOCUMENTS = [
    {
        "id": "doc_001",
        "name": "SOP_Manual_v2.pdf",
        "type": "pdf",
        "collection": "internal_docs",
        "size_kb": 2847,
        "chunks": 184,
        "indexed_on": "2026-08-15T09:23:00",
        "status": "indexed",
        "tags": ["sop", "procedures", "operations"],
        "description": "Standard Operating Procedures Manual — Version 2.0",
        "sensitivity": "Internal",
        "pii_masked": False
    },
    {
        "id": "doc_002",
        "name": "Safety_Policy_2025.docx",
        "type": "docx",
        "collection": "policy_docs",
        "size_kb": 1203,
        "chunks": 97,
        "indexed_on": "2026-08-18T14:45:00",
        "status": "indexed",
        "tags": ["safety", "policy", "compliance"],
        "description": "Workplace Safety and Health Policy 2025",
        "sensitivity": "Internal",
        "pii_masked": False
    },
    {
        "id": "doc_003",
        "name": "QC_Checklist.xlsx",
        "type": "xlsx",
        "collection": "engineering_docs",
        "size_kb": 456,
        "chunks": 43,
        "indexed_on": "2026-08-20T11:12:00",
        "status": "indexed",
        "tags": ["quality", "checklist", "engineering"],
        "description": "Quality Control Inspection Checklist — Manufacturing",
        "sensitivity": "Internal",
        "pii_masked": False
    },
    {
        "id": "doc_004",
        "name": "Procurement_Policy_v3.pdf",
        "type": "pdf",
        "collection": "policy_docs",
        "size_kb": 1876,
        "chunks": 152,
        "indexed_on": "2026-08-22T16:30:00",
        "status": "indexed",
        "tags": ["procurement", "finance", "approval"],
        "description": "Procurement and Vendor Management Policy — Version 3",
        "sensitivity": "Internal",
        "pii_masked": False
    },
    {
        "id": "doc_005",
        "name": "Equipment_Maintenance_Standards.pdf",
        "type": "pdf",
        "collection": "engineering_docs",
        "size_kb": 3412,
        "chunks": 278,
        "indexed_on": "2026-08-25T10:00:00",
        "status": "indexed",
        "tags": ["maintenance", "engineering", "standards"],
        "description": "Equipment Maintenance and Inspection Standards — IS 14846",
        "sensitivity": "Internal",
        "pii_masked": False
    },
    {
        "id": "doc_006",
        "name": "HR_Leave_Policy.pdf",
        "type": "pdf",
        "collection": "hr_docs",
        "size_kb": 634,
        "chunks": 51,
        "indexed_on": "2026-08-28T09:15:00",
        "status": "indexed",
        "tags": ["hr", "leave", "policy"],
        "description": "Human Resources Leave and Attendance Policy",
        "sensitivity": "Restricted",
        "pii_masked": True
    },
    {
        "id": "doc_007",
        "name": "Network_Security_Guidelines.pdf",
        "type": "pdf",
        "collection": "it_docs",
        "size_kb": 921,
        "chunks": 73,
        "indexed_on": "2026-08-29T14:22:00",
        "status": "indexed",
        "tags": ["security", "network", "it"],
        "description": "Information Security and Network Access Guidelines",
        "sensitivity": "Confidential",
        "pii_masked": False
    },
    {
        "id": "doc_008",
        "name": "Maintenance_Budget_2025.pdf",
        "type": "pdf",
        "collection": "engineering_docs",
        "size_kb": 1124,
        "chunks": 89,
        "indexed_on": "2026-08-30T11:45:00",
        "status": "indexed",
        "tags": ["budget", "maintenance", "finance"],
        "description": "Annual Maintenance Budget and Cost Estimates 2025",
        "sensitivity": "Internal",
        "pii_masked": False
    }
]

# ─── Collection stats ─────────────────────────────────────────────────────────

COLLECTIONS = {
    "internal_docs": {"count": 184, "color": "#00C896"},
    "policy_docs": {"count": 249, "color": "#5B8DEF"},
    "engineering_docs": {"count": 410, "color": "#F5A623"},
    "hr_docs": {"count": 51, "color": "#A78BFA"},
    "it_docs": {"count": 73, "color": "#EF4444"},
}

TOTAL_CHUNKS = sum(c["count"] for c in COLLECTIONS.values())

# ─── Mock chunks for retrieval (Stage 6 + Document PII Redaction) ─────────────

MOCK_CHUNKS = {
    "approval": [
        {
            "source": "SOP_Manual_v2.pdf",
            "section": "§3.2 — Approval Workflow",
            "similarity": 0.94,
            "text": "The approval process for official documents requires sign-off from the originating Department Head, followed by cross-functional review if the document impacts multiple departments...",
            "pii_masked": False
        },
        {
            "source": "Procurement_Policy_v3.pdf",
            "section": "§4.2 — High-Value Procurement",
            "similarity": 0.91,
            "text": "All procurement requests exceeding ₹10,00,000 must follow the high-value approval chain: TEC evaluation → Finance clearance → Competent Authority approval...",
            "pii_masked": False
        },
        {
            "source": "Safety_Policy_2025.docx",
            "section": "§6.1 — Incident Reporting",
            "similarity": 0.78,
            "text": "Incident reports must be submitted within 24 hours and approved by the Safety Officer before filing with the regulatory authority...",
            "pii_masked": False
        }
    ],
    "maintenance": [
        {
            "source": "Equipment_Maintenance_Standards.pdf",
            "section": "§5.3 — Preventive Maintenance Schedule",
            "similarity": 0.92,
            "text": "Rotating equipment with bearing assemblies must undergo vibration analysis every 3 months. Bearing replacement is mandated when wear exceeds 80% of design limit...",
            "pii_masked": False
        },
        {
            "source": "Maintenance_Budget_2025.pdf",
            "section": "§2.1 — Cost Categories",
            "similarity": 0.88,
            "text": "Estimated repair costs for critical mechanical components: Bearing replacement ₹85,000–₹1,40,000; Valve overhaul ₹45,000–₹95,000; Electrical panel repair ₹60,000–₹2,20,000...",
            "pii_masked": False
        },
        {
            "source": "QC_Checklist.xlsx",
            "section": "Sheet: Equipment Checks",
            "similarity": 0.81,
            "text": "Inspection criteria for pump units: bearing temperature <65°C, vibration <4.5 mm/s RMS, seal leakage NIL, noise <85 dB(A) at 1m distance...",
            "pii_masked": False
        }
    ],
    "hr": [
        {
            "source": "HR_Leave_Policy.pdf",
            "section": "§4.1 — Medical Leave & Records",
            "similarity": 0.89,
            "text": "Medical certificates and employee health records [PII REDACTED] must be submitted directly to the HR Medical Review Board within 48 hours of leave commencement...",
            "pii_masked": True,
            "pii_badge": "PII redacted in this excerpt"
        }
    ]
}


def get_all_documents() -> list:
    """Return full document list for Knowledge Base page."""
    return MOCK_DOCUMENTS


def get_rag_stats() -> dict:
    """Return RAG index statistics."""
    return {
        "total_chunks": 1247,
        "total_documents": len(MOCK_DOCUMENTS),
        "collections": len(COLLECTIONS),
        "collection_details": COLLECTIONS,
        "last_updated": datetime.now().isoformat(),
        "embedding_model": "nomic-embed-text (local)",
        "vector_db": "ChromaDB v0.5.3",
        "index_size_mb": 847
    }


def simulate_indexing(filename: str, file_type: str, size_kb: int) -> dict:
    """Simulate document indexing process with sensitivity and PII classification."""
    chunks = max(20, int(size_kb / 15) + random.randint(-5, 10))
    collection = _assign_collection(file_type, filename)
    name_lower = filename.lower()

    if any(k in name_lower for k in ["hr", "leave", "salary", "payroll", "employee"]):
        sensitivity = "Restricted"
        pii_masked = True
    elif any(k in name_lower for k in ["security", "credential", "secret", "network"]):
        sensitivity = "Confidential"
        pii_masked = False
    else:
        sensitivity = "Internal"
        pii_masked = False

    return {
        "status": "indexed",
        "filename": filename,
        "file_type": file_type,
        "chunks": chunks,
        "collection": collection,
        "sensitivity": sensitivity,
        "pii_masked": pii_masked,
        "embedding_time_ms": random.randint(800, 3200),
        "indexed_at": datetime.now().isoformat()
    }


def _assign_collection(file_type: str, filename: str) -> str:
    """Assign document to appropriate collection."""
    name_lower = filename.lower()
    if any(k in name_lower for k in ["safety", "policy", "sop", "procedure"]):
        return "policy_docs"
    elif any(k in name_lower for k in ["equipment", "maintenance", "engineering", "qc"]):
        return "engineering_docs"
    elif any(k in name_lower for k in ["hr", "leave", "employee"]):
        return "hr_docs"
    elif any(k in name_lower for k in ["network", "security", "it", "cyber"]):
        return "it_docs"
    return "internal_docs"


# Import get_rag_results for backward-compatible fallback
from mock_llm import get_rag_results


def get_mock_chunks(category: str = "approval", user_role: Optional[str] = None) -> list:
    """
    Retrieve chunks for a category with document-level PII annotation and RBAC filtering.
    """
    chunks = MOCK_CHUNKS.get(category, [])
    doc_map = {doc["name"]: doc for doc in MOCK_DOCUMENTS}
    result_chunks = []

    for chunk in chunks:
        doc = doc_map.get(chunk.get("source"))
        doc_sens = doc.get("sensitivity", "Internal") if doc else "Internal"
        doc_pii = doc.get("pii_masked", False) if doc else chunk.get("pii_masked", False)

        if user_role and not check_access(user_role, doc_sens):
            continue

        c = dict(chunk)
        c["pii_masked"] = doc_pii
        if doc_pii:
            c["pii_badge"] = "PII redacted in this excerpt"
        result_chunks.append(c)

    return result_chunks


def get_authorized_rag_results(task_type: str, user_role: str = "inspector") -> dict:
    """
    Stage 4 (Authorization/RBAC Filter) merged with Stage 6 (Company Brain Retrieval).
    Wraps get_rag_results() and filters out any source document the user isn't cleared for.
    If documents are filtered, attaches a 'filtered_documents' list explaining why.
    Also notes document-level PII masking status with 'pii_badge'.
    """
    base_result = get_rag_results(task_type)
    result = dict(base_result)

    user_clearance = USER_CLEARANCE.get(user_role.lower(), user_role if user_role in CLEARANCE_LEVELS else "Internal")
    result["user_role"] = user_role
    result["user_clearance"] = user_clearance
    result["filtered_documents"] = []

    if not result.get("retrieved", False):
        return result

    doc_map = {doc["name"]: doc for doc in MOCK_DOCUMENTS}
    sources = result.get("sources", [])
    authorized_sources = []
    filtered_documents = []
    has_pii_masked = False

    for source_name in sources:
        doc = doc_map.get(source_name)
        doc_sensitivity = doc.get("sensitivity", "Internal") if doc else "Internal"
        doc_pii_masked = doc.get("pii_masked", False) if doc else False

        if check_access(user_role, doc_sensitivity):
            authorized_sources.append(source_name)
            if doc_pii_masked:
                has_pii_masked = True
        else:
            filtered_documents.append(
                f"{source_name} blocked — requires {doc_sensitivity} clearance, user has {user_clearance}"
            )

    result["sources"] = authorized_sources
    result["chunks"] = max(len(authorized_sources), 1) if authorized_sources else 0
    result["filtered_documents"] = filtered_documents
    result["rbac_filtered"] = len(filtered_documents) > 0
    result["pii_masked"] = has_pii_masked
    if has_pii_masked:
        result["pii_badge"] = "PII redacted in this excerpt"

    if len(authorized_sources) == 0 and len(sources) > 0:
        result["retrieved"] = False
        result["reason"] = f"All candidate documents blocked by RBAC filter for role '{user_role}' ({user_clearance} clearance)"

    return result
