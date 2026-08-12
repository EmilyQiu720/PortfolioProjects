"""Configuration objects for the dynamic pricing reinforcement learning lab."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EnvironmentConfig:
    """Business and simulation parameters for the pricing environment."""

    episode_length: int = 60
    initial_inventory: int = 900
    unit_cost: float = 42.0
    min_price: float = 55.0
    max_price: float = 145.0
    starting_price: float = 92.0
    base_demand: float = 18.0
    elasticity: float = 1.35
    seasonality_strength: float = 0.18
    competitor_noise: float = 7.5
    demand_noise: float = 3.0
    stockout_penalty: float = 34.0
    volatility_penalty: float = 0.22
    low_inventory_penalty: float = 0.08


@dataclass(frozen=True)
class TrainingConfig:
    """Hyperparameters for tabular Q-learning."""

    episodes: int = 2200
    learning_rate: float = 0.14
    discount: float = 0.96
    epsilon_start: float = 0.38
    epsilon_end: float = 0.04
    evaluation_episodes: int = 80
    seeds: tuple[int, ...] = (11, 23, 37, 51, 72)


ACTION_DELTAS: tuple[float, ...] = (-5.0, -2.0, 0.0, 2.0, 5.0)
ACTION_NAMES: tuple[str, ...] = ("large_discount", "small_discount", "hold", "small_increase", "large_increase")
