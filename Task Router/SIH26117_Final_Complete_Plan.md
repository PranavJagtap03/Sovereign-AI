# SIH 26117 — Final Complete Plan (Explained From Zero)
## Sovereign On-Premise Agentic AI Workbench for Confidential Industrial Work

---

## PART 1: THE BASICS — What Are We Even Building?

### 1.1 What problem are we solving?

Imagine a defense factory, a pharma company, or a power plant. They have huge amounts of confidential data — engineering blueprints, chemical formulas, machine inspection photos, maintenance logs. They'd love to use AI (like ChatGPT) to help analyze this stuff — read documents, spot defects in images, answer questions.

**The problem:** They CANNOT send this data to ChatGPT, Google, or any cloud AI. Why?
- The data is confidential/classified — sending it to an external company's servers is a security risk and often illegal (defense secrets, patient data, etc.)
- Indian law (DPDP Act) and defense rules require this kind of sensitive data to stay entirely inside the organization's own computers — nothing leaves the building, not even to "the cloud."

**So what do they need instead?** An AI system that:
1. Runs entirely on their own local computers (no internet needed, no data ever leaves)
2. Can understand text AND images/documents (called "multimodal")
3. Can actually *do things* — not just chat, but take actions like running calculations, looking things up, filling forms (called "agentic")
4. Uses AI models that are free and open ("open-weight") instead of paying a company like OpenAI, since you can't use their cloud anyway

This is called a **"Sovereign On-Premise Agentic AI Workbench"** — sovereign meaning "fully under your own control," on-premise meaning "runs on your own hardware," agentic meaning "can take actions, not just talk."

### 1.2 What's our specific plan?

We're building a **smaller working demo** of this idea — not the whole enterprise system, just enough to prove the concept works. Our chosen demo scenario:

**"An AI assistant that inspects industrial engineering photos/documents, spots problems, calculates safety tolerances, and does all of this completely offline, safely, and with a full record of everything it did."**

Think of it like a very smart, very secure inspector-assistant that a factory could actually trust with its secrets.

### 1.3 Why does SECURITY matter so much here (my specific job)?

Here's the key insight: giving an AI system the ability to *act* (not just talk) is powerful but dangerous. If someone tricks the AI into doing something bad — like running a harmful command, or leaking private data, or approving something it shouldn't — that's a real problem, not just a wrong chat answer.

So my job is: **build a security "cage" around the AI** that makes sure even if someone tries to trick it, nothing bad actually happens. This is the part judges will find genuinely impressive if done well, because most hackathon teams skip it entirely or fake it.

---

## PART 2: THE BUILDING BLOCKS (Explained Simply)

Before the workflow, let's understand the 4 main pieces of the system:

| Piece | What it is, in plain words |
|---|---|
| **The AI Model** | The actual "brain" — a free, downloadable AI (Qwen2.5-VL) that can read text and look at images, like a mini ChatGPT that runs on your own computer |
| **The Agent Framework** | The "manager" that lets the AI brain plan multi-step tasks and call tools (e.g., "first read the image, then look up the manual, then calculate the answer") |
| **The Security Layer** | Our main contribution — a set of checkpoints that inspect everything going in and out, so nothing malicious gets through |
| **The Dashboard** | The screen where a human sees what's happening — uploads a document, sees the AI's answer, sees the security checks happening live |

---

## PART 3: THE FULL WORKFLOW (Step by Step, Beginner-Friendly)

Here's literally what happens when someone uses our system, from start to finish:

### STEP 0: Setup (before anyone uses it)
- We download the AI model (Qwen2.5-VL) onto our own computer — once downloaded, it never needs the internet again.
- We check the model's "digital fingerprint" (a cryptographic hash) to make sure nobody tampered with the file before we downloaded it. *(This matters because a hacked AI model file could contain hidden malicious code — checking the fingerprint is like checking a wax seal on a letter.)*

### STEP 1: A user submits something
- Example: a factory inspector uploads a photo of a machine part, and asks "Is this component within safety tolerance?"
- This input (text + image) is the very first thing that enters our system.

### STEP 2: SECURITY CHECKPOINT #1 — "Is this input trying to trick the AI?"
- **What happens:** Before the image/text reaches the AI brain, we run it through a scanner.
- **Why:** Attackers can hide secret instructions inside images (invisible text, weird patterns) or inside documents, trying to trick the AI into ignoring its rules — this is called "prompt injection." It's like someone slipping a fake note into a stack of real paperwork.
- **How we catch it:** We run OCR (text-reading software) on the image to pull out any hidden text, then run BOTH the visible prompt and the hidden text through a "prompt injection detector" — a small pre-built AI model whose only job is spotting these tricks.
- **Result:** If something looks suspicious, we block it right here — the main AI brain never even sees it.

