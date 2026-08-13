# Agent Lab

Agent Lab is a learn-by-building project for understanding how real AI agents are built.

The goal is not to copy a large framework first. The goal is to grow one small working agent into a production-style agent platform step by step.

## What This Project Will Teach

This project will eventually cover the full agent stack:

- Agent loop
- Tool calling
- Tool registry
- Message history
- Context construction
- Model client abstraction
- State management
- Session persistence
- Long-term memory
- Context compaction
- Planning
- Multi-agent coordination
- Human approval
- Guardrails
- File and research tools
- MCP-style tool server
- Evaluation
- Observability
- Retry, timeout, and error recovery
- Prompt templates
- Skills
- Extensions and plugins
- CLI or simple UI
- Portfolio-ready documentation and demos

## Learning Rule

The project can become large, but each step must stay small.

We will use this rhythm:

```text
Build one tiny feature
Run it
Explain what changed
Connect it to agent theory
Then compare it with a production framework like Pi
```

## Planned Structure

```text
agent-lab/
  core/
    agent_loop.py
    messages.py
    model_client.py
    tools.py
    context.py
    state.py
  tools/
    file_tools.py
    search_tools.py
    math_tools.py
    web_tools.py
    approval_tools.py
  memory/
    session_store.py
    long_term_memory.py
    compaction.py
  planning/
    planner.py
    task_graph.py
    critic.py
  agents/
    research_agent.py
    coding_agent.py
    reviewer_agent.py
    supervisor_agent.py
  safety/
    guardrails.py
    policy.py
    audit_log.py
  evals/
    golden_cases.py
    evaluator.py
    reports.py
  observability/
    tracing.py
    metrics.py
    run_viewer.py
  app/
    cli.py
    ui.py
  examples/
  tests/
  README.md
```

Some files above will be created later. Empty folders mark the learning roadmap.

## Roadmap

### Phase 1: Minimal Agent Heart

Goal: build the smallest working agent loop.

Concepts:

- User message
- Model decision
- Tool call
- Tool result
- Final answer
- Stop condition

Files:

- `core/agent_loop.py`
- `core/tools.py`
- `core/messages.py`
- `app/cli.py`

### Phase 2: Tool System

Goal: make tools feel like a real registry instead of random functions.

Concepts:

- Tool name
- Tool description
- Tool arguments
- Tool validation
- Tool execution
- Tool errors

Files:

- `core/tools.py`
- `tools/math_tools.py`
- `tools/file_tools.py`

### Phase 3: Real Model Client

Goal: replace the fake model with a real LLM.

Concepts:

- Model provider
- API request
- Function calling
- Model response parsing
- Provider abstraction

Files:

- `core/model_client.py`

### Phase 4: Messages and Context

Goal: stop passing one string around and use real message history.

Concepts:

- `user`
- `assistant`
- `tool_call`
- `tool_result`
- context construction
- context trimming

Files:

- `core/messages.py`
- `core/context.py`

### Later Phases

After the core loop is clear, we will add:

- file and research tools
- state, session, and memory
- planning
- multi-agent coordination
- safety and human approval
- MCP-style tool server
- evaluation and observability
- skills, templates, and extensions

## How This Maps to Pi

This project will be compared with Pi as it grows:

```text
Agent Lab agent_loop.py
-> Pi packages/agent/src/agent-loop.ts

Agent Lab tools.py
-> Pi ToolDefinition / AgentTool

Agent Lab messages.py
-> Pi AgentMessage

Agent Lab session_store.py
-> Pi SessionManager

Agent Lab compaction.py
-> Pi compaction system

Agent Lab extensions
-> Pi ExtensionRunner
```

Pi is the production reference. Agent Lab is the learning build.

## Current Status

Created project structure and Phase 1 minimal agent heart.

Note:

```text
CHANGED in the latest lesson:
The agent now records assistant tool_call messages before running tools.
The trace is now: user -> assistant(tool_call) -> tool_result -> assistant(answer).
```

Current runnable demo:

```bash
python app/cli.py "what time is it?"
python app/cli.py "calculate 127*83"
```

Current flow:

```text
user message
-> fake model decides whether to call a tool
-> assistant message records the tool_call
-> tool runs
-> tool_result is added back into messages
-> fake model answers from the updated context
```

Next step:

```text
Explain Phase 1 line by line, then improve the tool system.
```
