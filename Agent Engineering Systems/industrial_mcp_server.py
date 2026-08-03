#!/usr/bin/env python3
"""
Industrial Inspection MCP Server

This portfolio project implements a local MCP-style integration layer for an
industrial inspection system. It uses JSON-RPC-shaped messages and demonstrates
the server-side responsibilities that matter when an agent gets access to
external systems:

- capability negotiation and server discovery
- tools, resources, and prompt templates
- input and output schemas
- read/write tool separation
- role and scope based authorization
- two-phase write approval: prepare -> approve -> commit
- audit logging for every security-relevant step
- local CLI transport and stdio JSON-RPC transport
- a tiny host/client pair that discovers and calls the server

Run:
  python industrial_mcp_server.py --self-test
  python industrial_mcp_server.py --discover
  python industrial_mcp_server.py --list-tools --role viewer
  python industrial_mcp_server.py --role engineer --call run_rca --arguments "{\"panel_id\":\"P-1003\",\"include_model_metrics\":true}"
  python industrial_mcp_server.py --role engineer --call create_retrain_request --arguments "{\"model_name\":\"defect-cnn-v4\",\"reason\":\"drift score exceeded threshold\",\"priority\":\"high\"}"
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable


JsonObject = dict[str, Any]
PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "industrial_mcp_server_data"
AUDIT_LOG = DATA_DIR / "audit_log.jsonl"
APPROVALS_PATH = DATA_DIR / "approvals.json"
RETRAIN_REQUESTS_PATH = DATA_DIR / "retrain_requests.json"
SERVER_NAME = "industrial-inspection-mcp"
SERVER_VERSION = "2.0.0"
PROTOCOL_VERSION = "2025-06-18"
TOOL_SCHEMA_VERSION = "inspection-tools.v2"


def utc_now() -> str:
    """Return a stable UTC timestamp for audit records and artifacts."""

    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def ensure_dirs() -> None:
    """Create the project data folder."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)


class JsonRpcCode:
    """JSON-RPC standard and application-specific error codes."""

    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    PERMISSION_DENIED = -32003
    NOT_FOUND = -32004
    APPROVAL_REQUIRED = -32010
    TOOL_EXECUTION_FAILED = -32020
    OUTPUT_SCHEMA_FAILED = -32021


class MCPError(Exception):
    """Error type returned through JSON-RPC error responses."""

    def __init__(self, code: int, message: str, data: JsonObject | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data or {}


class Role(str, Enum):
    """Demo roles. Real systems would map these from IAM claims."""

    VIEWER = "viewer"
    ENGINEER = "engineer"
    MAINTAINER = "maintainer"
    ADMIN = "admin"


ROLE_SCOPES: dict[Role, set[str]] = {
    Role.VIEWER: {"defects:read", "panels:read", "models:read", "resources:read", "prompts:read"},
    Role.ENGINEER: {
        "defects:read",
        "panels:read",
        "cad:read",
        "models:read",
        "rca:run",
        "retrain:prepare",
        "resources:read",
        "prompts:read",
    },
    Role.MAINTAINER: {
        "defects:read",
        "panels:read",
        "cad:read",
        "models:read",
        "rca:run",
        "retrain:prepare",
        "retrain:commit",
        "approval:grant",
        "resources:read",
        "prompts:read",
    },
    Role.ADMIN: {"*"},
}


def has_scope(role: Role, scope: str) -> bool:
    scopes = ROLE_SCOPES[role]
    return "*" in scopes or scope in scopes


class ToolMode(str, Enum):
    READ = "read"
    WRITE = "write"


class WritePhase(str, Enum):
    NONE = "none"
    PREPARE = "prepare"
    COMMIT = "commit"


@dataclass
class CallerContext:
    """Identity context attached to every host/client request."""

    role: Role = Role.VIEWER
    subject: str = "local-demo-user"
    request_id: str = field(default_factory=lambda: f"req-{uuid.uuid4().hex[:10]}")


@dataclass(frozen=True)
class ToolDefinition:
    """Tool metadata, schemas, permission requirements, and handler."""

    name: str
    description: str
    input_schema: JsonObject
    output_schema: JsonObject
    handler: Callable[[JsonObject], JsonObject]
    mode: ToolMode
    required_scopes: set[str]
    version: str = TOOL_SCHEMA_VERSION
    write_phase: WritePhase = WritePhase.NONE
    requires_approval: bool = False

    def public_descriptor(self) -> JsonObject:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
            "outputSchema": self.output_schema,
            "annotations": {
                "mode": self.mode.value,
                "version": self.version,
                "requiredScopes": sorted(self.required_scopes),
                "writePhase": self.write_phase.value,
                "requiresApproval": self.requires_approval,
            },
        }


