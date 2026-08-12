"""Evaluation utilities for pricing policies."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, stdev

from .environment import DynamicPricingEnvironment
from .policies import Policy


@dataclass(frozen=True)
class EpisodeMetrics:
    """Metrics collected from one rollout."""

    reward: float
    profit: float
    revenue: float
    units_sold: int
    stockout: int
    price_volatility: float
    final_inventory: int


@dataclass(frozen=True)
class PolicySummary:
    """Aggregate metrics for one policy across repeated episodes."""

    policy: str
    mean_reward: float
    reward_ci95: float
    mean_profit: float
    profit_ci95: float
    mean_revenue: float
    stockout_rate: float
    mean_price_volatility: float
    mean_final_inventory: float


def run_episode(policy: Policy, seed: int) -> EpisodeMetrics:
    """Roll out one policy for one episode."""

    env = DynamicPricingEnvironment(seed=seed)
    state = env.reset(seed=seed)
    done = False
    total_reward = 0.0
    total_profit = 0.0
    total_revenue = 0.0
    units_sold = 0
    unmet_demand = 0
    prices: list[float] = []

    while not done:
        action = policy.act(state)
        result = env.step(action)
        state = result.state
        done = result.done
        total_reward += result.reward
        total_profit += float(result.info["profit"])
        total_revenue += float(result.info["revenue"])
        units_sold += int(result.info["sales"])
        unmet_demand += int(result.info["unmet_demand"])
        prices.append(float(result.info["price"]))

    return EpisodeMetrics(
        reward=round(total_reward, 4),
        profit=round(total_profit, 4),
        revenue=round(total_revenue, 4),
        units_sold=units_sold,
        stockout=1 if unmet_demand > 0 or (int(result.info["inventory"]) <= 0 and int(result.info["day"]) < 60) else 0,
        price_volatility=round(_mean_absolute_change(prices), 4),
        final_inventory=int(result.info["inventory"]),
    )


def evaluate_policy(policy: Policy, seeds: list[int]) -> PolicySummary:
    """Evaluate a policy across repeated random seeds."""

    episodes = [run_episode(policy, seed) for seed in seeds]
    rewards = [episode.reward for episode in episodes]
    profits = [episode.profit for episode in episodes]
    return PolicySummary(
        policy=policy.name,
        mean_reward=round(mean(rewards), 3),
        reward_ci95=round(_ci95(rewards), 3),
        mean_profit=round(mean(profits), 3),
        profit_ci95=round(_ci95(profits), 3),
        mean_revenue=round(mean(episode.revenue for episode in episodes), 3),
        stockout_rate=round(mean(episode.stockout for episode in episodes), 3),
        mean_price_volatility=round(mean(episode.price_volatility for episode in episodes), 3),
        mean_final_inventory=round(mean(episode.final_inventory for episode in episodes), 3),
    )


def write_summary_csv(path: Path, summaries: list[PolicySummary]) -> None:
    """Persist policy summaries as a reviewable CSV artifact."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(PolicySummary.__dataclass_fields__.keys()))
        writer.writeheader()
        for summary in summaries:
            writer.writerow(summary.__dict__)


def _mean_absolute_change(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return mean(abs(current - previous) for previous, current in zip(values, values[1:]))


def _ci95(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return 1.96 * stdev(values) / math.sqrt(len(values))
