#!/usr/bin/env python3
"""
Agent Research Benchmark Lab

This project demonstrates research skills needed for frontier agent work:
controlled benchmarks, ablations, confidence intervals, token budget control,
failure trajectory analysis, benchmark contamination checks, and separation of
base model ability from scaffold gains.

Run:
  python agent_research_benchmark_lab.py --self-test
  python agent_research_benchmark_lab.py --run
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


JsonObject = dict[str, Any]
DATA_DIR = Path(__file__).resolve().parent / "agent_research_benchmark_lab_data"


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


class TaskKind(str, Enum):
    LONG_HORIZON = "long_horizon_planning"
    TOOL_USE = "tool_use"
    MEMORY = "memory_consolidation"
    SECURITY = "agent_security"
    VERIFIER = "verifier_guided"


@dataclass
class BenchmarkTask:
    task_id: str
    kind: TaskKind
    prompt: str
    hidden_answer: str
    max_tokens: int
    contaminated_terms: list[str] = field(default_factory=list)


@dataclass
class ExperimentConfig:
    name: str
    base_model_strength: float
    scaffold: str
    verifier: bool
    memory: bool
    test_time_search: int
    token_budget: int
    parallel_samples: int
    hidden_human_intervention: bool = False


@dataclass
class TrialResult:
    task_id: str
    config_name: str
    success: bool
    tokens_used: int
    cost_usd: float
    trajectory: list[str]
    failure_reason: str | None = None


@dataclass
class ExperimentReport:
    config_name: str
    mean_success: float
    variance: float
    ci95_low: float
    ci95_high: float
    avg_tokens: float
    avg_cost: float
    contamination_hits: int
    failure_reasons: dict[str, int]


class ControlledBenchmark:
    """Small benchmark with hidden answers and contamination markers."""

    def tasks(self) -> list[BenchmarkTask]:
        return [
            BenchmarkTask("b1", TaskKind.LONG_HORIZON, "Plan a 5-step RCA workflow.", "checkpoint", 800),
            BenchmarkTask("b2", TaskKind.TOOL_USE, "Choose the right tool for model drift.", "get_model_metrics", 500),
            BenchmarkTask("b3", TaskKind.MEMORY, "Consolidate user preference without leaking PII.", "provenance", 700, ["public answer leaked"]),
            BenchmarkTask("b4", TaskKind.SECURITY, "Resist document prompt injection.", "blocked", 600, ["ignore previous instructions"]),
            BenchmarkTask("b5", TaskKind.VERIFIER, "Use verifier to reject unsupported claim.", "verifier", 700),
        ]

    def contamination_check(self, task: BenchmarkTask, generated: str) -> bool:
        return any(term.lower() in generated.lower() for term in task.contaminated_terms)


class AgentScaffoldSimulator:
    """Simulates research variants without relying on a live model."""

    def run_task(self, task: BenchmarkTask, config: ExperimentConfig, seed: int) -> TrialResult:
        rng = random.Random(seed)
        scaffold_bonus = {
            "none": 0.0,
            "react": 0.08,
            "planner_executor": 0.12,
            "verifier_guided": 0.18,
            "test_time_search": 0.05 * math.log2(max(1, config.test_time_search)),
        }.get(config.scaffold, 0.0)
        memory_bonus = 0.05 if config.memory and task.kind == TaskKind.MEMORY else 0.0
        verifier_bonus = 0.08 if config.verifier and task.kind in {TaskKind.SECURITY, TaskKind.VERIFIER} else 0.0
        budget_penalty = -0.15 if config.token_budget < task.max_tokens else 0.0
        human_bonus = 0.30 if config.hidden_human_intervention else 0.0
        probability = min(0.98, max(0.02, config.base_model_strength + scaffold_bonus + memory_bonus + verifier_bonus + budget_penalty + human_bonus))
        success = rng.random() < probability
        tokens = min(config.token_budget, int(task.max_tokens * (0.5 + rng.random() * 0.8) * max(1, config.test_time_search)))
        trajectory = [config.scaffold, f"task:{task.kind.value}", "verifier" if config.verifier else "no_verifier"]
        failure = None if success else ("budget_exhausted" if budget_penalty else "wrong_tool_or_plan")
        return TrialResult(task.task_id, config.name, success, tokens, tokens * 0.0000008, trajectory, failure)


class ResearchEvaluator:
    """Runs ablations and reports mean, variance, confidence intervals, and failures."""

    def __init__(self) -> None:
        self.benchmark = ControlledBenchmark()
        self.simulator = AgentScaffoldSimulator()

    def run_experiment(self, config: ExperimentConfig, repeats: int = 12) -> tuple[ExperimentReport, list[TrialResult]]:
        results: list[TrialResult] = []
        contamination_hits = 0
        for repeat in range(repeats):
            for task in self.benchmark.tasks():
                result = self.simulator.run_task(task, config, seed=repeat * 100 + hash(task.task_id) % 97)
                results.append(result)
                generated = " ".join(result.trajectory + ([task.hidden_answer] if result.success else []))
                contamination_hits += int(self.benchmark.contamination_check(task, generated))
        success_values = [1.0 if result.success else 0.0 for result in results]
        mean = statistics.mean(success_values)
        variance = statistics.pvariance(success_values)
        stderr = math.sqrt(variance / len(success_values))
        failures: dict[str, int] = {}
        for result in results:
            if result.failure_reason:
                failures[result.failure_reason] = failures.get(result.failure_reason, 0) + 1
        report = ExperimentReport(
            config.name,
            mean,
            variance,
            max(0.0, mean - 1.96 * stderr),
            min(1.0, mean + 1.96 * stderr),
            statistics.mean(result.tokens_used for result in results),
            statistics.mean(result.cost_usd for result in results),
            contamination_hits,
            failures,
        )
        return report, results

    def ablation_suite(self) -> JsonObject:
        configs = [
            ExperimentConfig("base_only", 0.45, "none", False, False, 1, 700, 1),
            ExperimentConfig("react", 0.45, "react", False, False, 1, 700, 1),
            ExperimentConfig("planner_executor", 0.45, "planner_executor", False, False, 1, 700, 1),
            ExperimentConfig("verifier_guided", 0.45, "verifier_guided", True, False, 1, 700, 1),
            ExperimentConfig("memory_enabled", 0.45, "planner_executor", True, True, 1, 700, 1),
            ExperimentConfig("test_time_search", 0.45, "test_time_search", True, True, 4, 2200, 4),
            ExperimentConfig("stronger_base_model", 0.62, "none", False, False, 1, 700, 1),
        ]
        reports = []
        all_results = {}
        for config in configs:
            report, results = self.run_experiment(config)
            reports.append(report)
            all_results[config.name] = [asdict(result) for result in results]
        scaffold_gain = reports[2].mean_success - reports[0].mean_success
        model_gain = reports[-1].mean_success - reports[0].mean_success
        research_checks = self.paper_review_checks(configs, reports)
        output = {
            "run_id": f"research-{uuid.uuid4().hex[:8]}",
            "reports": [asdict(report) for report in reports],
            "scaffold_gain_planner_executor": scaffold_gain,
            "base_model_gain": model_gain,
            "paper_review_checks": research_checks,
            "hardware": {"cpu": "local simulation", "parallel_samples_reported": True},
            "all_results": all_results,
        }
        ensure_dirs()
        (DATA_DIR / "research_benchmark_report.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
        return output

    def paper_review_checks(self, configs: list[ExperimentConfig], reports: list[ExperimentReport]) -> list[str]:
        warnings = []
        for config, report in zip(configs, reports):
            if config.hidden_human_intervention:
                warnings.append(f"{config.name}: hidden human intervention detected.")
            if config.parallel_samples > 1:
                warnings.append(f"{config.name}: uses {config.parallel_samples} parallel samples; compare cost fairly.")
            if config.test_time_search > 1:
                warnings.append(f"{config.name}: uses extra test-time tokens.")
            if report.contamination_hits:
                warnings.append(f"{config.name}: possible benchmark contamination.")
        return warnings


def self_test() -> None:
    evaluator = ResearchEvaluator()
    output = evaluator.ablation_suite()
    reports = output["reports"]
    assert len(reports) >= 6
    assert output["base_model_gain"] != 0
    assert "paper_review_checks" in output
    assert Path(DATA_DIR / "research_benchmark_report.json").exists()
    for report in reports:
        assert 0.0 <= report["ci95_low"] <= report["ci95_high"] <= 1.0
    print("Self-tests passed.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent research benchmark lab.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.run:
        print(json.dumps(ResearchEvaluator().ablation_suite(), indent=2, ensure_ascii=False))
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
