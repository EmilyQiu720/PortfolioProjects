# Reinforcement Learning Dynamic Pricing Lab

## Goal

Build a reproducible reinforcement learning lab for dynamic pricing. The project frames pricing as a finite-horizon Markov decision process, trains a tabular Q-learning agent, compares it against business baselines, and evaluates the tradeoff between profit, stockout risk, and price volatility.

## Why This Project Matters

Many reinforcement learning demos stop at a game environment and a single reward curve. This project is designed like a portfolio-grade decision science system: the environment is custom, the reward function is business-aware, the baselines are explicit, and the evaluation reports multiple operational metrics across repeated random seeds.

The goal is not to claim that tabular Q-learning is the final production solution for pricing. The goal is to demonstrate the full RL workflow: define the MDP, encode reward tradeoffs, train a policy, compare against baselines, quantify uncertainty, and produce reviewable artifacts.

## MDP Design

### State

The environment exposes a compact discrete state:

- Inventory bucket
- Price bucket
- Relative competitor price bucket
- Seasonality bucket
- Selling horizon bucket

### Actions

The agent chooses one of five price adjustments:

- Large discount
- Small discount
- Hold price
- Small increase
- Large increase

### Reward

The reward balances business value and operational risk:

```text
reward = gross_profit
       - stockout_penalty
       - low_inventory_penalty
       - early_depletion_penalty
       - price_volatility_penalty
```

This discourages policies that maximize short-term revenue by creating unstable prices, ignoring pacing, or burning through inventory too early.

## Project Structure

```text
Reinforcement Learning Dynamic Pricing Lab/
  README.md
  requirements.txt
  scripts/
    run_experiment.py
  src/
    config.py
    environment.py
    evaluation.py
    plotting.py
    policies.py
    q_learning.py
  tests/
    test_environment.py
    test_policies.py
    test_q_learning.py
  outputs/
    evaluation_summary.csv
    policy_heatmap.svg
    portfolio_preview.svg
    training_curve.svg
```

## Implemented Policies

- `fixed_price`: holds the starting price throughout the episode.
- `random`: selects valid price actions uniformly at random.
- `rule_based`: uses inventory and competitor-price heuristics.
- `myopic_greedy`: increases price when the observed state suggests stronger demand.
- `q_learning`: learned tabular policy trained through epsilon-greedy exploration with conservative pricing guardrails for low-inventory and below-competitor-price states.

## Evaluation Metrics

- Mean episode reward
- 95% confidence interval for reward
- Mean gross profit
- 95% confidence interval for profit
- Mean revenue
- Stockout rate
- Mean price volatility
- Mean final inventory

## Run Locally

```bash
python -m pip install -r requirements.txt
python scripts/run_experiment.py
pytest -q
```

## Results

The experiment writes all reviewable artifacts to `outputs/`:

- `evaluation_summary.csv`: policy-level benchmark table
- `training_curve.svg`: Q-learning reward curve
- `policy_heatmap.svg`: learned action map by inventory and price bucket
- `portfolio_preview.svg`: visual project preview for the portfolio website

## Portfolio Skills Demonstrated

- Reinforcement learning
- Markov decision process design
- Reward shaping
- Tabular Q-learning
- Baseline policy design
- Simulation-based evaluation
- Confidence intervals
- Experiment reproducibility
- Business metric tradeoff analysis
- Portfolio-grade Python project structure
