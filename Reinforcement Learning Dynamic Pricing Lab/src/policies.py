"""Baseline policies for comparison against learned pricing agents."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Protocol

from .config import ACTION_DELTAS
from .environment import State


class Policy(Protocol):
    """Callable pricing policy."""

    name: str

    def act(self, state: State) -> int:
        """Return an action index for the current state."""


@dataclass
class FixedPricePolicy:
    """Hold price constant throughout the episode."""

    name: str = "fixed_price"

    def act(self, state: State) -> int:
        return 2


@dataclass
class RandomPolicy:
    """Choose any valid action uniformly at random."""

    seed: int = 0
    name: str = "random"

    def __post_init__(self) -> None:
        self.rng = random.Random(self.seed)

    def act(self, state: State) -> int:
        return self.rng.randrange(len(ACTION_DELTAS))


@dataclass
class RuleBasedPolicy:
    """Simple business heuristic that reacts to inventory and relative price."""

    name: str = "rule_based"

    def act(self, state: State) -> int:
        inventory_bucket, price_bucket, competitor_bucket, _season_bucket, _horizon_bucket = state
        if inventory_bucket <= 1:
            return 3 if price_bucket < 5 else 2
        if inventory_bucket >= 4 and competitor_bucket == 2:
            return 1
        if inventory_bucket >= 4 and price_bucket <= 2:
            return 3
        return 2


@dataclass
class MyopicGreedyPolicy:
    """Heuristic that increases price when recent sales are strong."""

    name: str = "myopic_greedy"

    def act(self, state: State) -> int:
        inventory_bucket, price_bucket, competitor_bucket, season_bucket, _horizon_bucket = state
        if inventory_bucket <= 1:
            return 4 if price_bucket < 5 else 2
        if competitor_bucket == 0 and season_bucket == 1:
            return 3
        if competitor_bucket == 2 and inventory_bucket >= 3:
            return 1
        return 2