### STEP 3: SECURITY CHECKPOINT #2 — "Does this contain private information?"
- **What happens:** We scan the (now-cleared) input for personal details — names, phone numbers, ID numbers.
- **Why:** Even in a legitimate document, there might be an employee's name or personal info that shouldn't be stored or processed unnecessarily — Indian data protection law (DPDP Act) requires minimizing this.
- **How:** A tool called Presidio automatically finds and blacks out (masks) this kind of information before it goes any further.

### STEP 4: THE AI BRAIN THINKS
- **What happens:** The cleaned, safe input finally reaches Qwen2.5-VL, our AI model.
- It "looks" at the image, reads the question, and decides what to do — maybe it decides "I need to calculate a tolerance measurement, so I'll write a small calculation and run it."
- This is where the actual intelligence happens — but everything *around* it (the steps before and after) is what keeps it safe.

### STEP 5: SECURITY CHECKPOINT #3 — "Does a second, independent AI agree this action is safe?" (Guardian Agent)
- **What happens:** Before the AI's proposed action (e.g., "run this calculation" or "tell the user this part is safe") actually happens, a SECOND, separate AI reviews it independently.
- **Why:** This is like having a second doctor double-check a diagnosis. The main AI might be overconfident or wrong, and we don't want to just trust it blindly — especially for something like "this equipment is safe to use."
- **How:** The Guardian Agent gets the proposed action + the reasoning behind it, and independently judges: does this make sense? Is it within allowed limits? If the main AI seems to be making a risky or overconfident claim, the Guardian flags it for a HUMAN to review instead of letting it happen automatically.

### STEP 6: SECURITY CHECKPOINT #4 — "Is this specific action allowed and correctly formatted?"
- **What happens:** If the AI wants to run a tool (like a calculation script), we check the exact technical details — right format, right size, no sneaky attempts to access files it shouldn't (like trying to read `/etc/passwd`, a sensitive system file).
- **Why:** Even a "safe-sounding" action can be secretly dangerous if it's asking for the wrong file path or too much data — this step catches technical tricks.

### STEP 7: SECURITY CHECKPOINT #5 — "Is the AI stuck in a loop or using too many resources?"
- **What happens:** We track how many steps and how much time the AI has spent on this one task.
- **Why:** Sometimes a trick can make an AI get stuck repeating an action forever, slowing down or crashing the whole system (this is called a Denial-of-Service attack). We set a limit — if it's exceeded, we stop the task automatically.

### STEP 8: THE ACTUAL EXECUTION — "Run this code, but in a locked box"
- **What happens:** If the AI needs to run actual code (like a calculation), it doesn't run directly on our real computer. Instead, it runs inside a "sandbox" — a completely isolated, temporary mini-computer-within-a-computer (using a tool called gVisor) that:
  - Has no internet/network access at all
  - Can't read or write to the real computer's files
  - Gets destroyed immediately after running
- **Why:** This is our safety net. Even if every previous check somehow failed and the AI tried to do something truly malicious (like trying to delete files or steal data), it's stuck inside this locked box and can't actually touch anything real.

### STEP 9: RECORDING EVERYTHING — The tamper-proof diary
- **What happens:** Every single step above — what was scanned, what was blocked or allowed, what the AI decided, what the sandbox returned — gets written down in a special log.
- **Why it's special:** Each log entry is "chained" to the previous one using cryptography (like a blockchain), so if anyone — even someone with admin access — tries to secretly edit or delete a past entry, the chain "breaks" and it's immediately obvious that tampering happened.
- **Why this matters for the real world:** Indian cybersecurity rules (CERT-In) require organizations to be able to prove exactly what happened during a security incident within 6 hours — this tamper-proof log makes that possible.

### STEP 10: SHOWING THE RESULT
- **What happens:** Finally, the safe, verified answer is shown to the user on a dashboard — along with a summary of what security checks passed, so the user can trust the answer wasn't influenced by any of the attacks we discussed.
- The dashboard also shows a "Risk Coverage Score" — literally a number (like "5 out of 5 attack types successfully blocked in our tests") that proves our security actually works, not just claims to.

---

## PART 4: THE FULL VISUAL WORKFLOW

```
   [User uploads image/document + question]
                    │
                    ▼
   ┌─────────────────────────────────────┐
   │ STEP 2: Prompt Injection Scanner     │ ← catches hidden tricks
   └─────────────────────────────────────┘
                    │ (cleared)
                    ▼
   ┌─────────────────────────────────────┐
   │ STEP 3: PII / Privacy Masker         │ ← removes personal info
   └─────────────────────────────────────┘
                    │ (cleared)
                    ▼
   ┌─────────────────────────────────────┐
   │ STEP 4: AI Brain (Qwen2.5-VL)        │ ← the actual intelligence
   └─────────────────────────────────────┘
                    │ (proposes an action)
                    ▼
   ┌─────────────────────────────────────┐
   │ STEP 5: Guardian Agent Review        │ ← second opinion, catches overconfidence
   └─────────────────────────────────────┘
                    │ (approved)
                    ▼
   ┌─────────────────────────────────────┐
   │ STEP 6: Tool-Call Format Check       │ ← catches technical tricks
   └─────────────────────────────────────┘
                    │ (valid)
                    ▼
   ┌─────────────────────────────────────┐
   │ STEP 7: Resource Budget Check        │ ← prevents infinite loops
   └─────────────────────────────────────┘
                    │ (within budget)
                    ▼
   ┌─────────────────────────────────────┐
   │ STEP 8: Locked Sandbox Execution     │ ← isolated, no real damage possible
   └─────────────────────────────────────┘
                    │ (result)
                    ▼
   ┌─────────────────────────────────────┐
   │ STEP 9: Tamper-Proof Audit Log       │ ← records everything, unchangeable
   └─────────────────────────────────────┘
                    │
                    ▼
   [Dashboard shows: Answer + Security Score]
```

