"""Custom Markov decision process for dynamic pricing.

The environment simulates a seller that adjusts price over a fixed selling
horizon. Demand depends on own price, competitor price, seasonality, and random
noise. The reward balances immediate profit with stockout and price volatility
risk, which makes the task closer to a business decision problem than a pure
game score.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from .config import ACTION_DELTAS, EnvironmentConfig


State = tuple[int, int, int, int, int]


@dataclass(frozen=True)
class StepResult:
    """Structured output from one environment transition."""

    state: State
    reward: float
    done: bool
    info: dict[str, float | int]


class DynamicPricingEnvironment:
    """Finite-horizon pricing environment with discretized observations."""

    def __init__(self, config: EnvironmentConfig | None = None, seed: int = 0) -> None:
        self.config = config or EnvironmentConfig()
        self.rng = random.Random(seed)
        self.day = 0
        self.inventory = self.config.initial_inventory
        self.price = self.config.starting_price
        self.competitor_price = self.config.starting_price
        self.previous_sales = 0

    def reset(self, seed: int | None = None) -> State:
        """Start a new episode and return the initial discretized state."""

        if seed is not None:
            self.rng.seed(seed)
        self.day = 0
        self.inventory = self.config.initial_inventory
        self.price = self.config.starting_price
        self.competitor_price = self.config.starting_price + self.rng.uniform(-4.0, 4.0)
        self.previous_sales = 0
        return self._state()

    def step(self, action: int) -> StepResult:
        """Apply a price action and return the next state, reward, and metadata."""

        if action < 0 or action >= len(ACTION_DELTAS):
            raise ValueError(f"action must be between 0 and {len(ACTION_DELTAS) - 1}")
        if self.day >= self.config.episode_length:
            raise RuntimeError("episode is already complete; call reset before stepping again")

        old_price = self.price
        self.price = self._clamp_price(self.price + ACTION_DELTAS[action])
        self.competitor_price = self._clamp_price(
            self.config.starting_price
            + 9.0 * math.sin((self.day + 2) / 9.0)
            + self.rng.uniform(-self.config.competitor_noise, self.config.competitor_noise)
        )

        demand = self._expected_demand(self.price, self.competitor_price, self.day)
        noisy_demand = max(0.0, demand + self.rng.gauss(0.0, self.config.demand_noise))
        sales = min(self.inventory, int(round(noisy_demand)))
        unmet_demand = max(0, int(round(noisy_demand)) - sales)
        self.inventory -= sales

        revenue = sales * self.price
        profit = sales * (self.price - self.config.unit_cost)
        volatility_cost = self.config.volatility_penalty * abs(self.price - old_price) ** 2
        stockout_cost = self.config.stockout_penalty * unmet_demand
        low_inventory_cost = self.config.low_inventory_penalty * max(0, 120 - self.inventory)
        remaining_days = max(0, self.config.episode_length - (self.day + 1))
        early_depletion_cost = 220.0 * remaining_days if self.inventory <= 0 else 0.0
        reward = profit - volatility_cost - stockout_cost - low_inventory_cost - early_depletion_cost

        self.previous_sales = sales
        self.day += 1
        done = self.day >= self.config.episode_length or self.inventory <= 0

        return StepResult(
            state=self._state(),
            reward=round(reward, 4),
            done=done,
            info={
                "day": self.day,
                "price": round(self.price, 2),
                "competitor_price": round(self.competitor_price, 2),
                "sales": sales,
                "inventory": self.inventory,
                "revenue": round(revenue, 2),
                "profit": round(profit, 2),
                "unmet_demand": unmet_demand,
                "volatility_cost": round(volatility_cost, 2),
                "early_depletion_cost": round(early_depletion_cost, 2),
            },
        )

    def _expected_demand(self, price: float, competitor_price: float, day: int) -> float:
        price_pressure = (self.config.starting_price / price) ** self.config.elasticity
        competitor_effect = 1.0 + 0.35 * ((competitor_price - price) / self.config.starting_price)
        seasonality = 1.0 + self.config.seasonality_strength * math.sin((2 * math.pi * day) / 30.0)
        inventory_effect = 0.75 + 0.25 * min(1.0, self.inventory / self.config.initial_inventory)
        return max(0.0, self.config.base_demand * price_pressure * competitor_effect * seasonality * inventory_effect)

    def _state(self) -> State:
        inventory_bucket = min(5, self.inventory * 6 // max(1, self.config.initial_inventory))
        price_bucket = min(5, max(0, int((self.price - self.config.min_price) / 15)))
        competitor_bucket = 0 if self.price < self.competitor_price - 4 else 1 if self.price <= self.competitor_price + 4 else 2
        season_bucket = (self.day % 30) // 10
        horizon_bucket = min(5, (self.day * 6) // max(1, self.config.episode_length))
        return (inventory_bucket, price_bucket, competitor_bucket, season_bucket, horizon_bucket)

    def _clamp_price(self, value: float) -> float:
        return min(self.config.max_price, max(self.config.min_price, value))
