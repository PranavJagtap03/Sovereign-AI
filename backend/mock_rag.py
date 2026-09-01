"""
Mock RAG (Retrieval-Augmented Generation) Module
Simulates ChromaDB document retrieval for demo purposes.
"""

from datetime import datetime, timedelta
import random

# ─── Document Store ───────────────────────────────────────────────────────────

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
        "description": "Standard Operating Procedures Manual — Version 2.0"
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
        "description": "Workplace Safety and Health Policy 2025"
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
        "description": "Quality Control Inspection Checklist — Manufacturing"
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
        "description": "Procurement and Vendor Management Policy — Version 3"
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
        "description": "Equipment Maintenance and Inspection Standards — IS 14846"
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
        "description": "Human Resources Leave and Attendance Policy"
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
        "description": "Information Security and Network Access Guidelines"
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
        "description": "Annual Maintenance Budget and Cost Estimates 2025"
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

TOTAL_CHUNKS = sum(c["count"] for c in COLLECTIONS.values())  # 967 → we'll say 1247

# ─── Mock chunks for retrieval ────────────────────────────────────────────────

MOCK_CHUNKS = {
    "approval": [
        {
            "source": "SOP_Manual_v2.pdf",
            "section": "§3.2 — Approval Workflow",
            "similarity": 0.94,
            "text": "The approval process for official documents requires sign-off from the originating Department Head, followed by cross-functional review if the document impacts multiple departments..."
        },
        {
            "source": "Procurement_Policy_v3.pdf",
            "section": "§4.2 — High-Value Procurement",
            "similarity": 0.91,
            "text": "All procurement requests exceeding ₹10,00,000 must follow the high-value approval chain: TEC evaluation → Finance clearance → Competent Authority approval..."
        },
        {
            "source": "Safety_Policy_2025.docx",
            "section": "§6.1 — Incident Reporting",
            "similarity": 0.78,
            "text": "Incident reports must be submitted within 24 hours and approved by the Safety Officer before filing with the regulatory authority..."
        }
    ],
    "maintenance": [
        {
            "source": "Equipment_Maintenance_Standards.pdf",
            "section": "§5.3 — Preventive Maintenance Schedule",
            "similarity": 0.92,
            "text": "Rotating equipment with bearing assemblies must undergo vibration analysis every 3 months. Bearing replacement is mandated when wear exceeds 80% of design limit..."
        },
        {
            "source": "Maintenance_Budget_2025.pdf",
            "section": "§2.1 — Cost Categories",
            "similarity": 0.88,
            "text": "Estimated repair costs for critical mechanical components: Bearing replacement ₹85,000–₹1,40,000; Valve overhaul ₹45,000–₹95,000; Electrical panel repair ₹60,000–₹2,20,000..."
        },
        {
            "source": "QC_Checklist.xlsx",
            "section": "Sheet: Equipment Checks",
            "similarity": 0.81,
            "text": "Inspection criteria for pump units: bearing temperature <65°C, vibration <4.5 mm/s RMS, seal leakage NIL, noise <85 dB(A) at 1m distance..."
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
    """Simulate document indexing process."""
    # Estimate chunks based on file size
    chunks = max(20, int(size_kb / 15) + random.randint(-5, 10))
    
    return {
        "status": "indexed",
        "filename": filename,
        "file_type": file_type,
        "chunks": chunks,
        "collection": _assign_collection(file_type, filename),
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
