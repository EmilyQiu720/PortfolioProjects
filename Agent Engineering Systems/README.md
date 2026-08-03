# Agent Engineering Systems

This portfolio suite contains ten self-contained Python projects that progress from a minimal tool-calling agent loop to production-grade runtime design, MCP integration, security guardrails, evaluation, training, reinforcement learning, and research benchmarking.

The goal is to demonstrate senior-level agent engineering judgment: controlled tool execution, structured state, checkpointing, observability, security boundaries, evaluation discipline, and research methodology. Each project is dependency-light, documented, and includes a `--self-test` mode so the behavior can be verified without external services.

## Project Map

| Project | File | Engineering Focus |
|---|---|---|
| Tool Calling Agent Loop | `tool_calling_agent_loop.py` | Model-tool-observation loop, Pydantic validation, SQL/document/time/write tools, retries, logging, permissions |
| Stateful Research Agent | `stateful_research_agent.py` | Context engineering, state/session/memory separation, evidence storage, checkpoint resume |
| Workflow Agent Orchestrator | `workflow_agent_orchestrator.py` | Deterministic workflow with dynamic decision nodes, planner-executor, supervisor-worker, handoff, human approval |
| Industrial MCP Server | `industrial_mcp_server.py` | MCP-style host/client/server, tools/resources/prompts, schema validation, RBAC scopes, two-phase approval, audit logs |
| Agent Evaluation Harness | `agent_evaluation_harness.py` | Golden dataset, tool-call metrics, trajectory checks, system metrics, cost per success, regression gates |
| Production Agent Observability | `production_agent_observability.py` | API gateway, queue, runtime, state/memory/artifact stores, tracing, reliability patterns, model/tool fallback |
| Agent Security Guardrails | `agent_security_guardrails.py` | Prompt injection detection, least privilege, tenant isolation, sandboxing, DLP, kill switch, dry-run and approval gates |
| Advanced Agent Architecture | `advanced_agent_architecture.py` | Hierarchical planning, dependency graph, critical path, verifier, dynamic replanning, long-task workspace |
| Agent Training and RL Lab | `agent_training_rl_lab.py` | Trajectory collection, tool-call SFT data, negative examples, reward shaping, offline RL simulation |
| Agent Research Benchmark Lab | `agent_research_benchmark_lab.py` | Controlled benchmark, ablations, confidence intervals, contamination checks, scaffold-vs-model gain analysis |

## Why This Project Matters

Most agent demos stop at "the model called a tool." This suite focuses on what makes agents reliable in real systems:

- **Execution control:** Tools validate parameters, enforce scopes, separate reads from writes, and require approval for risky actions.
- **Stateful operation:** Sessions, checkpoints, memory, artifacts, and ledgers make long-running work inspectable and resumable.
- **Production readiness:** Runtime services track latency, tokens, cost, retries, timeouts, fallback paths, and human interventions.
- **Security by construction:** Prompt injection, memory poisoning, unsafe SQL/shell/network calls, tenant leaks, and secret exposure are blocked at execution boundaries.
- **Evaluation discipline:** Golden datasets, trajectory-level metrics, regression gates, and cost-per-success prevent subjective quality claims.
- **Research maturity:** Training data construction, reward modeling, ablations, confidence intervals, and contamination checks distinguish real agent capability from scaffold effects.

## Quick Start

Run all self-tests:

```powershell
python .\run_all_self_tests.py
```

Run an individual project:

```powershell
python .\tool_calling_agent_loop.py --self-test
python .\stateful_research_agent.py --self-test
python .\workflow_agent_orchestrator.py --self-test
python .\industrial_mcp_server.py --self-test
python .\agent_evaluation_harness.py --self-test
python .\production_agent_observability.py --self-test
python .\agent_security_guardrails.py --self-test
python .\advanced_agent_architecture.py --self-test
python .\agent_training_rl_lab.py --self-test
python .\agent_research_benchmark_lab.py --self-test
```

## Optional Local LLM Integration

`stateful_research_agent.py` and `workflow_agent_orchestrator.py` support an optional `--use-llm` mode for OpenAI-compatible vLLM endpoints:

```powershell
$env:VLLM_API_KEY="your_key"
python .\stateful_research_agent.py --use-llm --goal "How should agent memory be managed safely?"
python .\workflow_agent_orchestrator.py --use-llm --goal "Compare workflow and agent orchestration patterns"
```

The default mode remains deterministic so reviewers can run and test the suite without credentials.

## Design Notes

- All projects are single-file by design for portfolio review and easy execution.
- Generated runtime data is written into project-specific `*_data` folders.
- Dangerous actions are simulated behind approval, dry-run, and sandbox controls.
- The code intentionally favors explicit state machines and typed records over hidden framework behavior.
