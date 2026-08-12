from src.config import ACTION_DELTAS
from src.environment import DynamicPricingEnvironment


def test_reset_returns_discrete_state() -> None:
    env = DynamicPricingEnvironment(seed=123)
    state = env.reset()
    assert len(state) == 5
    assert all(isinstance(value, int) for value in state)


def test_step_updates_inventory_and_respects_price_bounds() -> None:
    env = DynamicPricingEnvironment(seed=123)
    env.reset()
    for _ in range(12):
        result = env.step(len(ACTION_DELTAS) - 1)
        assert env.config.min_price <= result.info["price"] <= env.config.max_price
        assert 0 <= result.info["inventory"] <= env.config.initial_inventory
        if result.done:
            break


def test_invalid_action_raises_value_error() -> None:
    env = DynamicPricingEnvironment(seed=123)
    env.reset()
    try:
        env.step(99)
    except ValueError as exc:
        assert "action must be" in str(exc)
    else:
        raise AssertionError("invalid action should raise ValueError")
