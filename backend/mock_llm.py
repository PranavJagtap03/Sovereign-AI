"""
Mock LLM Response Engine
Simulates realistic AI model responses for demo purposes without a GPU.
"""

import random
from typing import Optional

# ─── Pre-written realistic demo responses ────────────────────────────────────

DEMO_RESPONSES = {
    "code": """```python
import json
import numpy as np
from pathlib import Path
from datetime import datetime

def parse_sensor_logs(log_file: str, threshold_std: float = 3.0) -> dict:
    \"\"\"
    Parse JSON sensor logs and flag anomalies above N standard deviations.
    
    Args:
        log_file: Path to JSON sensor log file
        threshold_std: Standard deviation threshold (default: 3.0)
    
    Returns:
        Dictionary with parsed data and flagged anomalies
    \"\"\"
    with open(log_file, 'r') as f:
        logs = json.load(f)
    
    sensor_data = {}
    for entry in logs:
        sensor_id = entry.get('sensor_id', 'unknown')
        value = entry.get('value', 0)
        timestamp = entry.get('timestamp', '')
        
        if sensor_id not in sensor_data:
            sensor_data[sensor_id] = {'values': [], 'timestamps': []}
        
        sensor_data[sensor_id]['values'].append(value)
        sensor_data[sensor_id]['timestamps'].append(timestamp)
    
    anomalies = []
    for sensor_id, data in sensor_data.items():
        values = np.array(data['values'])
        mean = np.mean(values)
        std = np.std(values)
        
        for i, (val, ts) in enumerate(zip(data['values'], data['timestamps'])):
            z_score = abs(val - mean) / std if std > 0 else 0
            if z_score > threshold_std:
                anomalies.append({
                    'sensor_id': sensor_id,
                    'timestamp': ts,
                    'value': val,
                    'z_score': round(z_score, 2),
                    'mean': round(mean, 2),
                    'std': round(std, 2),
                    'severity': 'HIGH' if z_score > 5 else 'MEDIUM'
                })
    
    return {
        'total_sensors': len(sensor_data),
        'total_readings': sum(len(d['values']) for d in sensor_data.values()),
        'anomalies_detected': len(anomalies),
        'anomalies': sorted(anomalies, key=lambda x: x['z_score'], reverse=True),
        'processed_at': datetime.now().isoformat()
    }

if __name__ == '__main__':
    result = parse_sensor_logs('sensor_logs.json', threshold_std=3.0)
    print(f"✓ Processed {result['total_readings']} readings across {result['total_sensors']} sensors")
    print(f"⚠ Detected {result['anomalies_detected']} anomalies")
    
    for anomaly in result['anomalies'][:5]:
        print(f"  [{anomaly['severity']}] Sensor {anomaly['sensor_id']} @ {anomaly['timestamp']}: "
              f"value={anomaly['value']}, z-score={anomaly['z_score']}")
```""",

    "vision": """Document Analysis Complete.

**Structural Analysis:**
- Document Type: Engineering Inspection Report (PDF, 24 pages)
- Detected Elements: 3 data tables, 2 technical diagrams, 1 flow chart, 47 text sections

**Extracted Tables:**
| Table | Title | Rows | Columns |
|-------|-------|------|---------|
| T-1 | Equipment Defect Log | 18 | 6 |
| T-2 | Inspection Checklist Results | 34 | 4 |
| T-3 | Maintenance Schedule | 12 | 5 |

**Defect Summary (from Table T-1):**
- Critical defects: 3 (immediate action required)
- Major defects: 7 (action within 30 days)
- Minor defects: 8 (scheduled maintenance)
- Category breakdown: Mechanical (9), Electrical (4), Structural (2), Other (3)

**Key Findings:**
1. Pump Unit P-07 shows bearing wear beyond acceptable limits (Severity: CRITICAL)
2. Control Panel CP-03 has exposed wiring — safety hazard flagged
3. Cooling tower CT-02 requires valve replacement within 30 days

**Output Generated:** `inspection_summary.xlsx` — 3 sheets: Defect Log, Category Analysis, Action Plan""",

    "text": """**Procurement Approval Process — High-Value Items**

*Source: Procurement_Policy_v3.pdf, Section 4.2 — High-Value Procurement Threshold: ₹10,00,000+*

**Process Overview:**

1. **Requisition Initiation** (Department Head)
   - Raise Purchase Requisition (PR) in ERP system
   - Attach technical specifications and vendor quotations (minimum 3)
   - Assign budget code from approved Annual Procurement Plan

2. **Technical Evaluation** (Technical Committee)
   - Minimum 3 registered vendors must be invited
   - Technical Evaluation Committee (TEC) reviews within 7 working days
   - TEC report submitted with scoring matrix

3. **Financial Approval** (Finance & Accounts)
   - Finance validates budget availability
   - For items > ₹50L: Additional CFO sign-off required
   - Comparative statement prepared and certified

4. **Competent Authority Approval**
   - Up to ₹25L: Divisional Head
   - ₹25L–₹1Cr: Director/GM
   - Above ₹1Cr: Board Committee approval required

5. **Purchase Order Issuance**
   - PO raised only after all approvals documented
   - Vendor notified with delivery timeline
   - All documents stored in DMS with audit trail

*Reference: SIH_Org Procurement_Policy_v3.pdf, Sections 4.2, 4.3, 5.1*""",

    "rag": """**Answer based on retrieved internal documents:**

According to **SOP_Manual_v2.pdf** (Section 3.2 — Standard Operating Procedures for Document Approval):

The approval workflow consists of the following mandatory steps:

**Step 1 — Draft Preparation**
The originating department prepares the document draft using the approved template (Form-DOC-001). All technical content must be reviewed by the subject matter expert before submission.

**Step 2 — Departmental Review (2 working days)**
The Department Manager conducts an initial review for completeness, accuracy, and compliance with organizational standards.

**Step 3 — Cross-functional Review (if applicable)**
Documents affecting multiple departments require sign-off from all relevant HODs within 5 working days.

**Step 4 — Quality Assurance Check**
The QA department verifies the document against ISO 9001:2015 requirements and flags any non-conformances.

**Step 5 — Final Approval**
Competent Authority (as per Delegation of Powers matrix) provides final approval via digital signature in the DMS.

**Retention:** Approved documents are retained for a minimum of 7 years per Records Management Policy.

*Sources: SOP_Manual_v2.pdf §3.2, Records_Management_Policy.pdf §8.1*""",

    "analysis": """**Engineering Report Analysis — Executive Summary**

**Report:** Equipment Inspection Q3 2025 | **Analyzed:** 31-Aug-2026

**Overall Equipment Health Score: 72/100** (Requires Attention)

**Critical Findings:**
| Priority | Equipment ID | Issue | Recommended Action | Timeline |
|----------|-------------|-------|-------------------|----------|
| 🔴 CRITICAL | P-07 | Bearing wear >80% limit | Immediate replacement | 48 hours |
| 🔴 CRITICAL | CP-03 | Exposed high-voltage wiring | Emergency isolation + repair | 24 hours |
| 🟡 MAJOR | CT-02 | Valve seal degradation | Replacement during next shutdown | 30 days |
| 🟡 MAJOR | HX-11 | Fouling index: 1.8 (limit: 1.5) | Chemical cleaning | 30 days |
| 🟢 MINOR | Pump station general | Lubrication intervals overdue | Routine maintenance | 90 days |

**Cost Estimate:**
- Critical repairs: ₹4,20,000
- Major repairs: ₹1,85,000
- Preventive maintenance: ₹65,000
- **Total estimated: ₹6,70,000**

**Compliance Status:** 3 items non-compliant with IS 14846 safety standards

*Excel output: 3 sheets — Summary, Defect Log, Action Plan with responsible persons and deadlines*"""
}

