# Sovereign AI Workbench

> **Smart India Hackathon (SIH 2026) | Team Code: 201**  
> **100% Air-Gapped, Zero-Data-Egress Multi-Model Agentic Platform with 13-Stage Defense-in-Depth**

---

## 🛡️ Executive Summary

The **Sovereign AI Workbench** is an enterprise-grade AI system designed for high-security, defense, and public-sector enclaves where cloud connectivity is strictly prohibited. It guarantees **0 external API calls** and **0 outbound bytes**, running multi-model agentic workflows on local hardware while subjecting every prompt and action to an end-to-end **13-Stage Sovereign Security Pipeline**.

---

## 🏛️ The 13-Stage Sovereign Pipeline

Every incoming user task passes sequentially through 13 sovereign security and reasoning stages before deliverable release:

```
[User Task]
    │
    ▼
[Stage 1: Prompt Injection Scanner] ─────────► [🛑 HALT on Jailbreak / Injection]
    │
    ▼
[Stage 2: Live PII Sanitizer] ───────────────► [🧹 Redacts Email, Phone, Aadhaar, PAN]
    │
    ▼
[Stage 3: Task Classification & Routing] ────► [🏷️ Routes to Domain Model]
    │
    ▼
[Stage 4: Authorization & RBAC Filter] ──────► [🔑 Filters Documents by Role Clearance]
    │
    ▼
[Stage 5: Local Model Selection] ────────────► [🤖 Allocates Local Model to VRAM]
    │
    ▼
[Stage 6: Company Brain Retrieval (RAG)] ────► [📚 Local ChromaDB Semantic Retrieval]
    │
    ▼
[Stage 7: Primary Agent ReAct Loop] ─────────► [⚙️ Autonomous Reasoning (Thought/Action)]
    │   ├── [Stage 9: Tool Call Validator] ──► [🔧 Validates Tool Schema & Path Traversal]
    │   ├── [Stage 10: Resource Budget] ─────► [⏱️ Enforces Step (15) & Time (30s) Budget]
    │   └── [Stage 11: gVisor Secure Sandbox]► [📦 Kernel-Isolated Container (net=none, fs=ro)]
    │
    ▼
[Stage 8: Guardian Agent Review] ────────────► [⏸️ Phi-3-Mini Escalates High-Impact Claims]
    │
    ▼
[Stage 12: Air-Gapped Deliverable Vault] ────► [🔐 AES-256-GCM Vault / Quarantine Hold]
    │
    ▼
[Stage 13: Cryptographic Hash Chain Audit] ──► [⛓️ HMAC-SHA256 Tamper-Evident Ledger]
    │
    ▼
[Verified Sovereign Deliverable]
```

---

## 🎯 Attack-to-Stage Mapping Matrix

The workbench includes automated live containment for **9 distinct threat vectors**, verifiable via one-click preset buttons during judging:

| # | Threat / Attack Class | Intercepting Stage | Defense Mechanism | Preset Demo Button | Expected Live Verdict |
|---|---|---|---|---|---|
| 1 | **Prompt Injection (Text)** | **Stage 1**: Input Guard | Regex & semantic jailbreak scanner (`ignore previous instructions`, `system prompt`, hidden commands) | `Attack: Prompt Injection (text)` | 🛑 **BLOCKED**: Execution halted immediately; zero model tokens consumed. |
| 2 | **Prompt Injection (Image/OCR)** | **Stage 1**: Input Guard | Multimodal OCR text analysis scanning for visual prompt override vectors | `Attack: Prompt Injection (image)` | 🛑 **BLOCKED**: Visual jailbreak vector caught before downstream vision reasoning. |
| 3 | **PII Leakage** | **Stage 2**: PII Sanitizer | Live query regex tokenization for emails, phone numbers, Aadhaar (12-digit), and PAN (10-char) | `Attack: PII Leakage` | 🧹 **SANITIZED**: Tokens masked with `[REDACTED-*]`; downstream model never sees raw PII. |
| 4 | **Unauthorized Document Access** | **Stage 4**: RBAC Filter | Hierarchical clearance scale (`Internal` $\rightarrow$ `Restricted` $\rightarrow$ `Confidential` $\rightarrow$ `Highly Confidential`) | `Attack: Unauthorized Access` | 🚫 **RBAC FILTER**: Restricted documents filtered out for lower-clearance roles (e.g. Inspector). |
| 5 | **Overconfident AI Recommendation** | **Stage 8**: Guardian Agent | Independent model family (`Phi-3-Mini-4K`) scanning for high-impact phrases (`"safe to operate"`, `"approved"`) | `Attack: Overconfident Claim` | ⏸️ **ESCALATED**: Quarantine hold engaged; requires explicit human operator sign-off. |
| 6 | **Malformed Tool Call** | **Stage 9**: Tool Validator | Schema white-listing and strict path traversal detection (`../`, `/etc/`, `C:\Windows`) | `Attack: Malformed Tool Call` | 🛑 **BLOCKED**: ReAct loop halts immediately if illegal tools or traversal arguments are invoked. |
| 7 | **Resource Exhaustion (Infinite Loop)** | **Stage 10**: Budget Limiter | Hard compute thresholds: Max 15 reasoning steps and 30,000ms total loop elapsed time | `Attack: Resource Exhaustion` | ⏱️ **EXCEEDED**: Execution aborted at step 16 to protect system VRAM and compute resources. |
| 8 | **Malicious Code Execution** | **Stage 11**: Secure Sandbox | Containerized execution inside gVisor (`runsc`) sandbox with `--net=none` and read-only filesystem | `Attack: Malicious Code` | 📦 **CONTAINED**: Syscall virtualization prevents network access or local file tampering. |
| 9 | **Log Tampering** | **Stage 13**: Audit Hash Chain | Sequential HMAC-SHA256 signature chain ($H_i = \text{HMAC}(K, H_{i-1} \parallel T \parallel \text{JSON})$) | `Attack: Log Tampering` | 💥 **COMPROMISED**: Mathematical break detected at exact corrupted entry index. |

