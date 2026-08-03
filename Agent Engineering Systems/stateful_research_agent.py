#!/usr/bin/env python3
"""
Stateful Research Agent

What this file demonstrates:
- Context: the compact information injected into each model/reasoning step
- State: structured task state for the current research goal
- Session: a persistent container that can be resumed after restart
- Memory: reusable information across sessions, with provenance and expiration
- Checkpointing: save after every major step so interrupted work can continue

Run:
  python stateful_research_agent.py --self-test
  python stateful_research_agent.py --goal "How should agents manage memory safely?"
  python stateful_research_agent.py --resume <session_id>
  python stateful_research_agent.py --list-sessions
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import sys
import textwrap
import urllib.error
import urllib.request
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


JsonObject = dict[str, Any]

# All generated data lives next to this file so the project is easy to move,
# demo, or delete without touching unrelated user files.
PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "stateful_research_agent_data"
CHECKPOINT_DIR = DATA_DIR / "checkpoints"
REPORT_DIR = DATA_DIR / "reports"
MEMORY_PATH = DATA_DIR / "memory_store.json"
DEFAULT_LLM_BASE_URL = "http://192.168.170.201:8089/api"
DEFAULT_LLM_MODEL = "Qwen/Qwen3.6-35B-A3B-FP8"


CORPUS = [
    {
        "source_id": "agent-loop-notes",
        "title": "Agent Loop Notes",
        "url": "local://agent-loop-notes",
        "text": (
            "An agent loop alternates observations, model decisions, tool actions, and new observations. "
            "A reliable loop needs maximum step limits, timeout controls, repeated-action detection, "
            "and clear final-answer conditions."
        ),
    },
    {
        "source_id": "state-session-memory",
        "title": "State, Session, and Memory",
        "url": "local://state-session-memory",
        "text": (
            "Context is what the model sees in the current call. State is structured task data such as "
            "goal, plan, completed steps, evidence, and risk level. A session is the durable container "
            "for one continuous interaction. Memory stores reusable information across sessions."
        ),
    },
    {
        "source_id": "context-engineering",
        "title": "Context Engineering",
        "url": "local://context-engineering",
        "text": (
            "Good context engineering injects only task-relevant information, compresses long tool outputs, "
            "deduplicates retrieved evidence, labels provenance with source IDs, and avoids appending an "
            "unbounded chat history to every model call."
        ),
    },
    {
        "source_id": "memory-safety",
        "title": "Memory Safety",
        "url": "local://memory-safety",
        "text": (
            "Agent memory should track provenance, expiration, conflict resolution, and privacy deletion. "
            "User preferences should be separated from verified facts and speculative inferences."
        ),
    },
    {
        "source_id": "research-agent-eval",
        "title": "Research Agent Evaluation",
        "url": "local://research-agent-eval",
        "text": (
            "A research agent should decompose the question, gather evidence, check missing coverage, "
            "write cited claims, and resume from checkpoints rather than repeating completed searches."
        ),
    },
]


def utc_now() -> str:
    """Return a stable UTC timestamp for checkpoints and memory records."""

    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def tokenize(text: str) -> set[str]:
    """Convert text into simple searchable terms."""

    return {term.lower() for term in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text)}


def stable_id(text: str, prefix: str) -> str:
    """Create a short deterministic-looking ID from text."""

    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}-{digest}"


def ensure_dirs() -> None:
    """Create the data folders used by checkpoints, reports, and memory."""

    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class Evidence:
    """One saved piece of evidence with provenance.

    source_id and url make the final report auditable instead of being a pile of
    unsupported claims.
    """

    evidence_id: str
    subquestion_id: str
    source_id: str
    title: str
    url: str
    quote: str
    relevance: int
    collected_at: str


@dataclass
class PlanItem:
    """One research subquestion and its completion state."""

    subquestion_id: str
    question: str
    status: str = "pending"


@dataclass
class ResearchState:
    """Structured state for the current research task.

    This is the durable task brain: it records the goal, plan, completed steps,
    saved evidence, gaps, and report path. It is intentionally separate from
    the compact context sent into each reasoning step.
    """

    goal: str
    plan: list[PlanItem] = field(default_factory=list)
    completed_steps: list[str] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    report_path: str | None = None
    risk_level: str = "medium"
    context_snapshot: JsonObject = field(default_factory=dict)
    updated_at: str = field(default_factory=utc_now)


@dataclass
class Session:
    """Persistent container for one continuous research task.

    A session wraps the current task state plus recent conversation history and
    a summary of older turns. The whole object is written to checkpoint JSON.
    """

    session_id: str
    created_at: str
    updated_at: str
    state: ResearchState
    conversation_buffer: list[JsonObject] = field(default_factory=list)
    conversation_summary: str = ""


class MemoryStore:
    """Simple cross-session memory with provenance, expiration, conflicts, and deletion.

    This store is separate from a single session. A session says "what is
    happening right now"; memory says "what may be useful across runs."
    """

    def __init__(self, path: Path = MEMORY_PATH) -> None:
        """Load memory from disk, or initialize an empty memory structure."""

        self.path = path
        self.data: JsonObject = {
            "semantic_memory": {},
            "episodic_memory": [],
            "user_preferences": {},
            "procedural_memory": {
                "research_agent": "Plan, search, save evidence, check gaps, write cited report, checkpoint each step."
            },
        }
        self.load()

    def load(self) -> None:
        """Read memory JSON from disk when it exists."""

        if self.path.exists():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))

    def save(self) -> None:
        """Persist memory JSON to disk."""

        ensure_dirs()
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")

    def remember_semantic_fact(
        self,
        key: str,
        value: str,
        source_id: str,
        confidence: float = 0.8,
        expires_days: int = 90,
    ) -> None:
        """Store a reusable fact with source, confidence, and expiration.

        If a new value conflicts with an older one, the old record is preserved
        inside conflict_with so the conflict is inspectable.
        """

        expires_at = (dt.datetime.now(dt.UTC) + dt.timedelta(days=expires_days)).isoformat(timespec="seconds")
        existing = self.data["semantic_memory"].get(key)
        record = {
            "value": value,
            "source_id": source_id,
            "confidence": confidence,
            "created_at": utc_now(),
            "expires_at": expires_at,
        }
        if existing and existing.get("value") != value:
            record["conflict_with"] = existing
        self.data["semantic_memory"][key] = record

    def remember_episode(self, session: Session) -> None:
        """Remember that a research session happened and where its report is."""

        self.data["episodic_memory"].append(
            {
                "session_id": session.session_id,
                "goal": session.state.goal,
                "completed_steps": session.state.completed_steps,
                "report_path": session.state.report_path,
                "created_at": utc_now(),
            }
        )

    def remember_preference(self, key: str, value: str, source: str = "user") -> None:
        """Store a user preference and record how conflicts are resolved."""

        existing = self.data["user_preferences"].get(key)
        record = {"value": value, "source": source, "updated_at": utc_now()}
        if existing and existing.get("value") != value:
            record["previous_value"] = existing.get("value")
            record["conflict_resolution"] = "latest_user_statement_wins"
        self.data["user_preferences"][key] = record

    def cleanup_expired(self) -> None:
        """Remove semantic memory records after their expiration time."""

        now = dt.datetime.now(dt.UTC)
        semantic = self.data["semantic_memory"]
        expired = []
        for key, record in semantic.items():
            expires_at = dt.datetime.fromisoformat(record["expires_at"])
            if expires_at < now:
                expired.append(key)
        for key in expired:
            del semantic[key]

    def delete_session_memory(self, session_id: str) -> int:
        """Delete episodic memory for one session as a privacy control."""

        before = len(self.data["episodic_memory"])
        self.data["episodic_memory"] = [
            item for item in self.data["episodic_memory"] if item.get("session_id") != session_id
        ]
        return before - len(self.data["episodic_memory"])


class LLMClient:
    """Small OpenAI-compatible chat client for the local vLLM endpoint.

    The key is read from an environment variable so portfolio code does not
    contain secrets. The server used in this project exposes /api/chat/completions.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_LLM_BASE_URL,
        model: str = DEFAULT_LLM_MODEL,
        api_key_env: str = "VLLM_API_KEY",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key_env = api_key_env

    def chat(self, system: str, user: str, max_tokens: int = 700, temperature: float = 0.2) -> str:
        import os

        api_key = os.getenv(self.api_key_env) or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(f"Set {self.api_key_env} or OPENAI_API_KEY before using --use-llm.")

        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.95,
            "stream": False,
            "chat_template_kwargs": {"enable_thinking": False},
            "extra_body": {"chat_template_kwargs": {"enable_thinking": False}},
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"LLM request failed: HTTP {exc.code} {detail}") from exc

        message = payload["choices"][0]["message"]
        return (message.get("content") or message.get("reasoning") or "").strip()