# ─── Model routing logic ──────────────────────────────────────────────────────

MODEL_ROUTING = {
    "code": {
        "model": "DeepSeek-Coder-V2-Lite",
        "reason": "Task requires code generation and algorithmic reasoning",
        "vram": "8.4 GB",
        "size": "15.7B params (Q4_K_M)"
    },
    "vision": {
        "model": "Qwen2.5-VL-7B",
        "reason": "Task involves document/image visual understanding and OCR",
        "vram": "6.8 GB",
        "size": "7.6B params (Q4_K_M)"
    },
    "text": {
        "model": "Qwen2.5-7B",
        "reason": "Task requires structured text generation and reasoning",
        "vram": "5.2 GB",
        "size": "7.2B params (Q4_K_M)"
    },
    "rag": {
        "model": "Phi-3-Mini-4K",
        "reason": "RAG retrieval task — efficient model suited for grounded Q&A",
        "vram": "2.4 GB",
        "size": "3.8B params (Q4_K_M)"
    },
    "analysis": {
        "model": "Qwen2.5-7B",
        "reason": "Analytical task requires structured output and table comprehension",
        "vram": "5.2 GB",
        "size": "7.2B params (Q4_K_M)"
    }
}

REACT_LOOPS = {
    "code": [
        {"thought": "I need to write a Python script that parses JSON sensor logs. First, I'll plan the data structure."},
        {"action": "analyze_requirements(task_description)", "observation": "Requirements: JSON input, statistical anomaly detection, configurable threshold, structured output"},
        {"thought": "I'll use numpy for statistical calculations (z-score method). Let me structure the function signature."},
        {"action": "generate_code_skeleton(language='python', libraries=['json', 'numpy', 'pathlib'])", "observation": "Code scaffold generated with docstrings and type hints"},
        {"thought": "Now implementing the core anomaly detection logic using z-score threshold."},
        {"action": "implement_core_logic(method='z-score', threshold=3.0)", "observation": "Core logic complete. 47 lines generated."},
        {"thought": "Adding error handling, logging, and CLI interface for usability."},
        {"action": "add_error_handling() + add_cli_interface()", "observation": "Complete script: 89 lines, fully documented"},
        {"action": "validate_code_syntax()", "observation": "✓ Syntax valid | ✓ No security issues | ✓ PEP8 compliant"}
    ],
    "vision": [
        {"thought": "This appears to be a PDF engineering report. I'll use OCR to extract text and table structures."},
        {"action": "OCR_Tool(file='inspection_report.pdf', mode='full')", "observation": "Extracted: 24 pages, 47 text blocks, 3 tables detected"},
        {"thought": "Tables detected. Let me extract and parse the structured data from each table."},
        {"action": "extract_tables(document, method='pdfplumber')", "observation": "Table T-1: 18×6 (Defect Log), T-2: 34×4 (Checklist), T-3: 12×5 (Schedule)"},
        {"thought": "I need to categorize defects by severity and type for the Excel summary."},
        {"action": "classify_defects(table_data=T1_data, schema='severity+category')", "observation": "Classified: 3 Critical, 7 Major, 8 Minor across 4 categories"},
        {"thought": "Generating Excel output with multiple sheets and formatting."},
        {"action": "generate_excel(sheets=['Summary', 'Defect Log', 'Action Plan'], format='styled')", "observation": "File generated: inspection_summary.xlsx (142 KB)"}
    ],
    "text": [
        {"thought": "The user is asking about high-value procurement approval. Let me search the knowledge base first."},
        {"action": "RAG_search(query='high value procurement approval process', k=5)", "observation": "Retrieved 5 chunks from Procurement_Policy_v3.pdf (Sections 4.2, 4.3, 5.1)"},
        {"thought": "The policy document has clear step-by-step procedures. Let me structure this into a readable response."},
        {"action": "structure_response(source_chunks=5, format='numbered_steps')", "observation": "Response structured: 5 approval stages with thresholds identified"},
        {"thought": "Adding specific monetary thresholds and responsible authorities from the policy."},
        {"action": "extract_thresholds(policy_sections=['4.2', '5.1'])", "observation": "Thresholds: ₹10L (base), ₹25L (Div Head), ₹1Cr (Board) — all captured"},
        {"action": "format_final_response(citations=True, format='markdown')", "observation": "Response complete with section references and source citations"}
    ],
    "rag": [
        {"thought": "This is a document-grounded Q&A task. Let me retrieve relevant SOP sections."},
        {"action": "ChromaDB_query(collection='internal_docs', query=task, k=3, threshold=0.82)", "observation": "3 chunks retrieved | Top similarity: 0.94 | Source: SOP_Manual_v2.pdf §3.2"},
        {"thought": "Retrieved context is highly relevant. Generating grounded answer with citations."},
        {"action": "generate_answer(context=chunks, grounding='strict', citations=True)", "observation": "Answer generated — all claims traceable to source documents"},
        {"action": "verify_hallucination_check(answer, sources)", "observation": "✓ No hallucinated facts | ✓ All citations valid"}
    ],
    "analysis": [
        {"thought": "I need to analyze this engineering inspection PDF and create a structured Excel summary."},
        {"action": "OCR_Tool(file='engineering_report.pdf', extract='tables+text')", "observation": "Extracted: 18 defect records, 5 equipment categories, 34 inspection items"},
        {"thought": "Categorizing defects by severity (Critical/Major/Minor) and equipment type."},
        {"action": "classify_and_aggregate(data=defect_records, by=['severity', 'category'])", "observation": "Aggregation complete: 3 Critical, 7 Major, 8 Minor items identified"},
        {"thought": "Now computing cost estimates based on historical repair data in the knowledge base."},
        {"action": "RAG_search(query='repair cost estimates mechanical electrical', k=3)", "observation": "Cost data retrieved from Maintenance_Budget_2025.pdf — estimates populated"},
        {"thought": "Generating multi-sheet Excel workbook with summary, detail, and action plan."},
        {"action": "generate_excel(sheets=['Executive Summary', 'Defect Log', 'Action Plan'], style='corporate')", "observation": "File ready: inspection_summary.xlsx (187 KB, 3 sheets)"}
    ]
}

