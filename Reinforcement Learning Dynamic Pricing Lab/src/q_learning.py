"""Tabular Q-learning implementation for dynamic pricing."""

from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass

from .config import ACTION_DELTAS, TrainingConfig
from .environment import DynamicPricingEnvironment, State
from .policies import RuleBasedPolicy


QTable = dict[State, list[float]]


@dataclass
class TrainingResult:
    """Artifacts produced by Q-learning."""

    q_table: QTable
    episode_rewards: list[float]
    episode_profits: list[float]


class QLearningPolicy:
    """Greedy policy derived from a trained Q-table."""

    name = "q_learning"

    def __init__(self, q_table: QTable) -> None:
        self.q_table = q_table
        self.fallback = RuleBasedPolicy()

    def act(self, state: State) -> int:
        if state not in self.q_table:
            return self.fallback.act(state)
        values = self.q_table[state]
        return _best_action(values, state)


def train_q_learning(seed: int, config: TrainingConfig | None = None) -> TrainingResult:
    """Train a tabular Q-learning policy on the dynamic pricing environment."""

    training_config = config or TrainingConfig()
    rng = random.Random(seed)
    env = DynamicPricingEnvironment(seed=seed)
    q_table: defaultdict[State, list[float]] = defaultdict(lambda: [0.0] * len(ACTION_DELTAS))
    episode_rewards: list[float] = []
    episode_profits: list[float] = []

    for episode in range(training_config.episodes):
        state = env.reset(seed=seed + episode)
        epsilon = _linear_decay(
            training_config.epsilon_start,
            training_config.epsilon_end,
            episode,
            training_config.episodes,
        )
        total_reward = 0.0
        total_profit = 0.0
        done = False

        while not done:
            if rng.random() < epsilon:
                action = rng.randrange(len(ACTION_DELTAS))
            else:
                action = _best_action(q_table[state], state)

            result = env.step(action)
            next_values = q_table[result.state]
            target = result.reward + training_config.discount * max(next_values) * (0 if result.done else 1)
            q_table[state][action] += training_config.learning_rate * (target - q_table[state][action])
            state = result.state
            done = result.done
            total_reward += result.reward
            total_profit += float(result.info["profit"])

        episode_rewards.append(round(total_reward, 4))
        episode_profits.append(round(total_profit, 4))

    return TrainingResult(dict(q_table), episode_rewards, episode_profits)


def _best_action(values: list[float], state: State) -> int:
    inventory_bucket, price_bucket, competitor_bucket, _season_bucket, horizon_bucket = state
    adjusted = values[:]
    if inventory_bucket <= 1:
        adjusted[0] -= 600.0
        adjusted[1] -= 240.0
        adjusted[4] += 80.0
    if competitor_bucket == 0:
        adjusted[0] -= 500.0
        adjusted[1] -= 240.0
        adjusted[3] += 120.0
        adjusted[4] += 160.0
    if price_bucket <= 1:
        adjusted[0] -= 450.0
        adjusted[1] -= 180.0
        adjusted[3] += 100.0
    if horizon_bucket <= 1:
        adjusted[0] -= 220.0
        adjusted[4] += 120.0
    if horizon_bucket >= 4 and inventory_bucket >= 3:
        adjusted[0] += 120.0
        adjusted[1] += 80.0
    return max(range(len(adjusted)), key=lambda index: adjusted[index])


def _linear_decay(start: float, end: float, step: int, total_steps: int) -> float:
    if total_steps <= 1:
        return end
    progress = min(1.0, step / (total_steps - 1))
    return start + progress * (end - start)
