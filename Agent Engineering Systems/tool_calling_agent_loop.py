#!/usr/bin/env python3
"""
Tool Calling Agent Loop

What it demonstrates:
- Receive a user goal
- Build model context and tool definitions
- Let the model choose final answer or tool calls
- Validate tool arguments before execution
- Execute tools with timeout/error handling
- Write tool observations back into the loop
- Stop with clear termination limits

Run:
  python tool_calling_agent_loop.py --self-test
  set OPENAI_API_KEY=your_key
  python tool_calling_agent_loop.py --verbose "calculate 127*83 and tell me the time in Asia/Shanghai"
"""

from __future__ import annotations

import argparse
import ast
import concurrent.futures
import datetime as dt
import json
import logging
import math
import os
import re
import sqlite3
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Type
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, ValidationError as PydanticValidationError


JsonObject = dict[str, Any]


class AgentError(Exception):
    """Base error for the demo agent."""


class ToolExecutionError(AgentError):
    """Raised when a tool fails at runtime."""


class StrictArgs(BaseModel):
    """Base class for all tool argument models.

    extra="forbid" means a model cannot sneak in unexpected fields. This is
    important because tool calls come from an LLM, not from trusted code.
    """

    model_config = ConfigDict(extra="forbid")


class CalculatorArgs(StrictArgs):
    """Arguments accepted by the calculator tool."""

    expression: str = Field(
        min_length=1,
        max_length=200,
        description="A numeric arithmetic expression, for example '127 * 83'.",
    )


class SqlQueryArgs(StrictArgs):
    """Arguments accepted by the read-only SQL tool."""

    query: str = Field(
        min_length=1,
        max_length=500,
        description="A read-only SELECT query against the demo defects table.",
    )


class DocumentSearchArgs(StrictArgs):
    """Arguments accepted by the local document retrieval tool."""

    query: str = Field(min_length=1, max_length=200, description="Search query.")
    top_k: int = Field(default=3, ge=1, le=5, description="Number of matching snippets to return.")


class CurrentTimeArgs(StrictArgs):
    """Arguments accepted by the timezone lookup tool."""

    timezone: str = Field(
        min_length=1,
        max_length=80,
        description="IANA timezone name, such as 'Asia/Shanghai' or 'America/New_York'.",
    )


class WriteNoteArgs(StrictArgs):
    """Arguments accepted by the write tool.

    The write tool is treated as a side-effecting action, so it also needs
    runtime permission through --allow-writes.
    """

    filename: str = Field(
        min_length=1,
        max_length=80,
        description="Plain filename only. Folders are not allowed.",
    )
    content: str = Field(min_length=1, max_length=5000, description="Text content to write.")


@dataclass(frozen=True)
class ToolSpec:
    """Runtime definition for one tool the agent can call.

    The same ToolSpec is used in two places:
    - to expose a JSON schema to the model through the OpenAI tools parameter
    - to validate and execute the local Python handler when the model calls it
    """

    name: str
    description: str
    args_model: Type[BaseModel]
    handler: Callable[[BaseModel], JsonObject]
    timeout_seconds: float = 5.0
    max_retries: int = 1
    side_effect: bool = False

    def as_openai_tool(self) -> JsonObject:
        """Convert a local tool definition into the Responses API tool format."""
        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": self.args_model.model_json_schema(),
            "strict": True,
        }


def safe_calculate(args: BaseModel) -> JsonObject:
    """Evaluate arithmetic after checking the expression's AST.

    This avoids directly trusting eval() on model-generated text. Only numeric
    constants and basic operators are allowed; calls, imports, names, and
    attribute access are rejected before execution.
    """

    expression = args.expression
    tree = ast.parse(expression, mode="eval")
    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.FloorDiv,
        ast.Mod,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.Load,
    )
    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            raise ToolExecutionError(f"Unsupported expression element: {type(node).__name__}")
        if isinstance(node, ast.Constant) and not isinstance(node.value, (int, float)):
            raise ToolExecutionError("Only numeric constants are allowed.")

    # eval is only reached after the AST whitelist passes. Builtins are also
    # removed so functions like open(), eval(), and __import__ are unavailable.
    result = eval(compile(tree, "<calculator>", "eval"), {"__builtins__": {}}, {})
    if not isinstance(result, (int, float)) or not math.isfinite(result):
        raise ToolExecutionError("Calculation did not produce a finite number.")
    return {"ok": True, "expression": expression, "result": result}


