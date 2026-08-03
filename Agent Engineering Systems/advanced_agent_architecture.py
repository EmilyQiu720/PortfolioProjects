#!/usr/bin/env python3
"""
Advanced Agent Architecture

This project demonstrates long-horizon agent architecture with planning,
search, reflection only when new evidence exists, critic/verifier review,
checkpointed workspace, task ledger, and multi-agent coordination.

Run:
  python advanced_agent_architecture.py --self-test
  python advanced_agent_architecture.py --run
"""

from __future__ import annotations

import argparse
import heapq
import json
import random
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


JsonObject = dict[str, Any]
DATA_DIR = Path(__file__).resolve().parent / "advanced_agent_architecture_data"
CHECKPOINT_DIR = DATA_DIR / "checkpoints"
ARTIFACT_DIR = DATA_DIR / "artifacts"


def ensure_dirs() -> None:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class TaskNode:
    task_id: str
    description: str
    role: str
    cost: int
    dependencies: list[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: str | None = None


@dataclass
class CandidatePlan:
    plan_id: str
    nodes: list[TaskNode]
    estimated_reward: float = 0.0
    critique: list[str] = field(default_factory=list)


@dataclass
class Workspace:
    run_id: str
    goal: str
    budget: int
    spent: int = 0
    ledger: list[JsonObject] = field(default_factory=list)
    shared_state: JsonObject = field(default_factory=dict)
    private_state: dict[str, JsonObject] = field(default_factory=dict)
    reflection_memory: list[str] = field(default_factory=list)
    artifact_paths: list[str] = field(default_factory=list)


class DependencyGraph:
    """Computes execution order and critical path from task dependencies."""

    def ready_nodes(self, nodes: list[TaskNode]) -> list[TaskNode]:
        done = {node.task_id for node in nodes if node.status == TaskStatus.DONE}
        return [node for node in nodes if node.status == TaskStatus.PENDING and all(dep in done for dep in node.dependencies)]

    def critical_path_cost(self, nodes: list[TaskNode]) -> int:
        by_id = {node.task_id: node for node in nodes}
        memo: dict[str, int] = {}

        def path_cost(task_id: str) -> int:
            if task_id in memo:
                return memo[task_id]
            node = by_id[task_id]
            if not node.dependencies:
                memo[task_id] = node.cost
            else:
                memo[task_id] = node.cost + max(path_cost(dep) for dep in node.dependencies)
            return memo[task_id]

        return max(path_cost(node.task_id) for node in nodes)


class Planner:
    """Combines hierarchical planning, beam search, and a tiny MCTS-like expansion."""

    def decompose(self, goal: str) -> list[TaskNode]:
        return [
            TaskNode("t1", "Collect defect evidence", "researcher", 2),
            TaskNode("t2", "Collect CAD alignment evidence", "tool_agent", 2),
            TaskNode("t3", "Rank root causes", "analyst", 3, ["t1", "t2"]),
            TaskNode("t4", "Verify claims against evidence", "verifier", 2, ["t3"]),
            TaskNode("t5", "Write final RCA artifact", "writer", 2, ["t4"]),
        ]

    def beam_search_plans(self, goal: str, width: int = 3) -> list[CandidatePlan]:
        base = self.decompose(goal)
        candidates = []
        for i in range(width):
            nodes = [TaskNode(**asdict(node)) for node in base]
            if i == 1:
                nodes.insert(2, TaskNode("t_extra", "Check model drift evidence", "model_agent", 2, ["t1"]))
            if i == 2:
                nodes = [node for node in nodes if node.task_id != "t2"]
            reward = self._estimate_reward(nodes)
            candidates.append(CandidatePlan(f"beam-{i}", nodes, reward))
        return sorted(candidates, key=lambda plan: plan.estimated_reward, reverse=True)

    def mcts_expand(self, plan: CandidatePlan, simulations: int = 8) -> CandidatePlan:
        best = plan
        for i in range(simulations):
            nodes = [TaskNode(**asdict(node)) for node in plan.nodes]
            if random.random() > 0.5 and not any(node.task_id == "t_safety" for node in nodes):
                nodes.append(TaskNode("t_safety", "Check safety and approval boundary", "critic", 1, ["t4"]))
            candidate = CandidatePlan(f"mcts-{i}", nodes, self._estimate_reward(nodes))
            if candidate.estimated_reward > best.estimated_reward:
                best = candidate
        return best

    def _estimate_reward(self, nodes: list[TaskNode]) -> float:
        roles = {node.role for node in nodes}
        coverage = sum(role in roles for role in ["researcher", "tool_agent", "analyst", "verifier", "writer"])
        cost = sum(node.cost for node in nodes)
        return coverage * 2.0 - cost * 0.2


class CriticVerifier:
    """Critiques only against plan structure and execution evidence."""

    REQUIRED_ROLES = {"researcher", "tool_agent", "analyst", "verifier", "writer"}

    def critique_plan(self, plan: CandidatePlan) -> CandidatePlan:
        roles = {node.role for node in plan.nodes}
        missing = sorted(self.REQUIRED_ROLES - roles)
        if missing:
            plan.critique.append(f"Missing roles: {missing}")
        if len({node.task_id for node in plan.nodes}) != len(plan.nodes):
            plan.critique.append("Duplicate task IDs.")
        return plan

    def verify_result(self, workspace: Workspace) -> bool:
        evidence = workspace.shared_state.get("evidence", [])
        final = workspace.shared_state.get("final", "")
        return bool(evidence) and "root cause" in final.lower()


class MultiAgentCoordinator:
    """Supervisor-worker coordination with shared/private state and deadlock detection."""

    def __init__(self) -> None:
        self.graph = DependencyGraph()

    def execute(self, plan: CandidatePlan, workspace: Workspace) -> None:
        seen_no_progress = 0
        while any(node.status == TaskStatus.PENDING for node in plan.nodes):
            ready = self.graph.ready_nodes(plan.nodes)
            if not ready:
                seen_no_progress += 1
                if seen_no_progress >= 2:
                    workspace.ledger.append({"event": "deadlock_detected"})
                    for node in plan.nodes:
                        if node.status == TaskStatus.PENDING:
                            node.status = TaskStatus.BLOCKED
                    return
            for node in ready:
                if workspace.spent + node.cost > workspace.budget:
                    node.status = TaskStatus.BLOCKED
                    workspace.ledger.append({"event": "budget_block", "task": node.task_id})
                    continue
                self._run_node(node, workspace)
                workspace.spent += node.cost
                workspace.ledger.append({"event": "task_done", "task": node.task_id, "role": node.role, "cost": node.cost})
                self._checkpoint(workspace, plan)

    def _run_node(self, node: TaskNode, workspace: Workspace) -> None:
        node.status = TaskStatus.RUNNING
        workspace.private_state.setdefault(node.role, {})
        if node.role in {"researcher", "tool_agent", "model_agent"}:
            workspace.shared_state.setdefault("evidence", []).append(node.description)
            node.result = "evidence collected"
        elif node.role == "analyst":
            node.result = "ranked root cause: CAD alignment drift"
            workspace.shared_state["analysis"] = node.result
        elif node.role == "verifier":
            node.result = "verified against evidence"
        elif node.role == "critic":
            node.result = "safety boundary checked"
        else:
            node.result = "Final RCA artifact: root cause is CAD alignment drift."
            workspace.shared_state["final"] = node.result
        node.status = TaskStatus.DONE

    def _checkpoint(self, workspace: Workspace, plan: CandidatePlan) -> None:
        ensure_dirs()
        path = CHECKPOINT_DIR / f"{workspace.run_id}.json"
        path.write_text(json.dumps({"workspace": asdict(workspace), "plan": asdict(plan)}, indent=2), encoding="utf-8")


class DynamicReplanner:
    """Adds missing work only when critic/verifier has new evidence of a gap."""

    def replan_if_needed(self, plan: CandidatePlan, workspace: Workspace, verifier: CriticVerifier) -> CandidatePlan:
        if verifier.verify_result(workspace):
            return plan
        workspace.reflection_memory.append("Verifier failed because final artifact lacked evidence-grounded root cause.")
        if not any(node.task_id == "t_repair" for node in plan.nodes):
            plan.nodes.append(TaskNode("t_repair", "Repair final answer using evidence", "writer", 1, ["t4"]))
        return plan


class LongHorizonAgent:
    """Runs the full architecture with bounded budget and persistent artifacts."""

    def __init__(self, budget: int = 14) -> None:
        self.planner = Planner()
        self.critic = CriticVerifier()
        self.coordinator = MultiAgentCoordinator()
        self.replanner = DynamicReplanner()
        self.budget = budget

    def run(self, goal: str) -> Workspace:
        ensure_dirs()
        workspace = Workspace(f"run-{uuid.uuid4().hex[:8]}", goal, self.budget)
        candidates = [self.critic.critique_plan(plan) for plan in self.planner.beam_search_plans(goal)]
        plan = next(plan for plan in candidates if not plan.critique)
        plan = self.planner.mcts_expand(plan)
        workspace.ledger.append({"event": "plan_selected", "plan_id": plan.plan_id, "critical_path": DependencyGraph().critical_path_cost(plan.nodes)})
        self.coordinator.execute(plan, workspace)
        plan = self.replanner.replan_if_needed(plan, workspace, self.critic)
        if any(node.status == TaskStatus.PENDING for node in plan.nodes):
            self.coordinator.execute(plan, workspace)
        artifact = ARTIFACT_DIR / f"{workspace.run_id}_artifact.json"
        artifact.write_text(json.dumps({"final": workspace.shared_state.get("final"), "ledger": workspace.ledger}, indent=2), encoding="utf-8")
        workspace.artifact_paths.append(str(artifact))
        return workspace


def self_test() -> None:
    agent = LongHorizonAgent()
    workspace = agent.run("Investigate complex RCA for P-1003")
    assert workspace.shared_state.get("evidence")
    assert workspace.shared_state.get("final")
    assert workspace.spent <= workspace.budget
    assert workspace.artifact_paths and Path(workspace.artifact_paths[0]).exists()
    assert any(item["event"] == "plan_selected" for item in workspace.ledger)

    tight = LongHorizonAgent(budget=2).run("Investigate complex RCA under tiny budget")
    assert any(item["event"] == "budget_block" for item in tight.ledger)
    print("Self-tests passed.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Advanced agent architecture.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.run:
        ws = LongHorizonAgent().run("Investigate complex RCA for P-1003")
        print(json.dumps(asdict(ws), indent=2, ensure_ascii=False))
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
