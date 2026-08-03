#!/usr/bin/env python3
"""
Workflow Agent Orchestrator

This portfolio project demonstrates how a production-style agent system can mix:
- deterministic workflow steps controlled by code
- dynamic decision nodes that choose the next action from current state
- multiple specialized workers coordinated by a supervisor
- handoff, critic review, human approval, shared blackboard state, and tracing

The project is intentionally dependency-free so it can run anywhere:
  python workflow_agent_orchestrator.py --self-test
  python workflow_agent_orchestrator.py --goal "Research agent memory safety and write a recommendation"
  python workflow_agent_orchestrator.py --goal "Draft a deployment plan that changes production thresholds"
  python workflow_agent_orchestrator.py --goal "Compare agent workflow patterns" --auto-approve
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import re
import sys
import textwrap
import urllib.error
import urllib.request
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Protocol


JsonObject = dict[str, Any]
PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "workflow_agent_orchestrator_data"
TRACE_DIR = DATA_DIR / "traces"
REPORT_DIR = DATA_DIR / "reports"
DEFAULT_LLM_BASE_URL = "http://192.168.170.201:8089/api"
DEFAULT_LLM_MODEL = "Qwen/Qwen3.6-35B-A3B-FP8"


def utc_now() -> str:
    """Return a timestamp used in traces and generated artifacts."""

    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def ensure_dirs() -> None:
    """Create output folders next to the project file."""

    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def tokenize(text: str) -> set[str]:
    """Turn text into lowercase terms for small local routing/retrieval logic."""

    return {term.lower() for term in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text)}


class LLMClient:
    """Small OpenAI-compatible chat client for the local vLLM endpoint."""

    def __init__(
        self,
        base_url: str = DEFAULT_LLM_BASE_URL,
        model: str = DEFAULT_LLM_MODEL,
        api_key_env: str = "VLLM_API_KEY",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key_env = api_key_env

    def chat(self, system: str, user: str, max_tokens: int = 700, temperature: float = 0.2) -> str:
        import os

        api_key = os.getenv(self.api_key_env) or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(f"Set {self.api_key_env} or OPENAI_API_KEY before using --use-llm.")

        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.95,
            "stream": False,
            "chat_template_kwargs": {"enable_thinking": False},
            "extra_body": {"chat_template_kwargs": {"enable_thinking": False}},
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"LLM request failed: HTTP {exc.code} {detail}") from exc

        message = payload["choices"][0]["message"]
        return (message.get("content") or message.get("reasoning") or "").strip()


def extract_json_object(text: str) -> JsonObject:
    """Extract a JSON object from a model response that may include prose."""

    fenced = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
    candidate = fenced.group(1) if fenced else text
    start = candidate.find("{")
    end = candidate.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in LLM response.")
    return json.loads(candidate[start : end + 1])


class Route(str, Enum):
    """High-level route chosen by the router decision node."""

    RESEARCH = "research"
    IMPLEMENTATION = "implementation"
    RISK_REVIEW = "risk_review"


class WorkStatus(str, Enum):
    """Lifecycle state for each planned work item."""

    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkItem:
    """One unit of work assigned to a specialized worker."""

    item_id: str
    description: str
    worker: str
    status: WorkStatus = WorkStatus.PENDING
    depends_on: list[str] = field(default_factory=list)


@dataclass
class AgentResult:
    """Standard result object returned by every worker agent."""

    worker: str
    item_id: str
    ok: bool
    summary: str
    evidence: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class Event:
    """Trace event for observability and responsibility tracking."""

    event_id: str
    timestamp: str
    actor: str
    action: str
    detail: JsonObject


@dataclass
class OrchestrationState:
    """Shared state passed between workflow steps and worker agents.

    This is the central contract of the orchestration layer. Workers do not pass
    private ad hoc messages to each other; they read from and write to this state
    through the supervisor.
    """

    run_id: str
    goal: str
    route: Route | None = None
    risk_level: str = "low"
    plan: list[WorkItem] = field(default_factory=list)
    results: list[AgentResult] = field(default_factory=list)
    blackboard: JsonObject = field(default_factory=dict)
    approvals: list[JsonObject] = field(default_factory=list)
    final_report_path: str | None = None
    token_budget: int = 2400
    tokens_used: int = 0
    handoff_count: int = 0
    max_handoffs: int = 3
    events: list[Event] = field(default_factory=list)


class WorkerAgent(Protocol):
    """Protocol shared by all specialized workers."""

    name: str

    def run(self, item: WorkItem, state: OrchestrationState) -> AgentResult:
        """Execute one planned work item."""


class TraceLogger:
    """Records events in memory and writes a final JSON trace to disk."""

    def __init__(self) -> None:
        ensure_dirs()

    def emit(self, state: OrchestrationState, actor: str, action: str, detail: JsonObject) -> None:
        state.events.append(
            Event(
                event_id=f"evt-{len(state.events) + 1:04d}",
                timestamp=utc_now(),
                actor=actor,
                action=action,
                detail=detail,
            )
        )

    def save(self, state: OrchestrationState) -> Path:
        path = TRACE_DIR / f"{state.run_id}.json"
        path.write_text(json.dumps(asdict(state), indent=2, ensure_ascii=False), encoding="utf-8")
        return path


class RouterNode:
    """Dynamic decision node that chooses the route from the current goal.

    In a real system this could be an LLM call with structured output. Here it
    is deterministic so the project is easy to test and demo without an API key.
    """

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm

    def decide(self, state: OrchestrationState) -> Route:
        if self.llm:
            try:
                system = "You are a router. Return only JSON with route as one of: research, implementation, risk_review."
                user = f'Goal: {state.goal}\nReturn JSON like {{"route":"research","reason":"..."}}'
                data = extract_json_object(self.llm.chat(system, user, max_tokens=200, temperature=0.0))
                return Route(data["route"])
            except Exception as exc:
                state.blackboard["router_llm_error"] = str(exc)

        terms = tokenize(state.goal)
        if terms & {"risk", "safety", "approval", "delete", "production", "thresholds"}:
            return Route.RISK_REVIEW
        if terms & {"build", "deploy", "implement", "architecture", "workflow"}:
            return Route.IMPLEMENTATION
        return Route.RESEARCH


class PlannerAgent:
    """Creates an executable plan for the selected route."""

    name = "planner"

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm

    def create_plan(self, state: OrchestrationState) -> list[WorkItem]:
        if self.llm:
            try:
                return self.create_llm_plan(state)
            except Exception as exc:
                state.blackboard["planner_llm_error"] = str(exc)

        if state.route == Route.RESEARCH:
            return [
                WorkItem("w1", "Collect background evidence for the goal.", "researcher"),
                WorkItem("w2", "Synthesize findings into a concise answer.", "writer", depends_on=["w1"]),
                WorkItem("w3", "Critique the answer for unsupported claims.", "critic", depends_on=["w2"]),
            ]
        if state.route == Route.IMPLEMENTATION:
            return [
                WorkItem("w1", "Identify fixed workflow steps and dynamic decision points.", "architect"),
                WorkItem("w2", "Generate implementation notes and tradeoffs.", "writer", depends_on=["w1"]),
                WorkItem("w3", "Review orchestration risks and stopping rules.", "critic", depends_on=["w2"]),
            ]
        return [
            WorkItem("w1", "Identify risky actions and required approval gates.", "risk_analyst"),
            WorkItem("w2", "Draft a safe execution recommendation.", "writer", depends_on=["w1"]),
            WorkItem("w3", "Critique whether human approval is required.", "critic", depends_on=["w2"]),
        ]

    def create_llm_plan(self, state: OrchestrationState) -> list[WorkItem]:
        """Ask the LLM to produce bounded WorkItems for the supervisor."""

        system = (
            "You are an orchestration planner. Return only JSON. "
            "Create 3 to 5 work items. worker must be one of researcher, architect, risk_analyst, writer, critic. "
            "Use depends_on to keep unsafe or review steps after their prerequisites."
        )
        user = (
            f"Goal: {state.goal}\nRoute: {state.route.value if state.route else 'unknown'}\n"
            'Return JSON like {"items":[{"item_id":"w1","description":"...","worker":"researcher","depends_on":[]}]}.'
        )
        data = extract_json_object(self.llm.chat(system, user, max_tokens=700, temperature=0.1))
        allowed_workers = {"researcher", "architect", "risk_analyst", "writer", "critic"}
        items = []
        for index, raw in enumerate(data.get("items", [])[:5]):
            worker = raw.get("worker", "researcher")
            if worker not in allowed_workers:
                worker = "researcher"
            item_id = str(raw.get("item_id") or f"w{index + 1}")
            depends_on = [dep for dep in raw.get("depends_on", []) if isinstance(dep, str)]
            items.append(
                WorkItem(
                    item_id=item_id,
                    description=str(raw.get("description") or f"Work item {index + 1}"),
                    worker=worker,
                    depends_on=depends_on,
                )
            )
        if not items:
            raise ValueError("LLM returned an empty plan.")
        if not any(item.worker == "critic" for item in items):
            items.append(WorkItem(f"w{len(items) + 1}", "Critique the final output.", "critic", [items[-1].item_id]))
        return items


class ResearchAgent:
    """Worker that gathers small local evidence snippets."""

    name = "researcher"

    def run(self, item: WorkItem, state: OrchestrationState) -> AgentResult:
        evidence = [
            "Workflow is best for predictable paths where code should control order.",
            "Agent decisions are useful when the next action depends on observations.",
            "Production systems often combine deterministic workflow with model decision nodes.",
        ]
        state.blackboard["evidence"] = evidence
        return AgentResult(self.name, item.item_id, True, "Collected orchestration background evidence.", evidence)


class ArchitectAgent:
    """Worker that maps deterministic workflow boundaries and dynamic nodes."""

    name = "architect"

    def run(self, item: WorkItem, state: OrchestrationState) -> AgentResult:
        architecture = {
            "fixed_workflow": ["intake", "route", "plan", "execute", "review", "finalize"],
            "decision_nodes": ["route selection", "handoff choice", "approval requirement"],
            "state_contract": ["goal", "route", "plan", "results", "blackboard", "events"],
        }
        state.blackboard["architecture"] = architecture
        return AgentResult(
            self.name,
            item.item_id,
            True,
            "Mapped fixed workflow steps and dynamic decision nodes.",
            [json.dumps(architecture, ensure_ascii=False)],
        )


class RiskAnalystAgent:
    """Worker that determines whether the workflow needs human approval."""

    name = "risk_analyst"

    def run(self, item: WorkItem, state: OrchestrationState) -> AgentResult:
        risky_terms = {"delete", "production", "threshold", "thresholds", "cost", "customer", "deploy"}
        matched = sorted(tokenize(state.goal) & risky_terms)
        state.risk_level = "high" if matched else "medium"
        state.blackboard["risk_terms"] = matched
        warnings = [f"High-risk term detected: {term}" for term in matched]
        return AgentResult(
            self.name,
            item.item_id,
            True,
            f"Risk level set to {state.risk_level}.",
            evidence=[f"matched_terms={matched}"],
            warnings=warnings,
        )


class WriterAgent:
    """Generator worker that drafts the final recommendation from blackboard data."""

    name = "writer"

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm

    def run(self, item: WorkItem, state: OrchestrationState) -> AgentResult:
        if self.llm:
            try:
                draft = self.write_with_llm(state)
                state.blackboard["draft"] = draft
                return AgentResult(self.name, item.item_id, True, "Drafted recommendation with LLM.", [draft])
            except Exception as exc:
                state.blackboard["writer_llm_error"] = str(exc)

        evidence = state.blackboard.get("evidence", [])
        architecture = state.blackboard.get("architecture", {})
        risk_terms = state.blackboard.get("risk_terms", [])

        summary_parts = [
            f"Goal: {state.goal}",
            f"Route: {state.route.value if state.route else 'unknown'}",
            "Recommendation: keep the outer process deterministic, and place dynamic agent choices only at explicit decision nodes.",
        ]
        if evidence:
            summary_parts.append("Evidence: " + " ".join(evidence))
        if architecture:
            summary_parts.append("Architecture: " + json.dumps(architecture, ensure_ascii=False))
        if risk_terms:
            summary_parts.append(f"Approval should be required because risky terms appeared: {', '.join(risk_terms)}.")

        draft = "\n".join(summary_parts)
        state.blackboard["draft"] = draft
        return AgentResult(self.name, item.item_id, True, "Drafted recommendation from shared state.", [draft])

    def write_with_llm(self, state: OrchestrationState) -> str:
        """Ask the LLM to turn blackboard state into a recommendation draft."""

        system = (
            "You are a workflow orchestration writer. Be concise. "
            "Use the provided shared state only. Mention approval if risk is high."
        )
        user = json.dumps(
            {
                "goal": state.goal,
                "route": state.route.value if state.route else None,
                "risk_level": state.risk_level,
                "blackboard": state.blackboard,
                "results": [asdict(result) for result in state.results],
            },
            ensure_ascii=False,
            indent=2,
        )
        return self.llm.chat(system, user, max_tokens=900, temperature=0.2)


class CriticAgent:
    """Critic worker that reviews the generated draft before finalization."""

    name = "critic"

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm

    def run(self, item: WorkItem, state: OrchestrationState) -> AgentResult:
        draft = state.blackboard.get("draft", "")
        warnings = []
        if self.llm and draft:
            try:
                system = "You are a critic. Return only JSON: {\"warnings\":[\"...\"]}. Empty array means approved."
                user = json.dumps(
                    {"goal": state.goal, "risk_level": state.risk_level, "draft": draft},
                    ensure_ascii=False,
                    indent=2,
                )
                data = extract_json_object(self.llm.chat(system, user, max_tokens=350, temperature=0.0))
                warnings.extend(str(item) for item in data.get("warnings", [])[:5])
            except Exception as exc:
                state.blackboard["critic_llm_error"] = str(exc)

        if "Recommendation:" not in draft:
            warnings.append("Draft is missing a recommendation.")
        if state.risk_level == "high" and "Approval should be required" not in draft:
            warnings.append("High-risk run must mention approval.")
        if len(state.results) > 12:
            warnings.append("Too many worker results; possible coordination loop.")

        state.blackboard["critic_warnings"] = warnings
        return AgentResult(
            self.name,
            item.item_id,
            ok=True,
            summary="Critic review completed." if not warnings else "Critic found issues.",
            warnings=warnings,
        )


class HandoffPolicy:
    """Decides when control should move to a more appropriate worker.

    Handoff is useful, but unlimited handoffs can create loops. The policy uses
    a global handoff counter to stop repeated transfers.
    """

    def maybe_handoff(self, item: WorkItem, state: OrchestrationState) -> WorkItem:
        if state.handoff_count >= state.max_handoffs:
            return item
        if item.worker == "researcher" and state.route == Route.IMPLEMENTATION:
            state.handoff_count += 1
            return WorkItem(item.item_id, item.description, "architect", item.status, item.depends_on)
        if item.worker == "architect" and state.route == Route.RESEARCH:
            state.handoff_count += 1
            return WorkItem(item.item_id, item.description, "researcher", item.status, item.depends_on)
        return item


class HumanApprovalGate:
    """Human-in-the-loop gate for high-risk runs.

    This project supports --auto-approve for demos. Without it, high-risk runs
    stop with a clear approval-required status instead of pretending approval
    happened.
    """

    def review(self, state: OrchestrationState, auto_approve: bool) -> bool:
        if state.risk_level != "high":
            return True
        decision = {
            "required": True,
            "approved": auto_approve,
            "reason": "High-risk route requires human approval before finalization.",
            "timestamp": utc_now(),
        }
        state.approvals.append(decision)
        return auto_approve


class Supervisor:
    """Coordinates workers, budgets, dependencies, partial failures, and final output."""

    def __init__(
        self,
        auto_approve: bool = False,
        max_rounds: int = 8,
        use_llm: bool = False,
        llm: LLMClient | None = None,
    ) -> None:
        ensure_dirs()
        self.auto_approve = auto_approve
        self.max_rounds = max_rounds
        self.llm = llm or LLMClient()
        active_llm = self.llm if use_llm else None
        self.tracer = TraceLogger()
        self.router = RouterNode(active_llm)
        self.planner = PlannerAgent(active_llm)
        self.handoff_policy = HandoffPolicy()
        self.approval_gate = HumanApprovalGate()
        self.workers: dict[str, WorkerAgent] = {
            "researcher": ResearchAgent(),
            "architect": ArchitectAgent(),
            "risk_analyst": RiskAnalystAgent(),
            "writer": WriterAgent(active_llm),
            "critic": CriticAgent(active_llm),
        }

    def run(self, goal: str) -> OrchestrationState:
        """Run the full orchestration from intake to report or approval stop."""

        state = OrchestrationState(run_id=f"run-{uuid.uuid4().hex[:10]}", goal=goal)
        self.tracer.emit(state, "supervisor", "intake", {"goal": goal})

        # Deterministic workflow step: every run must go through intake -> route.
        state.route = self.router.decide(state)
        self.tracer.emit(state, "router", "route_selected", {"route": state.route.value})

        # Deterministic workflow step with a planner component.
        state.plan = self.planner.create_plan(state)
        self.tracer.emit(state, "planner", "plan_created", {"items": [asdict(item) for item in state.plan]})

        # Dynamic execution continues until all work is done or a global stop is hit.
        for round_number in range(1, self.max_rounds + 1):
            runnable = self._runnable_items(state)
            if not runnable:
                break

            self.tracer.emit(
                state,
                "supervisor",
                "round_started",
                {"round": round_number, "runnable": [item.item_id for item in runnable]},
            )
            self._run_parallel_workers(state, runnable)

            if state.tokens_used > state.token_budget:
                self.tracer.emit(state, "supervisor", "budget_exceeded", {"tokens_used": state.tokens_used})
                break

        unfinished = [item for item in state.plan if item.status not in {WorkStatus.DONE, WorkStatus.SKIPPED}]
        if unfinished:
            self.tracer.emit(state, "supervisor", "partial_failure", {"unfinished": [asdict(item) for item in unfinished]})

        # Human approval is a deterministic gate triggered by dynamic risk state.
        if not self.approval_gate.review(state, self.auto_approve):
            self.tracer.emit(state, "approval_gate", "approval_required", {"risk_level": state.risk_level})
            self.tracer.save(state)
            return state

        self._write_final_report(state)
        self.tracer.emit(state, "supervisor", "finalized", {"report": state.final_report_path})
        self.tracer.save(state)
        return state

    def _runnable_items(self, state: OrchestrationState) -> list[WorkItem]:
        """Find pending items whose dependencies have completed."""

        done_ids = {item.item_id for item in state.plan if item.status == WorkStatus.DONE}
        return [
            item
            for item in state.plan
            if item.status == WorkStatus.PENDING and all(dep in done_ids for dep in item.depends_on)
        ]

    def _run_parallel_workers(self, state: OrchestrationState, items: list[WorkItem]) -> None:
        """Run independent work items in parallel and merge results into state."""

        with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, len(items))) as pool:
            future_to_item = {}
            for original_item in items:
                item = self.handoff_policy.maybe_handoff(original_item, state)
                original_item.worker = item.worker
                original_item.status = WorkStatus.RUNNING
                self.tracer.emit(
                    state,
                    "supervisor",
                    "worker_dispatched",
                    {"item_id": item.item_id, "worker": item.worker},
                )
                worker = self.workers[item.worker]
                future_to_item[pool.submit(worker.run, item, state)] = original_item

            for future, item in future_to_item.items():
                try:
                    result = future.result(timeout=10)
                    state.results.append(result)
                    item.status = WorkStatus.DONE if result.ok else WorkStatus.FAILED
                    state.tokens_used += self._estimate_tokens(result.summary)
                    self.tracer.emit(
                        state,
                        result.worker,
                        "worker_finished",
                        {"item_id": item.item_id, "ok": result.ok, "warnings": result.warnings},
                    )
                except Exception as exc:
                    item.status = WorkStatus.FAILED
                    state.results.append(
                        AgentResult(item.worker, item.item_id, False, "Worker failed.", warnings=[str(exc)])
                    )
                    self.tracer.emit(
                        state,
                        item.worker,
                        "worker_failed",
                        {"item_id": item.item_id, "error": str(exc)},
                    )

    def _write_final_report(self, state: OrchestrationState) -> None:
        """Write a concise report from shared blackboard state and trace metadata."""

        warnings = [warning for result in state.results for warning in result.warnings]
        body = f"""# Workflow Agent Orchestration Report

