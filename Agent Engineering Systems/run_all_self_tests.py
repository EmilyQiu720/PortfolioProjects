#!/usr/bin/env python3
"""
Run all Agent Engineering Systems self-tests.

This script keeps portfolio validation simple: each project exposes a
dependency-light --self-test command, and this runner fails fast if any project
regresses.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECTS = [
    "tool_calling_agent_loop.py",
    "stateful_research_agent.py",
    "workflow_agent_orchestrator.py",
    "industrial_mcp_server.py",
    "agent_evaluation_harness.py",
    "production_agent_observability.py",
    "agent_security_guardrails.py",
    "advanced_agent_architecture.py",
    "agent_training_rl_lab.py",
    "agent_research_benchmark_lab.py",
]


def main() -> int:
    root = Path(__file__).resolve().parent
    failed = []
    for project in PROJECTS:
        print(f"==> {project}")
        result = subprocess.run([sys.executable, str(root / project), "--self-test"], text=True)
        if result.returncode != 0:
            failed.append(project)
    if failed:
        print("\nFailed projects:")
        for project in failed:
            print(f"- {project}")
        return 1
    print("\nAll Agent Engineering Systems self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
