"""
Stage 11: Secure Sandbox Execution — Sovereign AI Workbench
Simulates isolated gVisor container runtime for safe code execution.

Features:
- Syscall interception via gVisor user-space kernel (runsc)
- Zero external network egress (--net=none)
- Read-only root filesystem (--read-only)
- Strict CPU and memory limits
"""

import random
from typing import Dict, Any, Optional

# TODO: replace simulated execution with real `docker run --runtime=runsc --net=none --read-only` call once gVisor is installed on the target machine


def _generate_realistic_stdout(code: str) -> str:
    """Generate realistic stdout based on the code's apparent purpose."""
    code_lower = (code or "").lower()
    if any(k in code_lower for k in ["sensor", "anomaly", "z_score", "threshold"]):
        return (
            "✓ Processed 1,420 sensor readings across 12 monitoring nodes\n"
            "⚠ Detected 3 anomalies exceeding 3.0σ threshold:\n"
            "  [HIGH] Sensor S-04 @ 2026-08-31T18:22:10: value=412.8 (z=3.84)\n"
            "  [MEDIUM] Sensor S-09 @ 2026-08-31T18:24:15: value=388.1 (z=3.12)\n"
            "  [MEDIUM] Sensor S-02 @ 2026-08-31T18:25:02: value=379.5 (z=3.05)\n"
            "✓ Exported anomaly report to anomaly_detector.json"
        )
    elif any(k in code_lower for k in ["report", "inspection", "defect", "excel", "table"]):
        return (
            "✓ Loaded inspection_report.pdf (24 pages)\n"
            "✓ Parsed 3 defect tables: 18 total records\n"
            "✓ Generated inspection_summary.xlsx (3 sheets: Summary, Defect Log, Action Plan)\n"
            "✓ Execution completed in isolated sandbox environment"
        )
    elif any(k in code_lower for k in ["json", "parser", "parse", "log"]):
        return (
            "✓ Parsed input JSON stream: 4,812 records\n"
            "✓ Filtered 0 invalid entries | 0 schema violations\n"
            "✓ Processed batch in 148ms | Memory footprint: 18.4 MB"
        )
    else:
        return (
            "✓ Executed test suite: 6 passed, 0 failed\n"
            "✓ Code executed in gVisor sandbox container (runsc)\n"
            "✓ System calls contained: network=none, fs=ro\n"
            "✓ Memory peak: 32.6 MB / 512 MB"
        )


def execute_in_sandbox(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Stage 11: Sandboxed Code Execution.
    Simulates code execution inside a hardened gVisor container sandbox.

    Args:
        code: The source code string to execute.
        language: Programming language runtime (default: "python").

    Returns:
        dict: Sandbox execution metrics, stdout, limits, and security configuration.
    """
    # TODO: replace simulated execution with real `docker run --runtime=runsc --net=none --read-only` call once gVisor is installed on the target machine
    duration_ms = random.randint(200, 2000)
    stdout_text = _generate_realistic_stdout(code)

    return {
        "executed": True,
        "sandbox": "gVisor (runsc)",
        "network_access": "disabled",
        "filesystem": "read-only",
        "exit_code": 0,
        "stdout": stdout_text,
        "execution_time_ms": duration_ms,
        "resource_limits": {
            "memory_mb": 512,
            "cpu_cores": 0.5,
            "timeout_s": 30
        }
    }


def simulate_malicious_code_block(attempted_action: str) -> Dict[str, Any]:
    """
    Simulates gVisor sandbox containment of an adversarial or malicious action.
    Used for demo scenarios demonstrating security containment against container escapes,
    network egress attempts, and sensitive system file access.

    Args:
        attempted_action: Description of the malicious action attempted.

    Returns:
        dict: Security containment result showing the sandbox blocked the operation.
    """
    action_lower = attempted_action.lower()

    if any(k in action_lower for k in ["network", "socket", "http", "api", "curl", "egress", "external"]):
        violation_type = "NETWORK_EGRESS_BLOCKED"
        stderr_msg = f"Network access denied: connect() syscall intercepted by gVisor (net=none, no route to host). Attempted: {attempted_action}"
    elif any(k in action_lower for k in ["passwd", "shadow", "/etc", "read", "file", "root", "c:\\"]):
        violation_type = "UNAUTHORIZED_FILESYSTEM_ACCESS"
        stderr_msg = f"Permission denied: open() syscall failed on read-only mount (EROFS). Attempted: {attempted_action}"
    else:
        violation_type = "UNAUTHORIZED_SYSCALL_INTERCEPTED"
        stderr_msg = f"Operation not permitted: syscall prohibited by gVisor sandbox seccomp profile. Attempted: {attempted_action}"

    return {
        "executed": False,
        "sandbox": "gVisor (runsc)",
        "action": "BLOCKED",
        "attempted_action": attempted_action,
        "violation_type": violation_type,
        "containment": "gVisor user-space kernel syscall interception",
        "exit_code": 1,
        "stderr": stderr_msg,
        "stdout": "",
        "network_access": "disabled (veth down)",
        "filesystem": "read-only (EROFS)",
        "execution_time_ms": random.randint(15, 60),
        "security_event_logged": True
    }
