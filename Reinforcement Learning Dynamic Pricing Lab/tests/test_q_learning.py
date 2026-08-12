from src.config import TrainingConfig
from src.evaluation import evaluate_policy
from src.q_learning import QLearningPolicy, train_q_learning


def test_q_learning_produces_q_table_and_reward_history() -> None:
    config = TrainingConfig(episodes=25, evaluation_episodes=5, seeds=(1,))
    result = train_q_learning(seed=42, config=config)
    assert len(result.episode_rewards) == 25
    assert len(result.episode_profits) == 25
    assert result.q_table


def test_trained_policy_can_be_evaluated() -> None:
    config = TrainingConfig(episodes=25, evaluation_episodes=5, seeds=(1,))
    result = train_q_learning(seed=42, config=config)
    summary = evaluate_policy(QLearningPolicy(result.q_table), [100, 101, 102])
    assert summary.policy == "q_learning"
    assert summary.mean_profit > 0
    assert 0 <= summary.stockout_rate <= 1
