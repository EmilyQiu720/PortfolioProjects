# PortfolioProjects

This repository contains selected portfolio projects across machine learning, optimization, databases, analytics, and agent engineering.

## Featured Project

### Agent Engineering Systems

[`Agent Engineering Systems`](./Agent%20Engineering%20Systems) is a ten-project Python suite covering practical agent engineering from first principles through production and research workflows:

- Tool-calling agent loop with validation, retries, logging, and permission controls
- Stateful research agent with context engineering, memory, evidence, and checkpoint resume
- Workflow orchestration with router, planner-executor, supervisor-worker, handoff, and approval gates
- Industrial MCP-style server with tools, resources, prompts, schema validation, RBAC scopes, audit logs, and two-phase write approval
- Agent evaluation harness with golden datasets, trajectory metrics, system metrics, and regression gates
- Production observability runtime with gateway, queue, stores, tracing, retries, fallbacks, circuit breakers, bulkheads, and cost-per-success metrics
- Security guardrail layer for prompt injection, sandboxing, tenant isolation, SQL/shell/network allowlists, DLP, and kill switch behavior
- Advanced architecture lab for hierarchical planning, dependency graphs, critical path analysis, verifier-guided replanning, long-task checkpoints, and multi-agent coordination
- Training and reinforcement learning lab for trajectory collection, tool-call SFT data, negative examples, reward shaping, offline RL, and deterministic replay
- Research benchmark lab for ablations, confidence intervals, contamination checks, token budget control, and scaffold-vs-model gain analysis

Each module is self-contained, documented, and runnable through `--self-test`.