class SchemaValidator:
    """JSON Schema subset validator for tool inputs and outputs.

    A production server would use a full JSON Schema implementation. This
    dependency-free subset supports the shapes used in this project, including
    nested objects and arrays.
    """

    @classmethod
    def validate(cls, schema: JsonObject, value: Any, path: str = "$") -> None:
        expected = schema.get("type")
        if expected == "object":
            if not isinstance(value, dict):
                raise MCPError(JsonRpcCode.INVALID_PARAMS, f"{path} must be an object.")
            properties = schema.get("properties", {})
            required = set(schema.get("required", []))
            missing = sorted(required - set(value))
            if missing:
                raise MCPError(JsonRpcCode.INVALID_PARAMS, f"{path} missing required: {', '.join(missing)}")
            if schema.get("additionalProperties") is False:
                extra = sorted(set(value) - set(properties))
                if extra:
                    raise MCPError(JsonRpcCode.INVALID_PARAMS, f"{path} unknown fields: {', '.join(extra)}")
            for key, child_schema in properties.items():
                if key in value:
                    cls.validate(child_schema, value[key], f"{path}.{key}")
            return
        if expected == "array":
            if not isinstance(value, list):
                raise MCPError(JsonRpcCode.INVALID_PARAMS, f"{path} must be an array.")
            item_schema = schema.get("items")
            if item_schema:
                for index, item in enumerate(value):
                    cls.validate(item_schema, item, f"{path}[{index}]")
            return
        if expected == "string" and not isinstance(value, str):
            raise MCPError(JsonRpcCode.INVALID_PARAMS, f"{path} must be a string.")
        if expected == "integer" and not isinstance(value, int):
            raise MCPError(JsonRpcCode.INVALID_PARAMS, f"{path} must be an integer.")
        if expected == "number" and not isinstance(value, (int, float)):
            raise MCPError(JsonRpcCode.INVALID_PARAMS, f"{path} must be a number.")
        if expected == "boolean" and not isinstance(value, bool):
            raise MCPError(JsonRpcCode.INVALID_PARAMS, f"{path} must be a boolean.")
        if "enum" in schema and value not in schema["enum"]:
            raise MCPError(JsonRpcCode.INVALID_PARAMS, f"{path} must be one of {schema['enum']}.")
        if isinstance(value, str):
            if "minLength" in schema and len(value) < schema["minLength"]:
                raise MCPError(JsonRpcCode.INVALID_PARAMS, f"{path} is too short.")
            if "maxLength" in schema and len(value) > schema["maxLength"]:
                raise MCPError(JsonRpcCode.INVALID_PARAMS, f"{path} is too long.")