# ─── Classification logic ─────────────────────────────────────────────────────

def classify_task(task_text: str, has_file: bool = False) -> str:
    """Classify task type based on keywords and context."""
    text_lower = task_text.lower()
    
    # Code generation signals
    code_keywords = ["code", "script", "function", "python", "program", "write a", "implement", 
                     "algorithm", "parse", "class", "module", "api", "json parser", "data parser"]
    if any(w in text_lower for w in code_keywords):
        return "code"
    
    # Vision/document analysis signals
    vision_keywords = ["image", "diagram", "scan", "ocr", "visual", "chart", "photo", 
                       "drawing", "figure", "extract from", "inspection report", "engineering report"]
    if any(w in text_lower for w in vision_keywords) or (has_file and "excel" in text_lower):
        return "vision"
    
    # RAG / Q&A signals
    rag_keywords = ["according to", "what is the", "policy", "sop", "approval process", 
                    "procedure", "regulation", "guideline", "based on", "from our", "answer"]
    if any(w in text_lower for w in rag_keywords):
        return "rag"
    
    # Analysis + file
    if has_file or any(w in text_lower for w in ["analyze", "analysis", "report", "summary", "excel", "defect"]):
        return "analysis"
    
    return "text"


def get_model_info(task_type: str) -> dict:
    """Get model routing info for a given task type."""
    return MODEL_ROUTING.get(task_type, MODEL_ROUTING["text"])


