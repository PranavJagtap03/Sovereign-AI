"""
Run with: pytest test_classifier.py -v

These are the tests the brief calls for in 2.1: "assert each task type routes
to the correct model." This checks classification only (routing to a model
name is covered by test_registry.py / integration tests once Ollama is up).
"""

from classifier import classify_rule_based


def test_coding_request():
    prompt = "Write a Python script that parses this CSV and computes monthly totals"
    assert classify_rule_based(prompt) == "coding"


def test_document_request():
    prompt = "Draft an approval note summarising the key findings from this report"
    assert classify_rule_based(prompt) == "document"


def test_vision_request_by_filename():
    assert classify_rule_based("please read this", attached_file="inspection_scan.jpg") == "vision"


def test_vision_request_by_keyword():
    prompt = "Can you interpret this P&ID diagram and list the valves?"
    assert classify_rule_based(prompt) == "vision"


def test_spreadsheet_request():
    prompt = "Build a spreadsheet with formulas to compute quarterly totals"
    assert classify_rule_based(prompt) == "spreadsheet"


def test_spreadsheet_by_filename():
    assert classify_rule_based("process this", attached_file="vendor_data.xlsx") == "spreadsheet"


def test_ambiguous_falls_through_to_none():
    # Nothing here should confidently match any rule -> caller should use LLM fallback
    prompt = "hello there"
    assert classify_rule_based(prompt) is None


def test_scanned_pdf_routes_to_vision():
    prompt = "please process this scanned inspection report"
    assert classify_rule_based(prompt, attached_file="report.pdf") == "vision"


def test_text_pdf_routes_to_document():
    prompt = "summarise this procurement SOP"
    assert classify_rule_based(prompt, attached_file="sop.pdf") == "document"