---

## 🔑 Role-Based Access Control (RBAC) Clearance Scale

Document sensitivity is enforced deterministically at **Stage 4** prior to vector retrieval:

| Role | Clearance Level | Accessible Document Classes | Example Allowed Docs |
|---|---|---|---|
| **Inspector** | `Internal` | Public procedures, general SOPs | `SOP_Manual_v2.pdf`, `Records_Management_Policy.pdf` |
| **Engineer** | `Restricted` | Technical blueprints, operations, employee HR data | `HR_Leave_Policy.pdf`, `Equipment_Inspection_Q3_2026.pdf` |
| **Manager** | `Confidential` | Security architecture, network topology, procurement | `Procurement_Policy_v3.pdf`, `Network_Security_Guidelines.pdf` |
| **Admin** | `Highly Confidential` | Executive directives, audit logs, system cryptographic keys | Full Unrestricted Access |

---

## 🤖 Local Model Routing Architecture

No third-party APIs (OpenAI, Anthropic, Google) are called. Models run strictly on-premise:

| Task Type | Assigned Local Model | Model Size | VRAM Allocation | Primary Role |
|---|---|---|---|---|
| **Document Analysis / Vision** | `Qwen2.5-VL-7B` | 7B Vision | 9.2 GB | Multimodal inspection, table parsing, diagram analysis |
| **Code Generation & Diagnostics** | `DeepSeek-Coder-V2-Lite` | 16B MoE | 11.5 GB | Python script generation, AST validation, anomaly detection |
| **Policy Q&A & Knowledge Base** | `Qwen2.5-7B` | 7B Instruct | 6.8 GB | High-speed semantic document retrieval & structured drafting |
| **Independent Guardian Agent** | `Phi-3-Mini-4K` | 3.8B Compact | 3.2 GB | Architectural diversity: independent safety review & human escalation |

---

## ⛓️ Cryptographic Hash-Chain Verification (Stage 13)

The audit log is an immutable hash-chained ledger:
- **Genesis Hash**: `0000000000000000000000000000000000000000000000000000000000000000`
- **Entry Hash Calculation**:
  $$\text{Hash}_i = \text{HMAC-SHA256}(\text{Key}, \text{Hash}_{i-1} \parallel \text{Timestamp} \parallel \text{CleanJSON}(\text{Details}))$$
- **Zero-PII Assurance**: Document content, raw passwords, and full PII are strictly excluded from audit records; only cryptographically hashed references, metadata, and redaction flags are stored.
- **Tamper Detection**: Altering any historical byte causes an irreversible signature mismatch detected during automatic chain-walking verification.

---

## 💻 Tech Stack & Infrastructure

- **Backend**: Python 3.14, FastAPI, Pydantic, python-docx, ChromaDB (offline), hashlib/hmac
- **Frontend**: React 19, Vite, Tailwind CSS, Framer Motion, Lucide Icons, Axios
- **Isolation & Security**: gVisor (`runsc`), iptables `DROP OUTPUT`, AES-256-GCM encryption

---

## 🚀 Quick Start Guide

### 1. Backend Setup
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate      # On Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

### 3. Run Automated Presets Test
```bash
cd backend
.\venv\Scripts\python.exe test_demo_presets.py
```
Outputs green `[PASS]` status across all 13 attack and capability scenarios.