---

## PART 5: WHY THIS DESIGN IS SMART (The "Advanced" Explanation)

Now that you understand the basic flow, here's the deeper reasoning:

1. **Defense in depth:** No single checkpoint has to be perfect. Even if a clever attack slips past the injection scanner, the Guardian Agent might catch it. Even if it slips past that too, the sandbox ensures it can't do real damage anyway. This layered approach is a core cybersecurity principle — never rely on just one wall.

2. **Independent verification (Guardian Agent):** This is our most advanced idea. Instead of just trusting the main AI's own judgment about whether its actions are safe, we have a *separate* AI system double-check it — because an AI can be tricked into believing its own bad reasoning is correct. Having an independent check is the same principle as having two pilots in a cockpit, or two signatures required for a bank transaction.

3. **Everything is provable, not just claimed:** The tamper-proof log and the Risk Coverage Score mean we're not just saying "trust us, it's secure" — we can mathematically prove what happened and measure how well our defenses worked. This is what real enterprise/government systems require (and what most hackathon projects skip).

4. **It's built from named, published research:** Every threat we defend against and every defense we use is based on real academic security research (AGENTSAFE from IBM, ATFAA/SHIELD from AWS, and a cybersecurity survey from university researchers) — meaning our system isn't guessing what attacks might happen, it's built against a documented, real threat model.

---

## PART 6: TECH STACK — What Software We Actually Use (All Free)

| Component | Tool | Cost |
|---|---|---|
| AI Brain | Qwen2.5-VL-7B-Instruct (from HuggingFace) | Free (Apache 2.0 license) |
| Model Serving | vLLM | Free, open-source |
| Injection Detection | LLM Guard / Meta Prompt Guard | Free |
| PII Masking | Microsoft Presidio | Free |
| Sandboxing | gVisor (runsc) + Docker | Free |
| Audit Logging | Python (hashlib/hmac) + SQLite | Free, built-in |
| Agent Orchestration | LangGraph | Free, open-source |
| Vector Database (for document search) | LanceDB | Free, open-source |
| Dashboard | Streamlit or React/Next.js | Free |

**The only real hardware requirement:** a computer with a GPU (16GB+ VRAM) to run the AI model at reasonable speed. Everything else runs on any normal laptop.

---

## PART 7: BUILD TIMELINE (36-48 Hour Hackathon)

| Phase | Hours | What Gets Built |
|---|---|---|
| Phase 1 | 0-12 | Set up AI model + vLLM serving; verify model file integrity (Step 0, 4) |
| Phase 2 | 12-24 | Build Steps 2-3 (injection scanner + PII masker) and Step 6 (schema validation) |
| Phase 3 | 24-36 | Build Step 8 (gVisor sandbox) + Step 7 (resource budget guard) |
| Phase 4 | 36-44 | Build Step 5 (Guardian Agent) + Step 9 (audit log) — these are your standout features |
| Phase 5 | 44-48 | Build dashboard, write Risk Coverage Score logic, rehearse demo |

---

## PART 8: THE DEMO — What You'll Show Judges

1. Show a normal, safe question → clean answer, all checkpoints shown passing on screen.
2. **Attack demo 1:** Try a hidden prompt injection in text → show it gets blocked at Step 2.
3. **Attack demo 2:** Try a hidden instruction inside an uploaded image → show OCR + scanner catches it.
4. **Attack demo 3:** Try to make the AI run dangerous code → show it's safely contained in the sandbox (Step 8), no real damage.
5. **Attack demo 4:** Try to tamper with a past log entry → show the tamper-proof chain detects it (Step 9).
6. **Attack demo 5 (your standout moment):** Make the AI give an overconfident, wrong safety recommendation → show the **Guardian Agent independently catches it** and escalates to a human instead of letting it auto-execute.
7. **Close:** Show the Risk Coverage Score (e.g., "5/5 attack types successfully caught") and a simple table showing every named threat category (from the ATFAA research) that your system defends against.

---

## PART 9: THE ONE-LINE PITCH (if you only remember one thing)

*"We built an AI assistant that can safely work with a company's most confidential documents and images, entirely on their own computers with no internet — and unlike most AI security demos which just claim to be safe, ours proves it with a second independent AI double-checking every decision and a tamper-proof record of everything that happened."*
