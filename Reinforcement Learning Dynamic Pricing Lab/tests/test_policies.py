from src.config import ACTION_DELTAS
from src.environment import State
from src.policies import FixedPricePolicy, MyopicGreedyPolicy, RandomPolicy, RuleBasedPolicy


def test_baseline_policies_return_valid_actions() -> None:
    state: State = (4, 2, 1, 1, 2)
    policies = [
        FixedPricePolicy(),
        RandomPolicy(seed=1),
        RuleBasedPolicy(),
        MyopicGreedyPolicy(),
    ]
    for policy in policies:
        assert 0 <= policy.act(state) < len(ACTION_DELTAS)


def test_rule_based_policy_discounts_when_price_is_above_competitor_and_inventory_is_high() -> None:
    policy = RuleBasedPolicy()
    assert policy.act((5, 4, 2, 1, 2)) == 1


def test_fixed_price_policy_holds_price() -> None:
    assert FixedPricePolicy().act((0, 0, 0, 0, 0)) == 2
