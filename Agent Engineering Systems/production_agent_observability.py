#!/usr/bin/env python3
"""
Production Agent Observability Runtime

This portfolio project demonstrates the production architecture around an agent,
not just the model call itself. It includes:

- API Gateway, Agent Runtime, Tool Service, Queue
- State Store, Memory Store, Artifact Store
- Evaluation Service, Tracing Service, Approval Service
- timeout, retry with backoff, circuit breaker, bulkhead isolation
- dead-letter queue, idempotency, checkpointing, resume after failure
- graceful degradation, model fallback, tool fallback, partial results
- prompt cache, semantic cache, tool result cache, model routing, context pruning
- trace events for model calls, tools, handoff, state transitions, approvals
- latency, token, cost, retry, timeout, and error metrics

Run:
  python production_agent_observability.py --self-test
  python production_agent_observability.py --run "Summarize panel P-1003 and recommend next steps"
  python production_agent_observability.py --run "Create retrain request for defect-cnn-v4" --auto-approve
  python production_agent_observability.py --demo-failure
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import math
import queue
import statistics
import sys
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable


JsonObject = dict[str, Any]
PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "production_agent_observability_data"
ARTIFACT_DIR = DATA_DIR / "artifacts"
TRACE_DIR = DATA_DIR / "traces"
METRICS_DIR = DATA_DIR / "metrics"


def ensure_dirs() -> None:
    """Create all output folders for artifacts, traces, and metrics."""

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)


def now_ms() -> float:
    """Monotonic time in milliseconds for latency measurement."""

    return time.perf_counter() * 1000


def stable_hash(value: str) -> str:
    """Stable short hash used for cache keys and idempotency keys."""

    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]


def percentile(values: list[float], pct: float) -> float:
    """Compute percentile without external dependencies."""

    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * pct
    low = math.floor(index)
    high = math.ceil(index)
    if low == high:
        return ordered[low]
    weight = index - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    DEAD_LETTERED = "dead_lettered"


class ErrorCategory(str, Enum):
    NONE = "none"
    TIMEOUT = "timeout"
    TRANSIENT = "transient"
    CIRCUIT_OPEN = "circuit_open"
    PERMISSION = "permission"
    VALIDATION = "validation"
    MODEL = "model"
    TOOL = "tool"
    UNKNOWN = "unknown"


@dataclass
class AgentRequest:
    """Request accepted by the API Gateway."""

    goal: str
    user_id: str = "demo-user"
    session_id: str = field(default_factory=lambda: f"sess-{uuid.uuid4().hex[:8]}")
    idempotency_key: str | None = None
    auto_approve: bool = False
    prompt_version: str = "prompt.production.v1"
    preferred_model: str = "auto"


@dataclass
class QueuedTask:
    """Queue item created after gateway validation."""

    task_id: str
    request: AgentRequest
    attempts: int = 0
    enqueued_ms: float = field(default_factory=now_ms)


@dataclass
class RuntimeState:
    """Checkpointed state for one agent task."""

    task_id: str
    trace_id: str
    session_id: str
    agent_id: str
    status: TaskStatus
    goal: str
    prompt_version: str
    model_version: str | None = None
    completed_steps: list[str] = field(default_factory=list)
    partial_results: JsonObject = field(default_factory=dict)
    artifact_paths: list[str] = field(default_factory=list)
    last_error: str | None = None
    updated_ms: float = field(default_factory=now_ms)


@dataclass
class TraceEvent:
    """Event-level observability record."""

    trace_id: str
    task_id: str
    session_id: str
    agent_id: str
    event_type: str
    timestamp_ms: float
    detail: JsonObject


@dataclass
class MetricsRecord:
    """Aggregated metrics for one task execution."""

    task_id: str
    trace_id: str
    status: str
    latency_ms: float
    queue_latency_ms: float
    model_latency_ms: float
    tool_latency_ms: float
    serialization_latency_ms: float
    input_tokens: int
    output_tokens: int
    model_calls: int
    tool_calls: int
    retries: int
    timeouts: int
    human_interventions: int
    model_cost_usd: float
    tool_cost_usd: float
    cache_hits: int
    error_category: str = ErrorCategory.NONE.value


class TracingService:
    """Collects events for model calls, tools, approvals, transitions, and custom events."""

    def __init__(self) -> None:
        ensure_dirs()
        self.events: dict[str, list[TraceEvent]] = {}

    def emit(self, state: RuntimeState, event_type: str, detail: JsonObject) -> None:
        event = TraceEvent(
            trace_id=state.trace_id,
            task_id=state.task_id,
            session_id=state.session_id,
            agent_id=state.agent_id,
            event_type=event_type,
            timestamp_ms=now_ms(),
            detail=detail,
        )
        self.events.setdefault(state.trace_id, []).append(event)

    def save(self, trace_id: str) -> Path:
        path = TRACE_DIR / f"{trace_id}.json"
        path.write_text(
            json.dumps([asdict(event) for event in self.events.get(trace_id, [])], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return path


class StateStore:
    """In-memory checkpoint store."""

    def __init__(self) -> None:
        self._states: dict[str, RuntimeState] = {}

    def save(self, state: RuntimeState) -> None:
        state.updated_ms = now_ms()
        self._states[state.task_id] = state

    def get(self, task_id: str) -> RuntimeState | None:
        return self._states.get(task_id)


class MemoryStore:
    """Small memory store for durable user/session facts."""

    def __init__(self) -> None:
        self.preferences: dict[str, JsonObject] = {}
        self.session_summaries: dict[str, str] = {}

    def remember_summary(self, session_id: str, summary: str) -> None:
        self.session_summaries[session_id] = summary

    def get_context(self, session_id: str) -> JsonObject:
        return {"session_summary": self.session_summaries.get(session_id, "")}


class ArtifactStore:
    """Writes task reports and partial artifacts to disk."""

    def write_json(self, task_id: str, name: str, payload: JsonObject) -> str:
        ensure_dirs()
        path = ARTIFACT_DIR / f"{task_id}_{name}.json"
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return str(path)


class IdempotencyStore:
    """Maps idempotency keys to task IDs to avoid duplicate side effects."""

    def __init__(self) -> None:
        self.keys: dict[str, str] = {}

    def get_or_create_task_id(self, key: str | None, goal: str) -> tuple[str, bool]:
        effective_key = key or stable_hash(goal)
        if effective_key in self.keys:
            return self.keys[effective_key], True
        task_id = f"task-{uuid.uuid4().hex[:10]}"
        self.keys[effective_key] = task_id
        return task_id, False


class TaskQueue:
    """Queue with a dead-letter queue for tasks that exceed retry limits."""

    def __init__(self) -> None:
        self.ready: queue.Queue[QueuedTask] = queue.Queue()
        self.dead_letters: list[QueuedTask] = []

    def enqueue(self, task: QueuedTask) -> None:
        self.ready.put(task)

    def dequeue(self) -> QueuedTask:
        return self.ready.get_nowait()

    def dead_letter(self, task: QueuedTask) -> None:
        self.dead_letters.append(task)


class CacheStore:
    """Prompt, semantic, and tool result caches."""

    def __init__(self) -> None:
        self.prompt_cache: dict[str, str] = {}
        self.semantic_cache: dict[str, JsonObject] = {}
        self.tool_cache: dict[str, JsonObject] = {}

    def prompt_key(self, prompt_version: str, goal: str) -> str:
        return stable_hash(f"{prompt_version}:{goal}")

    def tool_key(self, name: str, args: JsonObject) -> str:
        return stable_hash(json.dumps({"name": name, "args": args}, sort_keys=True))


class CircuitBreaker:
    """Stops calling a failing dependency for a cooldown window."""

    def __init__(self, failure_threshold: int = 2, cooldown_seconds: float = 1.0) -> None:
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.failures = 0
        self.open_until = 0.0

    def allow(self) -> bool:
        return time.perf_counter() >= self.open_until

    def record_success(self) -> None:
        self.failures = 0
        self.open_until = 0.0

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.open_until = time.perf_counter() + self.cooldown_seconds


class Bulkhead:
    """Limits concurrency for one dependency so it cannot starve the runtime."""

    def __init__(self, limit: int) -> None:
        self.semaphore = threading.Semaphore(limit)

    def run(self, fn: Callable[[], JsonObject], timeout_seconds: float) -> JsonObject:
        acquired = self.semaphore.acquire(timeout=timeout_seconds)
        if not acquired:
            raise TimeoutError("bulkhead queue timeout")
        try:
            return fn()
        finally:
            self.semaphore.release()


class RetryPolicy:
    """Retry wrapper with exponential backoff."""

    def __init__(self, max_attempts: int = 3, base_delay_seconds: float = 0.03) -> None:
        self.max_attempts = max_attempts
        self.base_delay_seconds = base_delay_seconds

    def run(self, fn: Callable[[], JsonObject]) -> tuple[JsonObject, int]:
        last_error: Exception | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                return fn(), attempt - 1
            except TimeoutError as exc:
                last_error = exc
            except RuntimeError as exc:
                last_error = exc
            if attempt < self.max_attempts:
                time.sleep(self.base_delay_seconds * (2 ** (attempt - 1)))
        raise last_error or RuntimeError("retry failed")


class SimulatedModelProvider:
    """Local model provider with routing, fallback, and cost accounting."""

    MODEL_COSTS = {
        "small-model-v1": {"input": 0.0000002, "output": 0.0000004},
        "large-model-v1": {"input": 0.0000008, "output": 0.0000016},
    }

    def choose_model(self, goal: str, preferred: str) -> str:
        if preferred != "auto":
            return preferred
        high_risk_terms = {"retrain", "approval", "root cause", "rca", "production"}
        return "large-model-v1" if any(term in goal.lower() for term in high_risk_terms) else "small-model-v1"

    def generate(self, model: str, prompt: str, fail_large: bool = False) -> JsonObject:
        if fail_large and model == "large-model-v1":
            raise RuntimeError("large model unavailable")
        input_tokens = max(1, len(prompt.split()) + len(prompt) // 16)
        output = f"Summary generated by {model}: {prompt[:120]}"
        output_tokens = max(8, len(output.split()) + len(output) // 18)
        latency_ms = 80.0 if model == "small-model-v1" else 160.0
        costs = self.MODEL_COSTS[model]
        cost = input_tokens * costs["input"] + output_tokens * costs["output"]
        return {
            "model": model,
            "output": output,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_ms": latency_ms,
            "cost_usd": cost,
        }


class ToolService:
    """Tool layer with timeout, retry, circuit breaker, bulkhead, fallback, and caching."""

    def __init__(self, cache: CacheStore) -> None:
        self.cache = cache
        self.retry = RetryPolicy()
        self.circuit_breakers = {
            "panel_summary": CircuitBreaker(),
            "cad_alignment": CircuitBreaker(),
            "model_metrics": CircuitBreaker(),
        }
        self.bulkheads = {
            "panel_summary": Bulkhead(2),
            "cad_alignment": Bulkhead(1),
            "model_metrics": Bulkhead(1),
        }
        self.fail_next: set[str] = set()

    def call(self, name: str, args: JsonObject, state: RuntimeState, tracing: TracingService) -> tuple[JsonObject, JsonObject]:
        """Call a tool and return result plus call metrics."""

        started = now_ms()
        cache_key = self.cache.tool_key(name, args)
        if cache_key in self.cache.tool_cache:
            tracing.emit(state, "tool_cache_hit", {"tool": name, "arguments": args})
            return self.cache.tool_cache[cache_key], {"latency_ms": 0.0, "retries": 0, "timeouts": 0, "cache_hit": 1, "cost_usd": 0.0}

        breaker = self.circuit_breakers[name]
        if not breaker.allow():
            tracing.emit(state, "tool_circuit_open", {"tool": name})
            fallback = self._fallback(name, args)
            return fallback, {"latency_ms": now_ms() - started, "retries": 0, "timeouts": 0, "cache_hit": 0, "cost_usd": 0.00005}

        def operation() -> JsonObject:
            def inner() -> JsonObject:
                if name in self.fail_next:
                    self.fail_next.remove(name)
                    raise TimeoutError(f"{name} simulated timeout")
                time.sleep(0.01)
                return self._execute(name, args)

            return self.bulkheads[name].run(inner, timeout_seconds=0.2)

        try:
            result, retries = self.retry.run(operation)
            breaker.record_success()
            self.cache.tool_cache[cache_key] = result
            latency = now_ms() - started
            tracing.emit(state, "tool_call", {"tool": name, "arguments": args, "latency_ms": latency, "retries": retries})
            return result, {"latency_ms": latency, "retries": retries, "timeouts": retries, "cache_hit": 0, "cost_usd": 0.0002}
        except Exception as exc:
            breaker.record_failure()
            fallback = self._fallback(name, args)
            tracing.emit(state, "tool_fallback", {"tool": name, "error": str(exc), "fallback": fallback})
            return fallback, {"latency_ms": now_ms() - started, "retries": self.retry.max_attempts - 1, "timeouts": 1, "cache_hit": 0, "cost_usd": 0.0001}

    def _execute(self, name: str, args: JsonObject) -> JsonObject:
        if name == "panel_summary":
            panel_id = args["panel_id"]
            return {"panel_id": panel_id, "defect_count": 1 if panel_id == "P-1003" else 2, "yield_risk": "high" if panel_id == "P-1003" else "medium"}
        if name == "cad_alignment":
            return {"panel_id": args["panel_id"], "within_tolerance": args["panel_id"] != "P-1003", "dx_um": 41.9 if args["panel_id"] == "P-1003" else 12.4}
        if name == "model_metrics":
            return {"model_name": args["model_name"], "precision": 0.942, "recall": 0.918, "drift_score": 0.17}
        raise RuntimeError(f"unknown tool {name}")

    def _fallback(self, name: str, args: JsonObject) -> JsonObject:
        if name == "cad_alignment":
            return {"panel_id": args.get("panel_id", "unknown"), "within_tolerance": None, "fallback": "CAD alignment unavailable"}
        if name == "model_metrics":
            return {"model_name": args.get("model_name", "unknown"), "fallback": "last-known metrics unavailable"}
        return {"fallback": f"{name} unavailable", "partial": True}


class ApprovalService:
    """Human approval service for high-risk actions."""

    def __init__(self) -> None:
        self.records: dict[str, JsonObject] = {}

    def request(self, state: RuntimeState, action: str, auto_approve: bool, tracing: TracingService) -> bool:
        approval_id = f"approval-{uuid.uuid4().hex[:8]}"
        approved = bool(auto_approve)
        record = {"approval_id": approval_id, "action": action, "approved": approved, "timestamp_ms": now_ms()}
        self.records[approval_id] = record
        tracing.emit(state, "human_approval", record)
        return approved


class EvaluationService:
    """Tiny post-run evaluator for production health checks."""

    def evaluate(self, state: RuntimeState) -> JsonObject:
        return {
            "task_id": state.task_id,
            "status": state.status.value,
            "has_artifact": bool(state.artifact_paths),
            "completed_steps": state.completed_steps,
            "partial": state.status == TaskStatus.PARTIAL,
            "last_error": state.last_error,
        }


class APIGateway:
    """Validates requests, applies idempotency, and enqueues tasks."""

    def __init__(self, idempotency: IdempotencyStore, task_queue: TaskQueue) -> None:
        self.idempotency = idempotency
        self.task_queue = task_queue

    def submit(self, request: AgentRequest) -> JsonObject:
        if not request.goal.strip():
            return {"accepted": False, "error": "goal is required"}
        idempotency_source = json.dumps(
            {
                "goal": request.goal,
                "user_id": request.user_id,
                "session_id": request.session_id,
                "auto_approve": request.auto_approve,
                "prompt_version": request.prompt_version,
                "preferred_model": request.preferred_model,
            },
            sort_keys=True,
        )
        task_id, duplicate = self.idempotency.get_or_create_task_id(request.idempotency_key, idempotency_source)
        if not duplicate:
            self.task_queue.enqueue(QueuedTask(task_id=task_id, request=request))
        return {"accepted": True, "task_id": task_id, "duplicate": duplicate}


class AgentRuntime:
    """Production-style runtime that coordinates model, tools, state, memory, approval, and tracing."""

    def __init__(
        self,
        state_store: StateStore,
        memory_store: MemoryStore,
        artifact_store: ArtifactStore,
        tracing: TracingService,
        tools: ToolService,
        approval: ApprovalService,
        evaluation: EvaluationService,
        model_provider: SimulatedModelProvider,
    ) -> None:
        self.state_store = state_store
        self.memory_store = memory_store
        self.artifact_store = artifact_store
        self.tracing = tracing
        self.tools = tools
        self.approval = approval
        self.evaluation = evaluation
        self.model_provider = model_provider

    def run_task(self, task: QueuedTask, fail_large_model: bool = False) -> tuple[RuntimeState, MetricsRecord]:
        queue_latency_ms = now_ms() - task.enqueued_ms
        trace_id = f"trace-{uuid.uuid4().hex[:10]}"
        state = self.state_store.get(task.task_id) or RuntimeState(
            task_id=task.task_id,
            trace_id=trace_id,
            session_id=task.request.session_id,
            agent_id="industrial-agent-runtime",
            status=TaskStatus.RUNNING,
            goal=task.request.goal,
            prompt_version=task.request.prompt_version,
        )
        self._transition(state, TaskStatus.RUNNING, "task_started")

        metrics = MetricsRecord(
            task_id=state.task_id,
            trace_id=state.trace_id,
            status=TaskStatus.RUNNING.value,
            latency_ms=0.0,
            queue_latency_ms=queue_latency_ms,
            model_latency_ms=0.0,
            tool_latency_ms=0.0,
            serialization_latency_ms=0.0,
            input_tokens=0,
            output_tokens=0,
            model_calls=0,
            tool_calls=0,
            retries=0,
            timeouts=0,
            human_interventions=0,
            model_cost_usd=0.0,
            tool_cost_usd=0.0,
            cache_hits=0,
        )
        started = now_ms()

        try:
            self._checkpoint(state, "intake")
            context = self._build_context(task.request, state)
            self._checkpoint(state, "context_pruned")

            if self._needs_approval(task.request.goal):
                metrics.human_interventions += 1
                if not self.approval.request(state, "high_risk_action", task.request.auto_approve, self.tracing):
                    self._transition(state, TaskStatus.WAITING_APPROVAL, "approval_required")
                    metrics.status = state.status.value
                    metrics.latency_ms = now_ms() - started
                    return state, metrics

            tool_results = self._run_parallel_tools(task.request, state, metrics)
            state.partial_results.update(tool_results)
            self._checkpoint(state, "tools_completed")

            prompt = self._make_prompt(task.request, context, tool_results)
            model_result = self._call_model(task.request, state, prompt, metrics, fail_large_model)
            state.model_version = model_result["model"]
            state.partial_results["model_output"] = model_result["output"]
            self._checkpoint(state, "model_completed")

            artifact_path = self.artifact_store.write_json(state.task_id, "report", state.partial_results)
            state.artifact_paths.append(artifact_path)
            self.memory_store.remember_summary(state.session_id, model_result["output"])

            status = TaskStatus.PARTIAL if any("fallback" in value for value in tool_results.values() if isinstance(value, dict)) else TaskStatus.COMPLETED
            self._transition(state, status, "task_finished")
        except Exception as exc:
            state.last_error = str(exc)
            self._transition(state, TaskStatus.FAILED, "task_failed")
            metrics.error_category = ErrorCategory.UNKNOWN.value
        finally:
            metrics.status = state.status.value
            metrics.latency_ms = now_ms() - started
            metrics.serialization_latency_ms = 3.0
            self._checkpoint(state, "final_checkpoint")
            evaluation = self.evaluation.evaluate(state)
            self.tracing.emit(state, "evaluation", evaluation)
            self.tracing.save(state.trace_id)
        return state, metrics

    def resume_after_failure(self, task_id: str) -> RuntimeState | None:
        state = self.state_store.get(task_id)
        if not state:
            return None
        self.tracing.emit(state, "resume_after_failure", {"completed_steps": state.completed_steps, "last_error": state.last_error})
        return state

    def _run_parallel_tools(self, request: AgentRequest, state: RuntimeState, metrics: MetricsRecord) -> JsonObject:
        tools_to_call = {
            "panel_summary": {"panel_id": self._extract_panel_id(request.goal)},
            "cad_alignment": {"panel_id": self._extract_panel_id(request.goal)},
        }
        if "model" in request.goal.lower() or "retrain" in request.goal.lower():
            tools_to_call["model_metrics"] = {"model_name": "defect-cnn-v4"}

        results: JsonObject = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            future_map = {
                pool.submit(self.tools.call, name, args, state, self.tracing): name
                for name, args in tools_to_call.items()
            }
            for future in concurrent.futures.as_completed(future_map):
                name = future_map[future]
                result, call_metrics = future.result()
                results[name] = result
                metrics.tool_calls += 1
                metrics.tool_latency_ms += call_metrics["latency_ms"]
                metrics.retries += call_metrics["retries"]
                metrics.timeouts += call_metrics["timeouts"]
                metrics.cache_hits += call_metrics["cache_hit"]
                metrics.tool_cost_usd += call_metrics["cost_usd"]
        return results

    def _call_model(
        self,
        request: AgentRequest,
        state: RuntimeState,
        prompt: str,
        metrics: MetricsRecord,
        fail_large_model: bool,
    ) -> JsonObject:
        prompt_key = stable_hash(f"{request.prompt_version}:{prompt}")
        model = self.model_provider.choose_model(request.goal, request.preferred_model)
        try:
            result = self.model_provider.generate(model, prompt, fail_large=fail_large_model)
        except RuntimeError:
            self.tracing.emit(state, "model_fallback", {"from": model, "to": "small-model-v1"})
            result = self.model_provider.generate("small-model-v1", prompt, fail_large=False)
        metrics.model_calls += 1
        metrics.model_latency_ms += result["latency_ms"]
        metrics.input_tokens += result["input_tokens"]
        metrics.output_tokens += result["output_tokens"]
        metrics.model_cost_usd += result["cost_usd"]
        self.tracing.emit(
            state,
            "model_generation",
            {
                "prompt_version": request.prompt_version,
                "model_version": result["model"],
                "input_tokens": result["input_tokens"],
                "output_tokens": result["output_tokens"],
                "latency_ms": result["latency_ms"],
                "prompt_cache_key": prompt_key,
            },
        )
        return result

    def _build_context(self, request: AgentRequest, state: RuntimeState) -> JsonObject:
        memory = self.memory_store.get_context(request.session_id)
        context = {
            "goal": request.goal[:600],
            "memory_summary": memory["session_summary"][:300],
            "prompt_version": request.prompt_version,
        }
        self.tracing.emit(state, "context_pruning", {"original_chars": len(request.goal), "context": context})
        return context

    def _make_prompt(self, request: AgentRequest, context: JsonObject, tool_results: JsonObject) -> str:
        return json.dumps({"context": context, "tool_results": tool_results}, ensure_ascii=False)

    def _extract_panel_id(self, goal: str) -> str:
        for token in goal.replace(",", " ").split():
            if token.upper().startswith("P-"):
                return token.strip(".").upper()
        return "P-1001"

    def _needs_approval(self, goal: str) -> bool:
        return any(term in goal.lower() for term in ["create retrain", "commit", "production change", "delete"])

    def _checkpoint(self, state: RuntimeState, step: str) -> None:
        if step not in state.completed_steps:
            state.completed_steps.append(step)
        self.state_store.save(state)
        self.tracing.emit(state, "checkpoint", {"step": step, "completed_steps": state.completed_steps})

    def _transition(self, state: RuntimeState, status: TaskStatus, reason: str) -> None:
        previous = state.status
        state.status = status
        self.state_store.save(state)
        self.tracing.emit(state, "state_transition", {"from": previous.value, "to": status.value, "reason": reason})


class MetricsService:
    """Aggregates task metrics and writes production reports."""

    def __init__(self) -> None:
        ensure_dirs()
        self.records: list[MetricsRecord] = []

    def add(self, record: MetricsRecord) -> None:
        self.records.append(record)

    def summary(self) -> JsonObject:
        successes = [record for record in self.records if record.status in {TaskStatus.COMPLETED.value, TaskStatus.PARTIAL.value}]
        total_model_cost = sum(record.model_cost_usd for record in self.records)
        total_tool_cost = sum(record.tool_cost_usd for record in self.records)
        latencies = [record.latency_ms for record in self.records]
        return {
            "tasks": len(self.records),
            "successful_tasks": len(successes),
            "p50_latency_ms": percentile(latencies, 0.50),
            "p95_latency_ms": percentile(latencies, 0.95),
            "p99_latency_ms": percentile(latencies, 0.99),
            "model_cost_usd": total_model_cost,
            "tool_cost_usd": total_tool_cost,
            "cost_per_success_usd": (total_model_cost + total_tool_cost) / max(1, len(successes)),
            "tokens_per_task": statistics.mean([record.input_tokens + record.output_tokens for record in self.records]) if self.records else 0,
            "tool_calls_per_task": statistics.mean([record.tool_calls for record in self.records]) if self.records else 0,
            "retry_rate": sum(record.retries for record in self.records) / max(1, sum(record.tool_calls for record in self.records)),
            "timeout_rate": sum(record.timeouts for record in self.records) / max(1, sum(record.tool_calls for record in self.records)),
            "human_intervention_rate": sum(record.human_interventions for record in self.records) / max(1, len(self.records)),
            "cache_hits": sum(record.cache_hits for record in self.records),
        }

    def save(self, label: str) -> Path:
        path = METRICS_DIR / f"{label}_metrics.json"
        path.write_text(
            json.dumps({"summary": self.summary(), "records": [asdict(record) for record in self.records]}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return path


class ProductionAgentSystem:
    """Wires all production services together."""

    def __init__(self) -> None:
        ensure_dirs()
        self.state_store = StateStore()
        self.memory_store = MemoryStore()
        self.artifact_store = ArtifactStore()
        self.idempotency = IdempotencyStore()
        self.queue = TaskQueue()
        self.cache = CacheStore()
        self.tracing = TracingService()
        self.tools = ToolService(self.cache)
        self.approval = ApprovalService()
        self.evaluation = EvaluationService()
        self.model_provider = SimulatedModelProvider()
        self.gateway = APIGateway(self.idempotency, self.queue)
        self.runtime = AgentRuntime(
            self.state_store,
            self.memory_store,
            self.artifact_store,
            self.tracing,
            self.tools,
            self.approval,
            self.evaluation,
            self.model_provider,
        )
        self.metrics = MetricsService()

    def submit_and_run(self, request: AgentRequest, fail_large_model: bool = False) -> JsonObject:
        accepted = self.gateway.submit(request)
        if not accepted["accepted"]:
            return accepted
        if accepted["duplicate"]:
            state = self.state_store.get(accepted["task_id"])
            return {"accepted": True, "duplicate": True, "task_id": accepted["task_id"], "status": state.status.value if state else "queued"}
        task = self.queue.dequeue()
        state, metrics = self.runtime.run_task(task, fail_large_model=fail_large_model)
        self.metrics.add(metrics)
        return {
            "accepted": True,
            "task_id": state.task_id,
            "trace_id": state.trace_id,
            "status": state.status.value,
            "artifacts": state.artifact_paths,
            "metrics": asdict(metrics),
        }

    def demo_failure_to_dead_letter(self) -> JsonObject:
        request = AgentRequest(goal="Summarize panel P-1003", idempotency_key=f"failure-{uuid.uuid4().hex[:6]}")
        accepted = self.gateway.submit(request)
        task = self.queue.dequeue()
        task.attempts = 3
        self.queue.dead_letter(task)
        state = RuntimeState(
            task_id=task.task_id,
            trace_id=f"trace-{uuid.uuid4().hex[:10]}",
            session_id=request.session_id,
            agent_id="industrial-agent-runtime",
            status=TaskStatus.DEAD_LETTERED,
            goal=request.goal,
            prompt_version=request.prompt_version,
            last_error="retry limit exceeded",
        )
        self.state_store.save(state)
        self.tracing.emit(state, "dead_lettered", {"attempts": task.attempts, "reason": state.last_error})
        self.tracing.save(state.trace_id)
        return {"accepted": accepted, "dead_letters": len(self.queue.dead_letters), "state": asdict(state)}


def self_test() -> None:
    """Verify the production runtime and key reliability paths."""

    system = ProductionAgentSystem()
    first = system.submit_and_run(
        AgentRequest(
            goal="Summarize panel P-1003 and recommend next steps",
            idempotency_key="same-task",
        )
    )
    assert first["status"] in {TaskStatus.COMPLETED.value, TaskStatus.PARTIAL.value}
    assert first["artifacts"]
    assert Path(first["artifacts"][0]).exists()
    trace_path = TRACE_DIR / f"{first['trace_id']}.json"
    assert trace_path.exists()
    trace_events = json.loads(trace_path.read_text(encoding="utf-8"))
    assert any(event["event_type"] == "model_generation" for event in trace_events)
    assert any(event["event_type"] == "tool_call" for event in trace_events)

    duplicate = system.submit_and_run(AgentRequest(goal="Summarize panel P-1003 and recommend next steps", idempotency_key="same-task"))
    assert duplicate["duplicate"] is True

    approval_wait = system.submit_and_run(AgentRequest(goal="Create retrain request for defect-cnn-v4", auto_approve=False))
    assert approval_wait["status"] == TaskStatus.WAITING_APPROVAL.value

    approved = system.submit_and_run(AgentRequest(goal="Create retrain request for defect-cnn-v4", auto_approve=True))
    assert approved["status"] in {TaskStatus.COMPLETED.value, TaskStatus.PARTIAL.value}

    model_fallback = system.submit_and_run(AgentRequest(goal="Run RCA for production panel P-1003", auto_approve=True), fail_large_model=True)
    fallback_trace = json.loads((TRACE_DIR / f"{model_fallback['trace_id']}.json").read_text(encoding="utf-8"))
    assert any(event["event_type"] == "model_fallback" for event in fallback_trace)

    dead = system.demo_failure_to_dead_letter()
    assert dead["dead_letters"] == 1
    assert system.metrics.summary()["cost_per_success_usd"] > 0
    print("Self-tests passed.")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Production agent observability runtime.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--run", help="Goal to run through the production runtime.")
    parser.add_argument("--auto-approve", action="store_true")
    parser.add_argument("--fail-large-model", action="store_true")
    parser.add_argument("--demo-failure", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.self_test:
        self_test()
        return 0

    system = ProductionAgentSystem()
    if args.demo_failure:
        print(json.dumps(system.demo_failure_to_dead_letter(), indent=2, ensure_ascii=False))
        return 0
    if args.run:
        result = system.submit_and_run(AgentRequest(goal=args.run, auto_approve=args.auto_approve), fail_large_model=args.fail_large_model)
        metrics_path = system.metrics.save("latest")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"Metrics: {metrics_path}")
        return 0
    print("Use --self-test, --run, or --demo-failure.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
