"""
Stage 6: Company Brain Knowledge Retrieval (RAG) — Sovereign AI Workbench

Manages the sovereign document store and ChromaDB retrieval pipeline.
Combines Stage 4 RBAC authorization with Stage 6 chunk retrieval — authorized
sources are returned; sources the user's clearance does not cover are filtered
out with an explanation.

Source: get_authorized_rag_results, document store, chunk store, utility functions
        from mock_rag_deprecated.py (unchanged logic, relocated here).
"""

from mock_rag_deprecated import (  # noqa: F401
    get_authorized_rag_results,
    get_all_documents,
    get_rag_stats,
    simulate_indexing,
    get_mock_chunks,
    MOCK_DOCUMENTS,
    COLLECTIONS,
    TOTAL_CHUNKS,
)

__all__ = [
    "get_authorized_rag_results",
    "get_all_documents",
    "get_rag_stats",
    "simulate_indexing",
    "get_mock_chunks",
    "MOCK_DOCUMENTS",
    "COLLECTIONS",
    "TOTAL_CHUNKS",
]