class AuditLogger:
    """Append-only JSONL audit log."""

    def __init__(self, path: Path = AUDIT_LOG) -> None:
        ensure_dirs()
        self.path = path

    def write(self, event: str, context: CallerContext, detail: JsonObject) -> None:
        record = {
            "timestamp": utc_now(),
            "event": event,
            "request_id": context.request_id,
            "subject": context.subject,
            "role": context.role.value,
            "detail": detail,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


class AuthorizationPolicy:
    """Scope-based authorization for tools, resources, prompts, and approvals."""

    def require_scopes(self, context: CallerContext, scopes: set[str]) -> None:
        missing = sorted(scope for scope in scopes if not has_scope(context.role, scope))
        if missing:
            raise MCPError(JsonRpcCode.PERMISSION_DENIED, "Missing required scope(s).", {"missingScopes": missing})


class IndustrialDataStore:
    """Small deterministic data layer replacing real MES/CAD/model databases."""

    def __init__(self) -> None:
        ensure_dirs()
        self.defects = [
            {"defect_id": "D-1001", "panel_id": "P-1001", "batch": "B-07", "type": "scratch", "severity": 3, "station": "AOI-1"},
            {"defect_id": "D-1002", "panel_id": "P-1002", "batch": "B-07", "type": "particle", "severity": 2, "station": "AOI-1"},
            {"defect_id": "D-1003", "panel_id": "P-1003", "batch": "B-08", "type": "offset", "severity": 5, "station": "AOI-2"},
            {"defect_id": "D-1004", "panel_id": "P-1001", "batch": "B-07", "type": "scratch", "severity": 4, "station": "AOI-2"},
        ]
        self.panel_summaries = {
            "P-1001": {"panel_id": "P-1001", "batch": "B-07", "defect_count": 2, "max_severity": 4, "yield_risk": "medium"},
            "P-1002": {"panel_id": "P-1002", "batch": "B-07", "defect_count": 1, "max_severity": 2, "yield_risk": "low"},
            "P-1003": {"panel_id": "P-1003", "batch": "B-08", "defect_count": 1, "max_severity": 5, "yield_risk": "high"},
        }
        self.cad_alignment = {
            "P-1001": {"panel_id": "P-1001", "dx_um": 12.4, "dy_um": -8.1, "theta_mdeg": 1.7, "within_tolerance": True},
            "P-1002": {"panel_id": "P-1002", "dx_um": 5.2, "dy_um": 3.3, "theta_mdeg": 0.5, "within_tolerance": True},
            "P-1003": {"panel_id": "P-1003", "dx_um": 41.9, "dy_um": -22.0, "theta_mdeg": 7.9, "within_tolerance": False},
        }
        self.model_metrics = {
            "defect-cnn-v4": {"model_name": "defect-cnn-v4", "precision": 0.942, "recall": 0.918, "f1": 0.930, "drift_score": 0.17},
            "alignment-vit-v2": {"model_name": "alignment-vit-v2", "precision": 0.955, "recall": 0.901, "f1": 0.927, "drift_score": 0.08},
        }
        self.retrain_requests = self._load_retrain_requests()

    def _load_retrain_requests(self) -> list[JsonObject]:
        if RETRAIN_REQUESTS_PATH.exists():
            return json.loads(RETRAIN_REQUESTS_PATH.read_text(encoding="utf-8"))
        return []

    def save_retrain_requests(self) -> None:
        RETRAIN_REQUESTS_PATH.write_text(json.dumps(self.retrain_requests, indent=2, ensure_ascii=False), encoding="utf-8")


class ApprovalWorkflow:
    """Two-phase approval store for write operations.

    Phase 1: create_retrain_request / prepare_retrain_request records the exact intended write.
    Phase 2: a maintainer/admin approves the prepared request.
    Phase 3: commit_create_retrain_request executes only the approved request.
    """

    def __init__(self, path: Path = APPROVALS_PATH) -> None:
        ensure_dirs()
        self.path = path
        self.data: JsonObject = {"prepared": {}, "approved": {}, "committed": {}}
        self.load()

    def load(self) -> None:
        if self.path.exists():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))

    def save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")

    def prepare(self, tool_name: str, arguments: JsonObject, context: CallerContext) -> str:
        approval_id = f"appr-{uuid.uuid4().hex[:10]}"
        self.data["prepared"][approval_id] = {
            "tool": tool_name,
            "arguments": arguments,
            "prepared_by": context.subject,
            "prepared_role": context.role.value,
            "prepared_at": utc_now(),
        }
        self.save()
        return approval_id

    def approve(self, approval_id: str, context: CallerContext, auth: AuthorizationPolicy) -> JsonObject:
        auth.require_scopes(context, {"approval:grant"})
        prepared = self.data["prepared"].pop(approval_id, None)
        if not prepared:
            raise MCPError(JsonRpcCode.NOT_FOUND, f"No prepared write found for {approval_id}.")
        prepared["approved_by"] = context.subject
        prepared["approved_at"] = utc_now()
        self.data["approved"][approval_id] = prepared
        self.save()
        return prepared

    def consume_approval(self, approval_id: str, tool_name: str, arguments: JsonObject) -> JsonObject:
        approved = self.data["approved"].get(approval_id)
        if not approved:
            raise MCPError(JsonRpcCode.APPROVAL_REQUIRED, "Write approval is required.", {"approvalId": approval_id})
        if approved["tool"] != tool_name or approved["arguments"] != arguments:
            raise MCPError(JsonRpcCode.PERMISSION_DENIED, "Approval does not match this write request.")
        self.data["committed"][approval_id] = self.data["approved"].pop(approval_id)
        self.data["committed"][approval_id]["committed_at"] = utc_now()
        self.save()
        return self.data["committed"][approval_id]


def object_schema(properties: JsonObject, required: list[str] | None = None) -> JsonObject:
    return {"type": "object", "properties": properties, "required": required or [], "additionalProperties": False}


def array_output(item_properties: JsonObject) -> JsonObject:
    return object_schema({"rows": {"type": "array", "items": object_schema(item_properties)}, "row_count": {"type": "integer"}}, ["rows", "row_count"])


