"""
Stage 11: Secure Sandbox Execution — Sovereign AI Workbench

Simulates isolated gVisor container runtime (runsc) for safe code execution.
Stays simulated per architecture decision — real gVisor integration requires
`docker run --runtime=runsc --net=none --read-only` on the target machine.

TODO (future): replace with real docker/gVisor call once runtime is installed.

Source: execute_in_sandbox, simulate_malicious_code_block
        from sandbox_deprecated.py (unchanged, stays simulated).
"""

from sandbox_deprecated import (  # noqa: F401
    execute_in_sandbox,
    simulate_malicious_code_block,
)

__all__ = ["execute_in_sandbox", "simulate_malicious_code_block"]
