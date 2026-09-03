"""
Stage 12: Air-Gapped Deliverable Vault — Sovereign AI Workbench

Generates real office-format deliverable documents (.docx) using python-docx
with professional formatting, sovereign attestation headers/footers, and
air-gapped metadata. Zero outbound egress — all generation is local.

Source: generate_docx_report, parse_markdown_to_sections
        from output_generator_deprecated.py (unchanged logic, relocated here).
"""

from output_generator_deprecated import (  # noqa: F401
    generate_docx_report,
    parse_markdown_to_sections,
)

__all__ = ["generate_docx_report", "parse_markdown_to_sections"]