class ToolRegistry:
    """Builds and owns all tool definitions."""

    def __init__(self, server: IndustrialInspectionMCPServerProtocol) -> None:
        self.server = server
        self.tools = self._build()

    def _build(self) -> dict[str, ToolDefinition]:
        defect_row = {
            "defect_id": {"type": "string"},
            "panel_id": {"type": "string"},
            "batch": {"type": "string"},
            "type": {"type": "string"},
            "severity": {"type": "integer"},
            "station": {"type": "string"},
        }
        any_object = {"type": "object", "additionalProperties": True}
        retrain_input = object_schema(
            {
                "model_name": {"type": "string", "minLength": 1, "maxLength": 80},
                "reason": {"type": "string", "minLength": 8, "maxLength": 500},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]},
            },
            ["model_name", "reason"],
        )
        return {
            "query_defects": ToolDefinition(
                "query_defects",
                "Read defects by panel, batch, type, or minimum severity.",
                object_schema(
                    {
                        "panel_id": {"type": "string", "minLength": 1, "maxLength": 40},
                        "batch": {"type": "string", "minLength": 1, "maxLength": 40},
                        "defect_type": {"type": "string", "minLength": 1, "maxLength": 40},
                        "min_severity": {"type": "integer"},
                    }
                ),
                array_output(defect_row),
                self.server.query_defects,
                ToolMode.READ,
                {"defects:read"},
            ),
            "get_panel_summary": ToolDefinition(
                "get_panel_summary",
                "Return quality summary for one inspected panel.",
                object_schema({"panel_id": {"type": "string", "minLength": 1, "maxLength": 40}}, ["panel_id"]),
                any_object,
                self.server.get_panel_summary,
                ToolMode.READ,
                {"panels:read"},
            ),
            "get_cad_alignment": ToolDefinition(
                "get_cad_alignment",
                "Return CAD-to-image alignment offsets for one panel.",
                object_schema({"panel_id": {"type": "string", "minLength": 1, "maxLength": 40}}, ["panel_id"]),
                any_object,
                self.server.get_cad_alignment,
                ToolMode.READ,
                {"cad:read"},
            ),
            "run_rca": ToolDefinition(
                "run_rca",
                "Run deterministic root-cause analysis over defect, panel, CAD, and model evidence.",
                object_schema({"panel_id": {"type": "string", "minLength": 1, "maxLength": 40}, "include_model_metrics": {"type": "boolean"}}, ["panel_id"]),
                any_object,
                self.server.run_rca,
                ToolMode.READ,
                {"rca:run", "defects:read", "panels:read"},
            ),
            "get_model_metrics": ToolDefinition(
                "get_model_metrics",
                "Return quality metrics for a deployed inspection model.",
                object_schema({"model_name": {"type": "string", "minLength": 1, "maxLength": 80}}, ["model_name"]),
                any_object,
                self.server.get_model_metrics,
                ToolMode.READ,
                {"models:read"},
            ),
            "prepare_retrain_request": ToolDefinition(
                "prepare_retrain_request",
                "Prepare a retraining request and return an approval ID. This does not mutate production state.",
                retrain_input,
                object_schema({"approval_id": {"type": "string"}, "status": {"type": "string"}, "prepared_request": any_object}, ["approval_id", "status", "prepared_request"]),
                self.server.prepare_retrain_request,
                ToolMode.WRITE,
                {"retrain:prepare"},
                write_phase=WritePhase.PREPARE,
                requires_approval=True,
            ),
            "create_retrain_request": ToolDefinition(
                "create_retrain_request",
                "Create a pending retraining request and return an approval ID. This prepares a write but does not commit it.",
                retrain_input,
                object_schema({"approval_id": {"type": "string"}, "status": {"type": "string"}, "prepared_request": any_object}, ["approval_id", "status", "prepared_request"]),
                self.server.create_retrain_request,
                ToolMode.WRITE,
                {"retrain:prepare"},
                write_phase=WritePhase.PREPARE,
                requires_approval=True,
            ),
            "commit_retrain_request": ToolDefinition(
                "commit_retrain_request",
                "Commit an approved retraining request. Requires maintainer/admin scope and matching approval.",
                object_schema({"approval_id": {"type": "string", "minLength": 1, "maxLength": 80}}, ["approval_id"]),
                any_object,
                self.server.commit_retrain_request,
                ToolMode.WRITE,
                {"retrain:commit"},
                write_phase=WritePhase.COMMIT,
                requires_approval=True,
            ),
        }


class IndustrialInspectionMCPServerProtocol:
    """Typing helper for ToolRegistry handlers."""

    def query_defects(self, args: JsonObject) -> JsonObject: ...

    def get_panel_summary(self, args: JsonObject) -> JsonObject: ...

    def get_cad_alignment(self, args: JsonObject) -> JsonObject: ...

    def run_rca(self, args: JsonObject) -> JsonObject: ...

    def get_model_metrics(self, args: JsonObject) -> JsonObject: ...

    def prepare_retrain_request(self, args: JsonObject) -> JsonObject: ...

    def create_retrain_request(self, args: JsonObject) -> JsonObject: ...

    def commit_retrain_request(self, args: JsonObject) -> JsonObject: ...