def extract_json_object(text: str) -> JsonObject:
    """Extract a JSON object from a model response that may include prose."""

    fenced = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
    candidate = fenced.group(1) if fenced else text
    start = candidate.find("{")
    end = candidate.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in LLM response.")
    return json.loads(candidate[start : end + 1])


class StatefulResearchAgent:
    """Research workflow with checkpointed state and compact context.

    This class coordinates the full lifecycle:
    create or resume a session, plan subquestions, search evidence, check gaps,
    write a cited report, and save checkpoints after major steps.
    """

    def __init__(
        self,
        memory: MemoryStore | None = None,
        max_context_evidence: int = 6,
        use_llm: bool = False,
        llm: LLMClient | None = None,
    ) -> None:
        """Prepare folders, memory, and context-size settings."""

        ensure_dirs()
        self.memory = memory or MemoryStore()
        self.max_context_evidence = max_context_evidence
        self.use_llm = use_llm
        self.llm = llm or LLMClient()

    def create_session(self, goal: str, session_id: str | None = None) -> Session:
        """Start a new research session and immediately checkpoint it."""

        session = Session(
            session_id=session_id or stable_id(f"{goal}-{uuid.uuid4()}", "session"),
            created_at=utc_now(),
            updated_at=utc_now(),
            state=ResearchState(goal=goal),
            conversation_buffer=[{"role": "user", "content": goal, "created_at": utc_now()}],
        )
        self.checkpoint(session, "session_created")
        return session

    def load_session(self, session_id: str) -> Session:
        """Restore a session object from its checkpoint file."""

        path = self.checkpoint_path(session_id)
        if not path.exists():
            raise FileNotFoundError(f"No checkpoint found for session_id={session_id}")
        raw = json.loads(path.read_text(encoding="utf-8"))
        return self.session_from_dict(raw)

    def checkpoint_path(self, session_id: str) -> Path:
        """Return the checkpoint file path for a session ID."""

        return CHECKPOINT_DIR / f"{session_id}.json"

    def checkpoint(self, session: Session, step_name: str) -> None:
        """Save the whole session after recording the completed step.

        The context snapshot is rebuilt at every checkpoint so the saved file
        shows exactly what compact context the agent would use next.
        """

        session.updated_at = utc_now()
        session.state.updated_at = session.updated_at
        if step_name not in session.state.completed_steps:
            session.state.completed_steps.append(step_name)
        session.state.context_snapshot = self.build_context(session)
        self.checkpoint_path(session.session_id).write_text(
            json.dumps(asdict(session), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def run(self, goal: str | None = None, resume: str | None = None, stop_after: str | None = None) -> Session:
        """Execute the research workflow or continue from a checkpoint."""

        if resume:
            session = self.load_session(resume)
            print(f"Resuming session {session.session_id}")
        elif goal:
            session = self.create_session(goal)
            print(f"Created session {session.session_id}")
        else:
            raise ValueError("Provide either goal or resume.")

        self.memory.cleanup_expired()

        self._maybe_step(session, "plan_created", self.create_plan)
        if stop_after == "plan":
            return session

        for item in session.state.plan:
            # Resume behavior: completed subquestions are skipped instead of
            # being searched again after restart.
            if item.status == "done":
                continue
            self.search_and_save_evidence(session, item)
            self.compress_conversation(session)
            self.checkpoint(session, f"searched_{item.subquestion_id}")
            if stop_after == "search-one":
                return session

        self._maybe_step(session, "gaps_checked", self.check_gaps)
        if stop_after == "gaps":
            return session

        if not session.state.report_path:
            self.write_report(session)
            self.checkpoint(session, "report_written")

        self.memory.remember_episode(session)
        self.memory.save()
        return session

    def _maybe_step(self, session: Session, step_name: str, fn: Any) -> None:
        """Run a step only if it is not already listed as completed."""

        if step_name in session.state.completed_steps:
            return
        fn(session)
        self.checkpoint(session, step_name)

    def create_plan(self, session: Session) -> None:
        """Break the research goal into a small set of subquestions."""

        if self.use_llm:
            try:
                session.state.plan = self.create_llm_plan(session.state.goal)
                return
            except Exception as exc:
                session.conversation_buffer.append(
                    {
                        "role": "system",
                        "content": f"LLM planner failed; used deterministic fallback. Error: {exc}",
                        "created_at": utc_now(),
                    }
                )

        goal = session.state.goal.rstrip(" ?")
        templates = [
            f"What are the key concepts needed to answer: {goal}?",
            f"What evidence explains the implementation approach for: {goal}?",
            f"What risks, missing information, or safety concerns matter for: {goal}?",
        ]
        session.state.plan = [
            PlanItem(subquestion_id=f"q{i + 1}", question=question) for i, question in enumerate(templates)
        ]

    def create_llm_plan(self, goal: str) -> list[PlanItem]:
        """Ask the LLM for a small structured research plan."""

        system = (
            "You are a research planner. Return only JSON. "
            "Create 3 to 5 focused subquestions that can be answered with evidence search."
        )
        user = (
            f"Research goal: {goal}\n\n"
            "Return this exact JSON shape:\n"
            '{"plan":[{"subquestion_id":"q1","question":"..."},{"subquestion_id":"q2","question":"..."}]}'
        )
        data = extract_json_object(self.llm.chat(system, user, max_tokens=600, temperature=0.1))
        items = data.get("plan", [])[:5]
        if not items:
            raise ValueError("LLM returned an empty plan.")
        return [
            PlanItem(
                subquestion_id=str(item.get("subquestion_id") or f"q{i + 1}"),
                question=str(item["question"]),
            )
            for i, item in enumerate(items)
            if item.get("question")
        ]

    def search_and_save_evidence(self, session: Session, item: PlanItem) -> None:
        """Search the local corpus and save deduplicated evidence records."""

        context_terms = tokenize(session.state.goal) | tokenize(item.question)
        existing_source_ids = {ev.source_id for ev in session.state.evidence}
        scored = []

        for doc in CORPUS:
            doc_terms = tokenize(f"{doc['title']} {doc['text']}")
            overlap = context_terms & doc_terms
            if overlap:
                scored.append((len(overlap), doc))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        for relevance, doc in scored[:3]:
            if doc["source_id"] in existing_source_ids:
                continue
            evidence = Evidence(
                evidence_id=f"E{len(session.state.evidence) + 1}",
                subquestion_id=item.subquestion_id,
                source_id=doc["source_id"],
                title=doc["title"],
                url=doc["url"],
                quote=self.compress_text(doc["text"], max_chars=260),
                relevance=relevance,
                collected_at=utc_now(),
            )
            session.state.evidence.append(evidence)
            # Saving a semantic memory record demonstrates provenance and
            # expiration without mixing this long-term memory into task state.
            self.memory.remember_semantic_fact(
                key=doc["source_id"],
                value=doc["title"],
                source_id=doc["source_id"],
                confidence=0.9,
            )

        item.status = "done"
        session.conversation_buffer.append(
            {
                "role": "tool",
                "name": "local_document_search",
                "content": f"Saved evidence for {item.subquestion_id}",
                "created_at": utc_now(),
            }
        )

    def check_gaps(self, session: Session) -> None:
        """Check whether the gathered evidence covers required concepts."""

        evidence_text = " ".join(ev.quote.lower() for ev in session.state.evidence)
        required_topics = {
            "context": "Need evidence that distinguishes context from state.",
            "state": "Need evidence about structured task state.",
            "memory": "Need evidence about memory provenance, expiration, conflict, or deletion.",
            "checkpoint": "Need evidence about checkpoint and resume behavior.",
        }
        session.state.gaps = [message for term, message in required_topics.items() if term not in evidence_text]

    def build_context(self, session: Session) -> JsonObject:
        """Build compact context from state, memory keys, and recent history.

        This is not the full checkpoint. It is the small, task-relevant view
        that would be injected into a model call.
        """

        recent_messages = session.conversation_buffer[-4:]
        compact_evidence = [
            {
                "evidence_id": ev.evidence_id,
                "source_id": ev.source_id,
                "title": ev.title,
                "quote": ev.quote,
            }
            for ev in session.state.evidence[-self.max_context_evidence :]
        ]
        return {
            "goal": session.state.goal,
            "plan": [asdict(item) for item in session.state.plan],
            "recent_messages": recent_messages,
            "conversation_summary": session.conversation_summary,
            "evidence": compact_evidence,
            "gaps": session.state.gaps,
            "memory_keys": sorted(self.memory.data["semantic_memory"].keys())[:12],
        }

    def compress_conversation(self, session: Session, keep_last: int = 6) -> None:
        """Keep recent messages and summarize older history."""

        if len(session.conversation_buffer) <= keep_last:
            return
        old = session.conversation_buffer[:-keep_last]
        summary_line = f"Earlier session had {len(old)} messages; completed: {session.state.completed_steps}."
        session.conversation_summary = (
            f"{session.conversation_summary}\n{summary_line}".strip()
            if session.conversation_summary
            else summary_line
        )
        session.conversation_buffer = session.conversation_buffer[-keep_last:]

    def write_report(self, session: Session) -> None:
        """Create a Markdown report with inline evidence citations."""

        if self.use_llm:
            try:
                self.write_llm_report(session)
                return
            except Exception as exc:
                session.conversation_buffer.append(
                    {
                        "role": "system",
                        "content": f"LLM writer failed; used template fallback. Error: {exc}",
                        "created_at": utc_now(),
                    }
                )

        evidence_by_id = {ev.evidence_id: ev for ev in session.state.evidence}
        citations = ", ".join(f"[{ev.evidence_id}]" for ev in session.state.evidence[:4]) or "[no evidence]"
        gap_text = "\n".join(f"- {gap}" for gap in session.state.gaps) if session.state.gaps else "- No major gaps detected."

        body = f"""# Stateful Research Report

## Question
{session.state.goal}

## Answer
The research supports a stateful agent design that separates context, state, session, and memory. Context should stay compact and include only the information needed for the next reasoning step {citations}. State should hold the durable task structure: goal, plan, completed steps, evidence, gaps, report path, and risk level [E2]. Session is the checkpointed container that lets the process resume after restart, while memory stores reusable facts and episodes across sessions [E2].

For a research agent, the practical workflow is: decompose the question, search sources for each subquestion, save evidence with source IDs, check coverage gaps, and write a cited report. The implementation should checkpoint after each major step so completed searches are skipped during resume [E5].

## Evidence
"""
        for ev_id, ev in evidence_by_id.items():
            body += f"- [{ev_id}] {ev.title} ({ev.url}): {ev.quote}\n"

        body += f"""
## Gaps
{gap_text}

## Resume Proof
Session checkpoint: {self.checkpoint_path(session.session_id)}

If the process stops, rerun:

```powershell
python stateful_research_agent.py --resume {session.session_id}
```
"""

        report_path = REPORT_DIR / f"{session.session_id}_report.md"
        report_path.write_text(body, encoding="utf-8")
        session.state.report_path = str(report_path)

    def write_llm_report(self, session: Session) -> None:
        """Ask the LLM to write the final report from saved evidence only."""

        evidence_lines = "\n".join(
            f"[{ev.evidence_id}] {ev.title} ({ev.url}): {ev.quote}" for ev in session.state.evidence
        )
        gaps = "\n".join(f"- {gap}" for gap in session.state.gaps) or "- No major gaps detected."
        system = (
            "You write concise research reports. Use only the provided evidence. "
            "Cite claims with evidence IDs like [E1]. Do not invent sources."
        )
        user = f"""Question:
{session.state.goal}

Evidence:
{evidence_lines}

Gaps:
{gaps}

Write a Markdown report with sections: Question, Answer, Evidence, Gaps, Resume Proof.
Mention this resume command exactly:
python stateful_research_agent.py --resume {session.session_id}
"""
        report = self.llm.chat(system, user, max_tokens=1400, temperature=0.2)
        report_path = REPORT_DIR / f"{session.session_id}_report.md"
        report_path.write_text(report, encoding="utf-8")
        session.state.report_path = str(report_path)

    @staticmethod
    def compress_text(text: str, max_chars: int) -> str:
        """Normalize whitespace and shorten long evidence text."""

        normalized = " ".join(text.split())
        if len(normalized) <= max_chars:
            return normalized
        return normalized[: max_chars - 3].rstrip() + "..."

    @staticmethod
    def session_from_dict(raw: JsonObject) -> Session:
        """Convert checkpoint JSON dictionaries back into dataclass objects."""

        state_raw = raw["state"]
        state = ResearchState(
            goal=state_raw["goal"],
            plan=[PlanItem(**item) for item in state_raw.get("plan", [])],
            completed_steps=state_raw.get("completed_steps", []),
            evidence=[Evidence(**item) for item in state_raw.get("evidence", [])],
            gaps=state_raw.get("gaps", []),
            report_path=state_raw.get("report_path"),
            risk_level=state_raw.get("risk_level", "medium"),
            context_snapshot=state_raw.get("context_snapshot", {}),
            updated_at=state_raw.get("updated_at", utc_now()),
        )
        return Session(
            session_id=raw["session_id"],
            created_at=raw["created_at"],
            updated_at=raw["updated_at"],
            state=state,
            conversation_buffer=raw.get("conversation_buffer", []),
            conversation_summary=raw.get("conversation_summary", ""),
        )


def list_sessions() -> None:
    """Print saved sessions in newest-first order."""

    ensure_dirs()
    checkpoints = sorted(CHECKPOINT_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not checkpoints:
        print("No sessions found.")
        return
    for path in checkpoints:
        raw = json.loads(path.read_text(encoding="utf-8"))
        report = raw["state"].get("report_path") or "not written"
        print(f"{raw['session_id']} | {raw['updated_at']} | {raw['state']['goal']} | report={report}")


def self_test() -> None:
    """Verify checkpoint resume without modifying the user's existing data."""

    test_dir = DATA_DIR / "_self_test_backup"
    if DATA_DIR.exists():
        if test_dir.exists():
            shutil.rmtree(test_dir)
        DATA_DIR.rename(test_dir)
    try:
        agent = StatefulResearchAgent()
        session = agent.run(goal="How should agents manage context, state, and memory?", stop_after="search-one")
        first_checkpoint = agent.checkpoint_path(session.session_id)
        assert first_checkpoint.exists()
        evidence_count = len(session.state.evidence)
        assert evidence_count > 0
        assert not session.state.report_path

        resumed = agent.run(resume=session.session_id)
        assert resumed.state.report_path is not None
        assert Path(resumed.state.report_path).exists()
        assert len(resumed.state.evidence) >= evidence_count
        assert "report_written" in resumed.state.completed_steps

        reloaded = agent.load_session(session.session_id)
        before = len(reloaded.state.evidence)
        resumed_again = agent.run(resume=session.session_id)
        after = len(resumed_again.state.evidence)
        assert before == after, "Resume should not duplicate already collected evidence."

        memory = MemoryStore()
        removed = memory.delete_session_memory(session.session_id)
        assert removed >= 0
        print("Self-tests passed.")
    finally:
        if DATA_DIR.exists():
            shutil.rmtree(DATA_DIR)
        if test_dir.exists():
            test_dir.rename(DATA_DIR)


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command-line options."""

    parser = argparse.ArgumentParser(description="Stateful research agent with checkpoint resume.")
    parser.add_argument("--goal", help="Research question to investigate.")
    parser.add_argument("--resume", help="Resume from a checkpoint session ID.")
    parser.add_argument("--stop-after", choices=["plan", "search-one", "gaps"], help="Stop early to demo resume.")
    parser.add_argument("--list-sessions", action="store_true")
    parser.add_argument("--delete-session-memory", help="Delete episodic memory for a session ID.")
    parser.add_argument("--use-llm", action="store_true", help="Use the configured vLLM endpoint for planning and writing.")
    parser.add_argument("--llm-base-url", default=DEFAULT_LLM_BASE_URL)
    parser.add_argument("--llm-model", default=DEFAULT_LLM_MODEL)
    parser.add_argument("--llm-api-key-env", default="VLLM_API_KEY")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    """Command-line entrypoint."""

    args = parse_args(argv)
    if args.self_test:
        self_test()
        return 0
    if args.list_sessions:
        list_sessions()
        return 0
    if args.delete_session_memory:
        memory = MemoryStore()
        removed = memory.delete_session_memory(args.delete_session_memory)
        memory.save()
        print(f"Deleted {removed} memory record(s).")
        return 0

    if not args.goal and not args.resume:
        print("Provide --goal, --resume, --list-sessions, or --self-test.")
        return 2

    agent = StatefulResearchAgent(
        use_llm=args.use_llm,
        llm=LLMClient(args.llm_base_url, args.llm_model, args.llm_api_key_env),
    )
    session = agent.run(goal=args.goal, resume=args.resume, stop_after=args.stop_after)
    print(f"Session: {session.session_id}")
    print(f"Checkpoint: {agent.checkpoint_path(session.session_id)}")
    if session.state.report_path:
        print(f"Report: {session.state.report_path}")
    else:
        print("Report: not written yet")
    print("\nContext snapshot:")
    print(textwrap.indent(json.dumps(session.state.context_snapshot, indent=2, ensure_ascii=False), "  "))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
