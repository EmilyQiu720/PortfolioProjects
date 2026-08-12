"""Run the full dynamic pricing RL experiment."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import TrainingConfig
from src.evaluation import evaluate_policy, write_summary_csv
from src.plotting import plot_policy_heatmap, plot_training_curve, write_portfolio_preview
from src.policies import FixedPricePolicy, MyopicGreedyPolicy, RandomPolicy, RuleBasedPolicy
from src.q_learning import QLearningPolicy, train_q_learning


def main() -> None:
    config = TrainingConfig()
    training = train_q_learning(seed=720, config=config)
    learned_policy = QLearningPolicy(training.q_table)
    evaluation_seeds = [10_000 + index for index in range(config.evaluation_episodes)]
    policies = [
        learned_policy,
        RuleBasedPolicy(),
        MyopicGreedyPolicy(),
        FixedPricePolicy(),
        RandomPolicy(seed=720),
    ]
    summaries = [evaluate_policy(policy, evaluation_seeds) for policy in policies]

    outputs = ROOT / "outputs"
    write_summary_csv(outputs / "evaluation_summary.csv", summaries)
    plot_training_curve(outputs / "training_curve.svg", training.episode_rewards)
    plot_policy_heatmap(outputs / "policy_heatmap.svg", training.q_table)
    write_portfolio_preview(outputs / "portfolio_preview.svg", summaries)

    print("Policy comparison:")
    for summary in sorted(summaries, key=lambda item: item.mean_profit, reverse=True):
        print(
            f"- {summary.policy}: mean_profit=${summary.mean_profit:,.2f}, "
            f"reward={summary.mean_reward:,.2f}, stockout_rate={summary.stockout_rate:.2%}, "
            f"price_volatility={summary.mean_price_volatility:.2f}"
        )
    print(f"\nArtifacts written to: {outputs}")


if __name__ == "__main__":
    main()