class IndustrialInspectionMCPServer:
    """MCP-style server exposing industrial inspection capabilities."""

    def __init__(self) -> None:
        ensure_dirs()
        self.audit = AuditLogger()
        self.auth = AuthorizationPolicy()
        self.store = IndustrialDataStore()
        self.approvals = ApprovalWorkflow()
        self.registry = ToolRegistry(self)
        self.resources = self._build_resources()
        self.prompts = self._build_prompts()

    def _build_resources(self) -> dict[str, JsonObject]:
        return {
            "inspection://schema/defects": {
                "uri": "inspection://schema/defects",
                "name": "Defect table schema",
                "mimeType": "application/json",
                "text": json.dumps({"columns": list(self.store.defects[0].keys())}, indent=2),
            },
            "inspection://models/current": {
                "uri": "inspection://models/current",
                "name": "Current model metrics",
                "mimeType": "application/json",
                "text": json.dumps(self.store.model_metrics, indent=2),
            },
        }

    def _build_prompts(self) -> dict[str, JsonObject]:
        return {
            "rca_report": {
                "name": "rca_report",
                "description": "Prompt template for writing RCA from tool evidence.",
                "arguments": [{"name": "panel_id", "required": True}, {"name": "evidence", "required": True}],
                "template": "Write an RCA report for panel {panel_id} using only this evidence: {evidence}",
            }
        }

    def initialize(self, client_info: JsonObject) -> JsonObject:
        return {
            "protocolVersion": PROTOCOL_VERSION,
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            "clientInfo": client_info,
            "capabilities": {
                "tools": {"listChanged": False},
                "resources": {"subscribe": False, "listChanged": False},
                "prompts": {"listChanged": False},
                "logging": {},
            },
        }

    def discover(self) -> JsonObject:
        return {
            "name": SERVER_NAME,
            "version": SERVER_VERSION,
            "protocolVersion": PROTOCOL_VERSION,
            "toolSchemaVersion": TOOL_SCHEMA_VERSION,
            "transports": ["stdio-jsonrpc", "local-cli"],
            "security": {
                "authentication": "demo CallerContext; replace with OAuth/JWT/mTLS in production",
                "authorization": "role scopes",
                "writeApproval": "prepare -> approval:grant -> commit",
                "boundary": "no arbitrary SQL, no arbitrary filesystem, no secret injection into prompts",
            },
        }

    def list_tools(self, context: CallerContext) -> JsonObject:
        visible = []
        for tool in self.registry.tools.values():
            try:
                self.auth.require_scopes(context, tool.required_scopes)
                visible.append(tool.public_descriptor())
            except MCPError:
                continue
        return {"tools": visible}

    def call_tool(self, name: str, arguments: JsonObject, context: CallerContext) -> JsonObject:
        tool = self.registry.tools.get(name)
        if not tool:
            raise MCPError(JsonRpcCode.METHOD_NOT_FOUND, f"Unknown tool: {name}")

        self.audit.write("request_received", context, {"tool": name})
        SchemaValidator.validate(tool.input_schema, arguments)
        self.audit.write("schema_validated", context, {"tool": name, "direction": "input"})

        self.auth.require_scopes(context, tool.required_scopes)
        self.audit.write("authorization_checked", context, {"tool": name, "scopes": sorted(tool.required_scopes)})

        try:
            self.audit.write("tool_started", context, {"tool": name, "mode": tool.mode.value, "phase": tool.write_phase.value})
            result = tool.handler(arguments)
            SchemaValidator.validate(tool.output_schema, result)
            self.audit.write("schema_validated", context, {"tool": name, "direction": "output"})
            self.audit.write("tool_completed", context, {"tool": name, "ok": True})
            return {"content": [{"type": "json", "json": result}], "isError": False}
        except MCPError:
            self.audit.write("tool_failed", context, {"tool": name, "error": "mcp_error"})
            raise
        except Exception as exc:
            self.audit.write("tool_failed", context, {"tool": name, "error": str(exc)})
            raise MCPError(JsonRpcCode.TOOL_EXECUTION_FAILED, str(exc)) from exc

    def list_resources(self, context: CallerContext) -> JsonObject:
        self.auth.require_scopes(context, {"resources:read"})
        return {"resources": [{key: value for key, value in item.items() if key != "text"} for item in self.resources.values()]}

    def read_resource(self, uri: str, context: CallerContext) -> JsonObject:
        self.auth.require_scopes(context, {"resources:read"})
        item = self.resources.get(uri)
        if not item:
            raise MCPError(JsonRpcCode.NOT_FOUND, f"Unknown resource URI: {uri}")
        return {"contents": [item]}

    def list_prompts(self, context: CallerContext) -> JsonObject:
        self.auth.require_scopes(context, {"prompts:read"})
        return {"prompts": [{key: value for key, value in item.items() if key != "template"} for item in self.prompts.values()]}

    def get_prompt(self, name: str, arguments: JsonObject, context: CallerContext) -> JsonObject:
        self.auth.require_scopes(context, {"prompts:read"})
        prompt = self.prompts.get(name)
        if not prompt:
            raise MCPError(JsonRpcCode.NOT_FOUND, f"Unknown prompt: {name}")
        try:
            text = prompt["template"].format(**arguments)
        except KeyError as exc:
            raise MCPError(JsonRpcCode.INVALID_PARAMS, f"Missing prompt argument: {exc.args[0]}") from exc
        return {"description": prompt["description"], "messages": [{"role": "user", "content": {"type": "text", "text": text}}]}

    def approve_write(self, approval_id: str, context: CallerContext) -> JsonObject:
        approved = self.approvals.approve(approval_id, context, self.auth)
        self.audit.write("approval_granted", context, {"approval_id": approval_id, "tool": approved["tool"]})
        return {"approval_id": approval_id, "approved": True, "approved_request": approved}

    def handle_jsonrpc(self, request: JsonObject, context: CallerContext) -> JsonObject:
        request_id = request.get("id")
        try:
            if request.get("jsonrpc") != "2.0":
                raise MCPError(JsonRpcCode.INVALID_REQUEST, "jsonrpc must be '2.0'.")
            method = request.get("method")
            params = request.get("params", {})
            if method == "initialize":
                result = self.initialize(params.get("clientInfo", {}))
            elif method == "server/discover":
                result = self.discover()
            elif method == "tools/list":
                result = self.list_tools(context)
            elif method == "tools/call":
                result = self.call_tool(params["name"], params.get("arguments", {}), context)
            elif method == "resources/list":
                result = self.list_resources(context)
            elif method == "resources/read":
                result = self.read_resource(params["uri"], context)
            elif method == "prompts/list":
                result = self.list_prompts(context)
            elif method == "prompts/get":
                result = self.get_prompt(params["name"], params.get("arguments", {}), context)
            elif method == "approvals/approve":
                result = self.approve_write(params["approval_id"], context)
            else:
                raise MCPError(JsonRpcCode.METHOD_NOT_FOUND, f"Unknown method: {method}")
            return {"jsonrpc": "2.0", "id": request_id, "result": result}
        except MCPError as exc:
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": exc.code, "message": exc.message, "data": exc.data}}
        except Exception as exc:
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": JsonRpcCode.INTERNAL_ERROR, "message": str(exc)}}

    def query_defects(self, args: JsonObject) -> JsonObject:
        rows = self.store.defects
        if "panel_id" in args:
            rows = [row for row in rows if row["panel_id"] == args["panel_id"]]
        if "batch" in args:
            rows = [row for row in rows if row["batch"] == args["batch"]]
        if "defect_type" in args:
            rows = [row for row in rows if row["type"] == args["defect_type"]]
        if "min_severity" in args:
            rows = [row for row in rows if row["severity"] >= args["min_severity"]]
        return {"rows": rows, "row_count": len(rows)}

    def get_panel_summary(self, args: JsonObject) -> JsonObject:
        panel_id = args["panel_id"]
        if panel_id not in self.store.panel_summaries:
            raise MCPError(JsonRpcCode.NOT_FOUND, f"No summary found for panel {panel_id}.")
        return self.store.panel_summaries[panel_id]

    def get_cad_alignment(self, args: JsonObject) -> JsonObject:
        panel_id = args["panel_id"]
        if panel_id not in self.store.cad_alignment:
            raise MCPError(JsonRpcCode.NOT_FOUND, f"No CAD alignment found for panel {panel_id}.")
        return self.store.cad_alignment[panel_id]

    def run_rca(self, args: JsonObject) -> JsonObject:
        panel_id = args["panel_id"]
        defects = self.query_defects({"panel_id": panel_id})["rows"]
        summary = self.store.panel_summaries.get(panel_id, {})
        alignment = self.store.cad_alignment.get(panel_id, {})
        causes = []
        if alignment and not alignment["within_tolerance"]:
            causes.append({"cause": "CAD alignment drift", "confidence": 0.86, "evidence": alignment})
        if any(row["type"] == "scratch" for row in defects):
            causes.append({"cause": "Handling or fixture contact", "confidence": 0.64, "evidence": defects})
        if summary.get("yield_risk") == "high":
            causes.append({"cause": "Panel-level process excursion", "confidence": 0.72, "evidence": summary})
        if args.get("include_model_metrics", False):
            causes.append({"cause": "Model drift check needed", "confidence": 0.44, "evidence": self.store.model_metrics["defect-cnn-v4"]})
        return {"panel_id": panel_id, "ranked_causes": causes, "missing_evidence": [] if causes else ["No matching defects found."]}

    def get_model_metrics(self, args: JsonObject) -> JsonObject:
        model_name = args["model_name"]
        if model_name not in self.store.model_metrics:
            raise MCPError(JsonRpcCode.NOT_FOUND, f"No metrics found for model {model_name}.")
        return self.store.model_metrics[model_name]

    def prepare_retrain_request(self, args: JsonObject) -> JsonObject:
        approval_id = self.approvals.prepare("commit_retrain_request", args, CallerContext())
        return {"approval_id": approval_id, "status": "prepared", "prepared_request": args}

    def create_retrain_request(self, args: JsonObject) -> JsonObject:
        """Prepare a retraining request under the required project tool name.

        The name says "create", but the safety boundary is still two-phase:
        this creates a pending approval record only. The actual state mutation
        happens later through commit_retrain_request after approval.
        """

        return self.prepare_retrain_request(args)

    def commit_retrain_request(self, args: JsonObject) -> JsonObject:
        approval_id = args["approval_id"]
        approved = self.approvals.data["approved"].get(approval_id)
        if not approved:
            raise MCPError(JsonRpcCode.APPROVAL_REQUIRED, "Approved retrain request is required.", {"approvalId": approval_id})
        intended = approved["arguments"]
        self.approvals.consume_approval(approval_id, "commit_retrain_request", intended)
        request_record = {
            "request_id": f"rtrain-{uuid.uuid4().hex[:10]}",
            "model_name": intended["model_name"],
            "reason": intended["reason"],
            "priority": intended.get("priority", "medium"),
            "status": "created",
            "approval_id": approval_id,
            "created_at": utc_now(),
        }
        self.store.retrain_requests.append(request_record)
        self.store.save_retrain_requests()
        return request_record


