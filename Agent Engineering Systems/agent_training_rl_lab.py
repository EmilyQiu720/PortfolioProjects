#!/usr/bin/env python3
"""
Agent Training and Reinforcement Learning Lab

This project demonstrates the research pipeline behind tool-use agents:
trajectory collection, action tokenization, supervised fine-tuning data,
negative trajectories, process/outcome supervision, curriculum learning,
offline RL, reward design, deterministic replay, and verifiable rewards.

Run:
  python agent_training_rl_lab.py --self-test
  python agent_training_rl_lab.py --run
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
DATA_DIR = Path(__file__).resolve().parent / "agent_training_rl_lab_data"


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


class ActionType(str, Enum):
    ANSWER = "answer"
    CALL_TOOL = "call_tool"
    ASK_USER = "ask_user"
    STOP = "stop"


@dataclass
class State:
    goal: str
    evidence: list[str] = field(default_factory=list)
    steps: int = 0
    hidden_success_key: str = ""


@dataclass
class Action:
    kind: ActionType
    tool_name: str | None = None
    arguments: JsonObject = field(default_factory=dict)
    text: str = ""


@dataclass
class Transition:
    state: State
    action: Action
    next_state: State
    reward: float
    done: bool
    process_label: str


@dataclass
class Trajectory:
    trajectory_id: str
    transitions: list[Transition]
    outcome_success: bool
    total_reward: float
    metadata: JsonObject = field(default_factory=dict)


class ToolEnvironment:
    """Deterministic tool environment with hidden test cases and reset."""

    CASES = {
        "easy": {"goal": "Find defect count for P-1001", "tool": "query_defects", "args": {"panel_id": "P-1001"}, "answer_key": "2"},
        "medium": {"goal": "Run RCA for P-1003", "tool": "run_rca", "args": {"panel_id": "P-1003"}, "answer_key": "CAD alignment"},
        "hard": {"goal": "Create safe retrain plan for drift", "tool": "get_model_metrics", "args": {"model": "defect-cnn-v4"}, "answer_key": "approval"},
    }

    def reset(self, difficulty: str) -> State:
        case = self.CASES[difficulty]
        return State(goal=case["goal"], hidden_success_key=case["answer_key"])

    def step(self, state: State, action: Action) -> tuple[State, float, bool, str]:
        next_state = State(state.goal, list(state.evidence), state.steps + 1, state.hidden_success_key)
        if state.steps >= 5:
            return next_state, -1.0, True, "too_many_steps"
        if action.kind == ActionType.CALL_TOOL:
            obs = self._tool(action.tool_name or "", action.arguments)
            next_state.evidence.append(obs)
            good_tool = any(case["tool"] == action.tool_name for case in self.CASES.values() if case["goal"] == state.goal)
            reward = 0.4 if good_tool else -0.4
            return next_state, reward, False, "good_tool" if good_tool else "wrong_tool"
        if action.kind == ActionType.ANSWER:
            success = state.hidden_success_key.lower() in action.text.lower()
            return next_state, 2.0 if success else -1.0, True, "correct_answer" if success else "wrong_answer"
        if action.kind == ActionType.ASK_USER:
            return next_state, -0.1, False, "unneeded_question"
        return next_state, 0.0, True, "stopped"

    def _tool(self, name: str, args: JsonObject) -> str:
        if name == "query_defects":
            return "panel P-1001 defect count is 2"
        if name == "run_rca":
            return "root cause evidence: CAD alignment drift"
        if name == "get_model_metrics":
            return "drift detected; retrain requires approval"
        return "tool error"


class ActionTokenizer:
    """Converts actions to tokens suitable for tool-call SFT."""

    def encode(self, action: Action) -> str:
        if action.kind == ActionType.CALL_TOOL:
            return f"<tool:{action.tool_name}>{json.dumps(action.arguments, sort_keys=True)}</tool>"
        if action.kind == ActionType.ANSWER:
            return f"<answer>{action.text}</answer>"
        if action.kind == ActionType.ASK_USER:
            return f"<ask>{action.text}</ask>"
        return "<stop/>"

    def decode(self, token: str) -> Action:
        if token.startswith("<tool:"):
            name = token.split(">", 1)[0].replace("<tool:", "")
            args = json.loads(token.split(">", 1)[1].replace("</tool>", ""))
            return Action(ActionType.CALL_TOOL, name, args)
        if token.startswith("<answer>"):
            return Action(ActionType.ANSWER, text=token.replace("<answer>", "").replace("</answer>", ""))
        if token.startswith("<ask>"):
            return Action(ActionType.ASK_USER, text=token.replace("<ask>", "").replace("</ask>", ""))
        return Action(ActionType.STOP)


class Policy:
    """Tiny stochastic policy over tool choices and answer timing."""

    def __init__(self) -> None:
        self.tool_preferences = {"query_defects": 0.33, "run_rca": 0.33, "get_model_metrics": 0.34}
        self.answer_after_evidence_prob = 0.8

    def act(self, state: State) -> Action:
        if state.evidence and random.random() < self.answer_after_evidence_prob:
            return Action(ActionType.ANSWER, text="Answer based on evidence: " + " ".join(state.evidence))
        tool = random.choices(list(self.tool_preferences), weights=list(self.tool_preferences.values()))[0]
        args = {"panel_id": "P-1003"} if tool == "run_rca" else {"panel_id": "P-1001"} if tool == "query_defects" else {"model": "defect-cnn-v4"}
        return Action(ActionType.CALL_TOOL, tool, args)

    def update_supervised(self, successful: list[Trajectory]) -> None:
        counts = {key: 1 for key in self.tool_preferences}
        for traj in successful:
            for transition in traj.transitions:
                if transition.action.kind == ActionType.CALL_TOOL and transition.action.tool_name:
                    counts[transition.action.tool_name] += 1
        total = sum(counts.values())
        self.tool_preferences = {key: value / total for key, value in counts.items()}

    def update_rl(self, trajectories: list[Trajectory], lr: float = 0.05) -> None:
        baseline = statistics.mean(t.total_reward for t in trajectories)
        for traj in trajectories:
            advantage = traj.total_reward - baseline
            for transition in traj.transitions:
                if transition.action.kind == ActionType.CALL_TOOL and transition.action.tool_name:
                    self.tool_preferences[transition.action.tool_name] += lr * advantage
        total = sum(max(0.01, value) for value in self.tool_preferences.values())
        self.tool_preferences = {key: max(0.01, value) / total for key, value in self.tool_preferences.items()}


class RewardModel:
    """Reward combines success, cost, latency, unsafe actions, and redundancy."""

    def score(self, success: bool, cost: float, latency: float, unsafe: bool, redundancy: int) -> float:
        return (2.0 if success else -1.0) - 0.1 * cost - 0.01 * latency - (2.0 if unsafe else 0.0) - 0.2 * redundancy


class TrainingPipeline:
    def __init__(self) -> None:
        self.env = ToolEnvironment()
        self.policy = Policy()
        self.tokenizer = ActionTokenizer()
        self.reward_model = RewardModel()

    def collect_trajectory(self, difficulty: str) -> Trajectory:
        state = self.env.reset(difficulty)
        transitions = []
        done = False
        total = 0.0
        while not done:
            action = self.policy.act(state)
            next_state, reward, done, label = self.env.step(state, action)
            transitions.append(Transition(state, action, next_state, reward, done, label))
            total += reward
            state = next_state
        success = transitions[-1].process_label == "correct_answer"
        shaped = self.reward_model.score(success, cost=len(transitions), latency=len(transitions) * 50, unsafe=False, redundancy=self._redundancy(transitions))
        return Trajectory(f"traj-{uuid.uuid4().hex[:8]}", transitions, success, total + shaped, {"difficulty": difficulty})

    def build_sft_dataset(self, trajectories: list[Trajectory]) -> list[JsonObject]:
        dataset = []
        for traj in trajectories:
            if not traj.outcome_success:
                continue
            for transition in traj.transitions:
                dataset.append(
                    {
                        "state": asdict(transition.state),
                        "action_token": self.tokenizer.encode(transition.action),
                        "process_label": transition.process_label,
                    }
                )
        return dataset

    def build_negative_dataset(self, trajectories: list[Trajectory]) -> list[JsonObject]:
        return [
            {"state": asdict(t.transitions[-1].state), "bad_action": self.tokenizer.encode(t.transitions[-1].action), "reason": t.transitions[-1].process_label}
            for t in trajectories
            if not t.outcome_success
        ]

    def curriculum(self) -> list[str]:
        return ["easy"] * 8 + ["medium"] * 8 + ["hard"] * 8

    def run(self) -> JsonObject:
        ensure_dirs()
        random.seed(7)
        trajectories = [self.collect_trajectory(diff) for diff in self.curriculum()]
        successful = [t for t in trajectories if t.outcome_success]
        self.policy.update_supervised(successful)
        self.policy.update_rl(trajectories)
        sft = self.build_sft_dataset(trajectories)
        negatives = self.build_negative_dataset(trajectories)
        report = {
            "trajectories": len(trajectories),
            "success_rate": len(successful) / len(trajectories),
            "sft_examples": len(sft),
            "negative_examples": len(negatives),
            "policy": self.policy.tool_preferences,
            "objective": "J(theta)=E[sum gamma^t r_t]",
            "sft_loss": "L=-sum_t log p_theta(a_t|s_t)",
        }
        (DATA_DIR / "training_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        return report

    def _redundancy(self, transitions: list[Transition]) -> int:
        seen = set()
        redundant = 0
        for transition in transitions:
            token = self.tokenizer.encode(transition.action)
            if token in seen:
                redundant += 1
            seen.add(token)
        return redundant


def self_test() -> None:
    pipeline = TrainingPipeline()
    report = pipeline.run()
    assert report["trajectories"] == 24
    assert report["sft_examples"] > 0
    assert abs(sum(report["policy"].values()) - 1.0) < 1e-6
    action = Action(ActionType.CALL_TOOL, "run_rca", {"panel_id": "P-1003"})
    assert pipeline.tokenizer.decode(pipeline.tokenizer.encode(action)).tool_name == "run_rca"
    print("Self-tests passed.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent training and RL lab.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.run:
        print(json.dumps(TrainingPipeline().run(), indent=2, ensure_ascii=False))
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