def sql_query(args: BaseModel) -> JsonObject:
    """Run a SELECT-only query against a small in-memory demo database."""

    query = args.query.strip()
    # The SQL tool is intentionally read-only. This guards both accidental
    # misuse and prompt-injection attempts that try to turn a query into a write.
    if not re.match(r"(?is)^\s*select\b", query):
        raise ToolExecutionError("Only SELECT queries are allowed.")
    blocked = re.search(r"(?is)\b(insert|update|delete|drop|alter|create|replace|attach|pragma)\b", query)
    if blocked or ";" in query.rstrip(";"):
        raise ToolExecutionError("Query contains a blocked SQL operation.")

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE defects (
            id INTEGER PRIMARY KEY,
            panel_id TEXT,
            batch TEXT,
            defect_type TEXT,
            severity INTEGER,
            station TEXT
        );
        INSERT INTO defects(panel_id, batch, defect_type, severity, station) VALUES
            ('P-1001', 'B-07', 'scratch', 3, 'AOI-1'),
            ('P-1002', 'B-07', 'particle', 2, 'AOI-1'),
            ('P-1003', 'B-08', 'offset', 5, 'AOI-2'),
            ('P-1004', 'B-08', 'scratch', 4, 'AOI-2');
        """
    )
    rows = conn.execute(query).fetchmany(20)
    return {"ok": True, "rows": [dict(row) for row in rows], "row_count": len(rows)}


DOCUMENTS = [
    {
        "id": "doc-agent-loop",
        "title": "Agent Loop",
        "text": "An agent loop alternates model decisions, tool execution, observations, and final answers.",
    },
    {
        "id": "doc-tool-safety",
        "title": "Tool Safety",
        "text": "Tools should validate arguments, set timeouts, separate read and write permissions, and log calls.",
    },
    {
        "id": "doc-evaluation",
        "title": "Evaluation",
        "text": "Agent evaluation checks final answers, tool selection, arguments, trajectory quality, latency, and cost.",
    },
    {
        "id": "doc-state",
        "title": "State",
        "text": "State stores the current goal, completed steps, tool results, risk level, and checkpoint metadata.",
    },
]


def document_search(args: BaseModel) -> JsonObject:
    """Search a tiny local document set and return ranked snippets."""

    terms = {term.lower() for term in re.findall(r"\w+", args.query)}
    scored = []
    for doc in DOCUMENTS:
        haystack = f"{doc['title']} {doc['text']}".lower()
        score = sum(1 for term in terms if term in haystack)
        if score:
            scored.append((score, doc))
    scored.sort(key=lambda item: item[0], reverse=True)
    matches = [
        {"id": doc["id"], "title": doc["title"], "snippet": doc["text"], "score": score}
        for score, doc in scored[: args.top_k]
    ]
    return {"ok": True, "matches": matches, "query": args.query}


def current_time(args: BaseModel) -> JsonObject:
    """Return the current time in a requested IANA timezone."""

    timezone = args.timezone
    now = dt.datetime.now(ZoneInfo(timezone))
    return {
        "ok": True,
        "timezone": timezone,
        "iso_time": now.isoformat(timespec="seconds"),
        "utc_offset": now.strftime("%z"),
    }


def write_note(args: BaseModel) -> JsonObject:
    """Write a text note into a controlled Desktop output folder."""

    desktop = Path.home() / "Desktop"
    out_dir = desktop / "agent_loop_outputs"
    out_dir.mkdir(exist_ok=True)

    filename = args.filename.strip()
    if not filename.endswith(".txt"):
        filename += ".txt"
    if Path(filename).name != filename:
        raise ToolExecutionError("filename must not include folders.")

    target = out_dir / filename
    target.write_text(args.content, encoding="utf-8")
    return {"ok": True, "path": str(target), "bytes": target.stat().st_size}


def build_tools() -> dict[str, ToolSpec]:
    """Register all tools available to the agent.

    Adding a new tool usually means adding:
    1. a Pydantic argument model
    2. a handler function
    3. a ToolSpec entry here
    """

    tools = [
        ToolSpec(
            name="calculator",
            description="Safely evaluate a basic arithmetic expression. Supports +, -, *, /, //, %, and **.",
            args_model=CalculatorArgs,
            handler=safe_calculate,
        ),
        ToolSpec(
            name="sql_query",
            description="Run a read-only SELECT query against a small demo defects database.",
            args_model=SqlQueryArgs,
            handler=sql_query,
        ),
        ToolSpec(
            name="document_search",
            description="Search local teaching notes about agent loops, tool safety, state, and evaluation.",
            args_model=DocumentSearchArgs,
            handler=document_search,
        ),
        ToolSpec(
            name="current_time",
            description="Return the current date and time for an IANA timezone.",
            args_model=CurrentTimeArgs,
            handler=current_time,
        ),
        ToolSpec(
            name="write_note",
            description="Write a text note into a safe output folder on the user's Desktop.",
            args_model=WriteNoteArgs,
            handler=write_note,
            side_effect=True,
        ),
    ]
    return {tool.name: tool for tool in tools}


def execute_tool(
    tool: ToolSpec,
    raw_arguments: str,
    allow_writes: bool = False,
    logger: logging.Logger | None = None,
) -> JsonObject:
    """Validate, authorize, retry, and execute one tool call.

    This is the safety boundary between the model and the local machine. The
    model may request a tool call, but this function decides whether the call is
    valid, permitted, and completed within the timeout.
    """

    if tool.side_effect and not allow_writes:
        result = {
            "ok": False,
            "error_type": "permission_denied",
            "message": "Write tools require --allow-writes.",
        }
        if logger:
            logger.warning("tool=%s permission_denied", tool.name)
        return result

    try:
        raw_args = json.loads(raw_arguments or "{}")
        # Pydantic turns untrusted JSON into a typed object or rejects it.
        args = tool.args_model.model_validate(raw_args)
    except (json.JSONDecodeError, PydanticValidationError) as exc:
        return {"ok": False, "error_type": "validation_error", "message": str(exc)}

    last_error: JsonObject | None = None
    for attempt in range(1, tool.max_retries + 2):
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(tool.handler, args)
                result = future.result(timeout=tool.timeout_seconds)
                if logger:
                    logger.info("tool=%s attempt=%s ok=true", tool.name, attempt)
                return result
        except concurrent.futures.TimeoutError:
            last_error = {
                "ok": False,
                "error_type": "timeout",
                "message": f"Tool timed out after {tool.timeout_seconds} seconds.",
            }
        except Exception as exc:
            last_error = {"ok": False, "error_type": "execution_error", "message": str(exc)}

        if logger:
            logger.warning("tool=%s attempt=%s error=%s", tool.name, attempt, last_error)
        if attempt <= tool.max_retries:
            time.sleep(0.2 * attempt)

    return last_error or {"ok": False, "error_type": "unknown_error", "message": "Tool failed."}


def configure_logger(verbose: bool) -> logging.Logger:
    """Create a file logger for tool calls, errors, and stopping conditions."""

    out_dir = Path.home() / "Desktop" / "agent_loop_outputs"
    out_dir.mkdir(exist_ok=True)
    logger = logging.getLogger("agent_loop")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_handler = logging.FileHandler(out_dir / "agent_loop.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if verbose:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    return logger


def extract_function_calls(response: Any) -> list[Any]:
    """Pull function_call items out of a Responses API result."""

    calls: list[Any] = []
    for item in getattr(response, "output", []) or []:
        if getattr(item, "type", None) == "function_call":
            calls.append(item)
    return calls


def response_text(response: Any) -> str:
    """Read final assistant text from a Responses API result."""

    text = getattr(response, "output_text", None)
    if text:
        return text

    chunks: list[str] = []
    for item in getattr(response, "output", []) or []:
        if getattr(item, "type", None) == "message":
            for content in getattr(item, "content", []) or []:
                if getattr(content, "type", None) in {"output_text", "text"}:
                    chunks.append(getattr(content, "text", ""))
    return "\n".join(chunk for chunk in chunks if chunk).strip()


class AgentLoop:
    """A small but complete model-tool-observation loop.

    The loop asks the model what to do next. If the model returns tool calls,
    the program validates and executes them, sends the observations back, and
    repeats. If the model returns normal text, the task is complete.
    """

    def __init__(
        self,
        model: str,
        max_steps: int = 8,
        max_tool_calls: int = 12,
        max_seconds: float = 60.0,
        allow_writes: bool = False,
        verbose: bool = False,
    ) -> None:
        """Configure runtime limits and permissions for one agent run."""

        self.model = model
        self.max_steps = max_steps
        self.max_tool_calls = max_tool_calls
        self.max_seconds = max_seconds
        self.allow_writes = allow_writes
        self.verbose = verbose
        self.tools = build_tools()
        self.logger = configure_logger(verbose)

    def run(self, goal: str) -> str:
        """Run the agent until it returns a final answer or hits a stop limit."""

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise AgentError("Install the OpenAI SDK first: python -m pip install -U openai") from exc

        client = OpenAI()
        started = time.monotonic()
        tool_calls_seen = 0
        seen_call_signatures: set[str] = set()

        instructions = (
            "You are a concise tool-using agent. Decide whether to answer directly or call tools. "
            "Use tools when calculation, SQL lookup, document retrieval, current time, or writing a note is required. "
            "After tool results arrive, continue reasoning and finish when the user's goal is satisfied. "
            "If a goal cannot be completed safely, explain why."
        )

        # First model call: provide the user goal and all available tool schemas.
        response = client.responses.create(
            model=self.model,
            instructions=instructions,
            input=f"User goal: {goal}",
            tools=[tool.as_openai_tool() for tool in self.tools.values()],
        )

        for step in range(1, self.max_steps + 1):
            self.logger.info("step=%s status=started", step)
            if time.monotonic() - started > self.max_seconds:
                self.logger.warning("agent stopped=max_seconds")
                return "Stopped: maximum execution time reached."

            calls = extract_function_calls(response)
            if not calls:
                return response_text(response) or "Stopped: model returned no final text."

            outputs: list[JsonObject] = []
            for call in calls:
                tool_calls_seen += 1
                if tool_calls_seen > self.max_tool_calls:
                    self.logger.warning("agent stopped=max_tool_calls")
                    return "Stopped: maximum tool-call count reached."

                name = getattr(call, "name", "")
                arguments = getattr(call, "arguments", "{}")
                signature = f"{name}:{arguments}"
                # A repeated identical tool call usually means the model is
                # stuck, so stop before burning more time and tokens.
                if signature in seen_call_signatures:
                    self.logger.warning("agent stopped=repeated_tool tool=%s", name)
                    return f"Stopped: repeated tool call detected for {name}."
                seen_call_signatures.add(signature)

                tool = self.tools.get(name)
                if tool is None:
                    result = {"ok": False, "error_type": "unknown_tool", "message": name}
                else:
                    result = execute_tool(tool, arguments, allow_writes=self.allow_writes, logger=self.logger)

                if self.verbose:
                    print(f"[step {step}] {name}({arguments}) -> {json.dumps(result, ensure_ascii=False)}")

                outputs.append(
                    {
                        "type": "function_call_output",
                        # call_id links this result to the exact function call
                        # the model made, which matters when there are multiple
                        # tool calls in one turn.
                        "call_id": getattr(call, "call_id"),
                        "output": json.dumps(result, ensure_ascii=False),
                    }
                )

            # Feed tool observations back into the same response thread so the
            # model can decide whether to call another tool or finish.
            response = client.responses.create(
                model=self.model,
                previous_response_id=response.id,
                input=outputs,
                tools=[tool.as_openai_tool() for tool in self.tools.values()],
            )

        self.logger.warning("agent stopped=max_steps")
        return "Stopped: maximum step count reached."


def self_test() -> None:
    """Run local tests that do not require an API key."""

    tools = build_tools()
    logger = configure_logger(False)
    calc = execute_tool(tools["calculator"], json.dumps({"expression": "127 * 83"}), logger=logger)
    assert calc["ok"] is True and calc["result"] == 10541

    bad_calc = execute_tool(tools["calculator"], json.dumps({"expression": "__import__('os').system('x')"}), logger=logger)
    assert bad_calc["ok"] is False

    validation = execute_tool(tools["current_time"], json.dumps({"tz": "Asia/Shanghai"}), logger=logger)
    assert validation["ok"] is False and validation["error_type"] == "validation_error"

    now = execute_tool(tools["current_time"], json.dumps({"timezone": "Asia/Shanghai"}), logger=logger)
    assert now["ok"] is True and "iso_time" in now

    sql = execute_tool(tools["sql_query"], json.dumps({"query": "SELECT batch, COUNT(*) AS n FROM defects GROUP BY batch"}), logger=logger)
    assert sql["ok"] is True and sql["row_count"] >= 1

    blocked_sql = execute_tool(tools["sql_query"], json.dumps({"query": "DROP TABLE defects"}), logger=logger)
    assert blocked_sql["ok"] is False

    docs = execute_tool(tools["document_search"], json.dumps({"query": "tool safety", "top_k": 2}), logger=logger)
    assert docs["ok"] is True and docs["matches"]

    denied_write = execute_tool(
        tools["write_note"],
        json.dumps({"filename": "agent_test.txt", "content": "hello"}),
        allow_writes=False,
        logger=logger,
    )
    assert denied_write["ok"] is False and denied_write["error_type"] == "permission_denied"

    print("Self-tests passed.")


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command-line options for local testing and interactive runs."""

    parser = argparse.ArgumentParser(description="Tool calling agent loop.")
    parser.add_argument("goal", nargs="*", help="User goal. If omitted, interactive mode starts.")
    parser.add_argument("--model", default=os.getenv("AGENT_MODEL", "gpt-5-mini"))
    parser.add_argument("--max-steps", type=int, default=8)
    parser.add_argument("--max-tool-calls", type=int, default=12)
    parser.add_argument("--max-seconds", type=float, default=60.0)
    parser.add_argument("--allow-writes", action="store_true", help="Allow side-effect tools such as write_note.")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    """Command-line entrypoint."""

    args = parse_args(argv)
    if args.self_test:
        self_test()
        return 0

    goal = " ".join(args.goal).strip()
    if not goal:
        goal = input("Goal> ").strip()
    if not goal:
        print("No goal provided.")
        return 2

    agent = AgentLoop(
        model=args.model,
        max_steps=args.max_steps,
        max_tool_calls=args.max_tool_calls,
        max_seconds=args.max_seconds,
        allow_writes=args.allow_writes,
        verbose=args.verbose,
    )
    print(agent.run(goal))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