class MCPClient:
    """Client facade that speaks JSON-RPC to the server."""

    def __init__(self, server: IndustrialInspectionMCPServer, context: CallerContext) -> None:
        self.server = server
        self.context = context

    def request(self, method: str, params: JsonObject | None = None) -> JsonObject:
        message = {"jsonrpc": "2.0", "id": f"msg-{uuid.uuid4().hex[:8]}", "method": method, "params": params or {}}
        response = self.server.handle_jsonrpc(message, self.context)
        if "error" in response:
            error = response["error"]
            raise MCPError(error["code"], error["message"], error.get("data", {}))
        return response["result"]

    def call_tool(self, name: str, arguments: JsonObject) -> JsonObject:
        return self.request("tools/call", {"name": name, "arguments": arguments})


class MCPHost:
    """Tiny host that discovers a server and chooses tools for a user goal."""

    def __init__(self, client: MCPClient) -> None:
        self.client = client

    def inspect_panel(self, panel_id: str) -> JsonObject:
        init = self.client.request("initialize", {"clientInfo": {"name": "industrial-demo-host", "version": "0.1"}})
        tools = self.client.request("tools/list")["tools"]
        summary = self.client.call_tool("get_panel_summary", {"panel_id": panel_id})
        rca = self.client.call_tool("run_rca", {"panel_id": panel_id, "include_model_metrics": True})
        return {"initialize": init, "available_tools": [tool["name"] for tool in tools], "summary": summary, "rca": rca}


