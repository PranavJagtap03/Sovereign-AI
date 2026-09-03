"""
Stage 13: Tamper-Evident Hash-Chain Audit Ledger — Sovereign AI Workbench

Maintains an in-memory HMAC-SHA256 hash-chained audit log of every pipeline
decision. Each entry cryptographically references its predecessor, making any
historical modification detectable via verify_log_chain().

Features:
  - HMAC-SHA256 cryptographically chained entries
  - Previous-hash pointer from genesis hash (64 zeros)
  - Tamper detection across all historical entries
  - Privacy enforcement: rejects raw document content and passwords

Source: append_log_entry, verify_log_chain, tamper_demo_entry,
        generate_audit_logs, get_audit_summary
        from mock_audit_deprecated.py (unchanged logic, relocated here).
"""

from mock_audit_deprecated import (  # noqa: F401
    append_log_entry,
    verify_log_chain,
    tamper_demo_entry,
    generate_audit_logs,
    get_audit_summary,
    GENESIS_HASH,
    DEFAULT_SECRET_KEY,
)

__all__ = [
    "append_log_entry",
    "verify_log_chain",
    "tamper_demo_entry",
    "generate_audit_logs",
    "get_audit_summary",
    "GENESIS_HASH",
    "DEFAULT_SECRET_KEY",
]