def get_demo_response(task_type: str) -> str:
    """Get the pre-written demo response for a task type."""
    return DEMO_RESPONSES.get(task_type, DEMO_RESPONSES["text"])


def get_react_loop(task_type: str) -> list:
    """Get the ReAct loop trace for a task type."""
    return REACT_LOOPS.get(task_type, REACT_LOOPS["text"])


def get_pii_check_result() -> dict:
    """Simulate PII detection result — always clean for demo."""
    return {
        "pii_detected": False,
        "entities_scanned": random.randint(120, 340),
        "scan_duration_ms": random.randint(18, 45),
        "patterns_checked": ["email", "phone", "aadhaar", "pan", "bank_account", "ip_address", "name"],
        "result": "CLEAN"
    }


def get_rag_results(task_type: str) -> dict:
    """Simulate RAG retrieval results."""
    rag_data = {
        "code": {
            "retrieved": False,
            "reason": "Code generation task — RAG not applicable",
            "chunks": 0
        },
        "vision": {
            "retrieved": True,
            "collection": "engineering_docs",
            "chunks": 2,
            "sources": ["Equipment_Maintenance_Standards.pdf", "ISO_13374_Condition_Monitoring.pdf"],
            "top_similarity": 0.87,
            "query_time_ms": 43
        },
        "text": {
            "retrieved": True,
            "collection": "policy_docs",
            "chunks": 3,
            "sources": ["Procurement_Policy_v3.pdf"],
            "top_similarity": 0.94,
            "query_time_ms": 38
        },
        "rag": {
            "retrieved": True,
            "collection": "internal_docs",
            "chunks": 3,
            "sources": ["SOP_Manual_v2.pdf"],
            "top_similarity": 0.94,
            "query_time_ms": 31
        },
        "analysis": {
            "retrieved": True,
            "collection": "engineering_docs",
            "chunks": 3,
            "sources": ["SOP_Manual_v2.pdf", "Maintenance_Budget_2025.pdf"],
            "top_similarity": 0.89,
            "query_time_ms": 52
        }
    }
    return rag_data.get(task_type, rag_data["text"])