class StdioJsonRpcTransport:
    """Line-delimited JSON-RPC transport for local MCP-style testing."""

    def __init__(self, server: IndustrialInspectionMCPServer, context: CallerContext) -> None:
        self.server = server
        self.context = context

    def serve(self) -> None:
        for line in sys.stdin:
            if not line.strip():
                continue
            try:
                request = json.loads(line)
                response = self.server.handle_jsonrpc(request, self.context)
            except json.JSONDecodeError as exc:
                response = {"jsonrpc": "2.0", "id": None, "error": {"code": JsonRpcCode.PARSE_ERROR, "message": str(exc)}}
            print(json.dumps(response, ensure_ascii=False), flush=True)


def role_from_text(value: str) -> Role:
    try:
        return Role(value)
    except ValueError as exc:
        raise SystemExit(f"Unknown role {value}. Use viewer, engineer, maintainer, or admin.") from exc


def print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def reset_demo_data() -> None:
    ensure_dirs()
    for path in [AUDIT_LOG, APPROVALS_PATH, RETRAIN_REQUESTS_PATH]:
        if path.exists():
            try:
                path.unlink()
            except PermissionError:
                # On Windows, a parallel demo command may briefly hold the file.
                # Truncating keeps self-test deterministic once the handle is released.
                if path == AUDIT_LOG:
                    fallback = ""
                elif path == RETRAIN_REQUESTS_PATH:
                    fallback = "[]"
                else:
                    fallback = json.dumps({"prepared": {}, "approved": {}, "committed": {}})
                path.write_text(fallback, encoding="utf-8")