## Goal
{state.goal}

## Route
{state.route.value if state.route else "unknown"}

## Recommendation
Use deterministic workflow for the outer process: intake, route, plan, execute, review, approval, and finalization. Use agent-style dynamic decisions only at explicit nodes where observations matter, such as route selection, handoff selection, critic review, and approval checks.

## Shared State
- Run ID: {state.run_id}
- Risk level: {state.risk_level}
- Token budget: {state.token_budget}
- Estimated tokens used: {state.tokens_used}
- Handoffs: {state.handoff_count}

## Worker Results
"""
        for result in state.results:
            body += f"- {result.worker} / {result.item_id}: {result.summary}\n"

        body += "\n## Critic Warnings\n"
        body += "\n".join(f"- {warning}" for warning in warnings) if warnings else "- No critic warnings."

        body += "\n\n## Approval\n"
        body += json.dumps(state.approvals or [{"required": False}], indent=2, ensure_ascii=False)

        report_path = REPORT_DIR / f"{state.run_id}_report.md"
        report_path.write_text(body, encoding="utf-8")
        state.final_report_path = str(report_path)

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Cheap token estimate for budgeting in a dependency-free demo."""

        return max(1, len(text.split()) * 2)


def self_test() -> None:
    """Verify routing, approval behavior, finalization, and trace creation."""

    research = Supervisor().run("Research workflow and agent orchestration patterns")
    assert research.route in {Route.RESEARCH, Route.IMPLEMENTATION}
    assert research.final_report_path is not None
    assert Path(research.final_report_path).exists()
    assert research.events

    blocked = Supervisor(auto_approve=False).run("Change production thresholds after risk review")
    assert blocked.route == Route.RISK_REVIEW
    assert blocked.risk_level == "high"
    assert blocked.final_report_path is None
    assert blocked.approvals and blocked.approvals[-1]["approved"] is False

    approved = Supervisor(auto_approve=True).run("Change production thresholds after risk review")
    assert approved.route == Route.RISK_REVIEW
    assert approved.final_report_path is not None
    assert Path(approved.final_report_path).exists()

    print("Self-tests passed.")


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command-line options."""

    parser = argparse.ArgumentParser(description="Workflow and agent orchestration demo.")
    parser.add_argument("--goal", help="Goal to orchestrate.")
    parser.add_argument("--auto-approve", action="store_true", help="Approve high-risk finalization for demos.")
    parser.add_argument("--use-llm", action="store_true", help="Use the configured vLLM endpoint for router/planner/writer/critic.")
    parser.add_argument("--llm-base-url", default=DEFAULT_LLM_BASE_URL)
    parser.add_argument("--llm-model", default=DEFAULT_LLM_MODEL)
    parser.add_argument("--llm-api-key-env", default="VLLM_API_KEY")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    """Command-line entrypoint."""

    args = parse_args(argv)
    if args.self_test:
        self_test()
        return 0
    if not args.goal:
        print("Provide --goal or --self-test.")
        return 2

    state = Supervisor(
        auto_approve=args.auto_approve,
        use_llm=args.use_llm,
        llm=LLMClient(args.llm_base_url, args.llm_model, args.llm_api_key_env),
    ).run(args.goal)
    print(f"Run: {state.run_id}")
    print(f"Route: {state.route.value if state.route else 'unknown'}")
    print(f"Risk: {state.risk_level}")
    print(f"Approvals: {json.dumps(state.approvals or [{'required': False}], ensure_ascii=False)}")
    print(f"Report: {state.final_report_path or 'not written; approval required or run incomplete'}")
    print(f"Trace: {TRACE_DIR / (state.run_id + '.json')}")
    print("\nPlan:")
    for item in state.plan:
        print(f"  {item.item_id} [{item.status.value}] -> {item.worker}: {item.description}")
    print("\nBlackboard:")
    print(textwrap.indent(json.dumps(state.blackboard, indent=2, ensure_ascii=False), "  "))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