def self_test() -> None:
    """Verify discovery, schemas, scopes, approval workflow, host/client, and audit."""

    reset_demo_data()
    server = IndustrialInspectionMCPServer()
    viewer = MCPClient(server, CallerContext(role=Role.VIEWER, subject="viewer@example.com"))
    engineer = MCPClient(server, CallerContext(role=Role.ENGINEER, subject="engineer@example.com"))
    maintainer = MCPClient(server, CallerContext(role=Role.MAINTAINER, subject="maintainer@example.com"))

    assert viewer.request("initialize", {"clientInfo": {"name": "self-test", "version": "0.1"}})["protocolVersion"] == PROTOCOL_VERSION
    assert viewer.request("server/discover")["toolSchemaVersion"] == TOOL_SCHEMA_VERSION
    assert "query_defects" in [tool["name"] for tool in viewer.request("tools/list")["tools"]]
    assert "run_rca" not in [tool["name"] for tool in viewer.request("tools/list")["tools"]]

    defects = viewer.call_tool("query_defects", {"batch": "B-07"})
    assert defects["content"][0]["json"]["row_count"] == 3

    try:
        viewer.call_tool("get_cad_alignment", {"panel_id": "P-1001"})
        raise AssertionError("viewer should not access CAD alignment")
    except MCPError as exc:
        assert exc.code == JsonRpcCode.PERMISSION_DENIED

    rca = engineer.call_tool("run_rca", {"panel_id": "P-1003", "include_model_metrics": True})
    assert rca["content"][0]["json"]["ranked_causes"]

    engineer_tools = [tool["name"] for tool in engineer.request("tools/list")["tools"]]
    assert "create_retrain_request" in engineer_tools
    assert "commit_retrain_request" not in engineer_tools

    prepared = engineer.call_tool("create_retrain_request", {"model_name": "defect-cnn-v4", "reason": "drift score exceeded threshold", "priority": "high"})
    approval_id = prepared["content"][0]["json"]["approval_id"]

    try:
        engineer.call_tool("commit_retrain_request", {"approval_id": approval_id})
        raise AssertionError("engineer should not commit retrain requests")
    except MCPError as exc:
        assert exc.code == JsonRpcCode.PERMISSION_DENIED

    maintainer.request("approvals/approve", {"approval_id": approval_id})
    committed = maintainer.call_tool("commit_retrain_request", {"approval_id": approval_id})
    assert committed["content"][0]["json"]["status"] == "created"

    host_result = MCPHost(engineer).inspect_panel("P-1003")
    assert "run_rca" in host_result["available_tools"]
    assert AUDIT_LOG.exists()
    assert len(AUDIT_LOG.read_text(encoding="utf-8").splitlines()) >= 8
    print("Self-tests passed.")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Industrial inspection MCP-style server.")
    parser.add_argument("--role", default="viewer", help="viewer, engineer, maintainer, or admin")
    parser.add_argument("--subject", default="local-demo-user")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--discover", action="store_true")
    parser.add_argument("--initialize", action="store_true")
    parser.add_argument("--list-tools", action="store_true")
    parser.add_argument("--list-resources", action="store_true")
    parser.add_argument("--read-resource")
    parser.add_argument("--list-prompts", action="store_true")
    parser.add_argument("--get-prompt")
    parser.add_argument("--call")
    parser.add_argument("--arguments", default="{}")
    parser.add_argument("--approve")
    parser.add_argument("--host-inspect-panel")
    parser.add_argument("--stdio", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.self_test:
        self_test()
        return 0

    server = IndustrialInspectionMCPServer()
    context = CallerContext(role=role_from_text(args.role), subject=args.subject)
    client = MCPClient(server, context)

    if args.stdio:
        StdioJsonRpcTransport(server, context).serve()
        return 0

    if args.initialize:
        print_json(client.request("initialize", {"clientInfo": {"name": "local-cli-host", "version": "0.1"}}))
    elif args.discover:
        print_json(client.request("server/discover"))
    elif args.list_tools:
        print_json(client.request("tools/list"))
    elif args.list_resources:
        print_json(client.request("resources/list"))
    elif args.read_resource:
        print_json(client.request("resources/read", {"uri": args.read_resource}))
    elif args.list_prompts:
        print_json(client.request("prompts/list"))
    elif args.get_prompt:
        print_json(client.request("prompts/get", {"name": args.get_prompt, "arguments": json.loads(args.arguments)}))
    elif args.call:
        print_json(client.call_tool(args.call, json.loads(args.arguments)))
    elif args.approve:
        print_json(client.request("approvals/approve", {"approval_id": args.approve}))
    elif args.host_inspect_panel:
        print_json(MCPHost(client).inspect_panel(args.host_inspect_panel))
    else:
        print("Use --self-test, --discover, --initialize, --list-tools, --call, --approve, --host-inspect-panel, or --stdio.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
