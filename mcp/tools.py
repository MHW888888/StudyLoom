from __future__ import annotations

"""Restricted Source2Study MCP tool wrappers.

The wrappers intentionally call the existing CLI pipeline instead of exposing
raw filesystem, network, shell, cookie, or browser-profile access to agents.
"""

import contextlib
import io
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evals.run_eval import run_suite  # noqa: E402
from mcp.schemas import list_tools  # noqa: E402
from source2study.cli import main as source2study_main  # noqa: E402
from source2study.config import SourcePolicy  # noqa: E402
from source2study.generation.modes import resolve_mode  # noqa: E402
from source2study.safety.policy import PolicyEngine  # noqa: E402
from source2study.safety.redaction import safe_display_path, sanitize_for_response  # noqa: E402
from source2study.workspace import citation_report_path, learning_quality_report_path, pack_json_path  # noqa: E402


DEFAULT_ALLOWED_WORKSPACES = ("./workspace", "./examples", "./tmp/source2study")
BLOCKED_SOURCE_MESSAGE = "MCP tools only process local allowlisted sources; use exported files or browser-capture JSON."


@dataclass(frozen=True)
class McpToolConfig:
    allowed_workspaces: tuple[Path, ...]
    network_enabled: bool = False
    allow_degraded: bool = False
    max_source_size_mb: int = 50
    max_output_chars: int = 20000
    root: Path = ROOT

    @classmethod
    def load(cls, config_path: Path | None = None) -> "McpToolConfig":
        root = ROOT
        path = config_path or root / ".source2study" / "config.json"
        data: dict[str, Any] = {}
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
        allowed = data.get("allowed_workspaces", list(DEFAULT_ALLOWED_WORKSPACES))
        return cls(
            allowed_workspaces=tuple(_resolve_config_path(item, root) for item in allowed),
            network_enabled=bool(data.get("network_enabled", False)),
            allow_degraded=bool(data.get("allow_degraded", False)),
            max_source_size_mb=int(data.get("max_source_size_mb", 50)),
            max_output_chars=int(data.get("max_output_chars", 20000)),
            root=root,
        )


def source2study_policy_check(source: str, *, config: McpToolConfig | None = None) -> dict[str, Any]:
    cfg = config or McpToolConfig.load()
    try:
        if _looks_like_path(source):
            source_path = _resolve_user_path(source, cfg.root)
            if source_path.exists():
                _ensure_inside_allowlist(source_path, cfg)
        decision = PolicyEngine().check_source(source, SourcePolicy(allow_network=cfg.network_enabled))
        status = "pass" if decision.allowed else "blocked"
        return _response(status, cfg, policy=decision.to_dict())
    except Exception as exc:  # noqa: BLE001 - MCP tools return structured errors.
        return _error_response(exc, cfg)


def source2study_inspect_local(
    workspace: str,
    source: str,
    source_type: str | None = None,
    *,
    config: McpToolConfig | None = None,
) -> dict[str, Any]:
    cfg = config or McpToolConfig.load()
    try:
        workspace_path = _ensure_workspace_allowed(workspace, cfg)
        source_path = _ensure_local_source_allowed(source, cfg)
        args = ["inspect", str(source_path), "--workspace", str(workspace_path)]
        if source_type:
            args.extend(["--source-type", source_type])
        result = _run_cli(args)
        if result["code"] != 0:
            return _error_response(RuntimeError(result["stderr"] or result["stdout"] or "inspect failed"), cfg, workspace_path)
        report = _read_json(workspace_path / "intake_report.json")
        return _response(
            "pass" if report.get("status") == "pass" else "degraded",
            cfg,
            workspace=workspace_path,
            intake_summary_path=workspace_path / "intake_report.json",
            intake_status=report.get("status"),
            source_count=report.get("source_count", 0),
            warnings=report.get("warnings", []),
        )
    except Exception as exc:  # noqa: BLE001
        return _error_response(exc, cfg)


def source2study_ingest_local(
    workspace: str,
    sources: list[str],
    source_type: str | None = None,
    *,
    config: McpToolConfig | None = None,
) -> dict[str, Any]:
    cfg = config or McpToolConfig.load()
    try:
        workspace_path = _ensure_workspace_allowed(workspace, cfg)
        if not sources:
            raise ValueError("At least one source is required.")
        source_paths = [_ensure_local_source_allowed(source, cfg) for source in sources]
        args = ["ingest", "--workspace", str(workspace_path)]
        for source_path in source_paths:
            args.extend(["--source", str(source_path)])
        if source_type:
            args.extend(["--source-type", source_type])
        result = _run_cli(args)
        if result["code"] != 0:
            return _error_response(RuntimeError(result["stderr"] or result["stdout"] or "ingest failed"), cfg, workspace_path)
        payload = _parse_json(result["stdout"])
        return _response(
            "pass",
            cfg,
            workspace=workspace_path,
            intake_summary_path=workspace_path / "intake_report.json",
            source_ledger_path=workspace_path / "source_ledger.json",
            evidence_ledger_path=workspace_path / "evidence_ledger.json",
            sources=payload.get("sources"),
            evidence=payload.get("evidence"),
            warnings=payload.get("warnings", []),
        )
    except Exception as exc:  # noqa: BLE001
        return _error_response(exc, cfg)


def source2study_build_index(workspace: str, *, config: McpToolConfig | None = None) -> dict[str, Any]:
    cfg = config or McpToolConfig.load()
    try:
        workspace_path = _ensure_workspace_allowed(workspace, cfg)
        args = ["build-index", str(workspace_path)]
        if cfg.allow_degraded:
            args.append("--allow-degraded")
        result = _run_cli(args)
        if result["code"] != 0:
            return _error_response(RuntimeError(result["stderr"] or result["stdout"] or "build-index failed"), cfg, workspace_path)
        payload = _parse_json(result["stdout"])
        return _response(
            "pass",
            cfg,
            workspace=workspace_path,
            index_path=workspace_path / "evidence_index.json",
            sources=payload.get("sources"),
            evidence=payload.get("evidence"),
        )
    except Exception as exc:  # noqa: BLE001
        return _error_response(exc, cfg)


def source2study_generate_pack(
    workspace: str,
    mode: str,
    format: str = "markdown",
    *,
    config: McpToolConfig | None = None,
) -> dict[str, Any]:
    return _generate(workspace, mode, format, None, config=config)


def source2study_generate_personalized_pack(
    workspace: str,
    mode: str,
    profile: dict[str, Any],
    format: str = "markdown",
    *,
    config: McpToolConfig | None = None,
) -> dict[str, Any]:
    return _generate(workspace, mode, format, profile, config=config)


def source2study_validate_pack(
    workspace: str,
    pack_path: str | None = None,
    mode: str | None = None,
    *,
    config: McpToolConfig | None = None,
) -> dict[str, Any]:
    cfg = config or McpToolConfig.load()
    try:
        workspace_path = _ensure_workspace_allowed(workspace, cfg)
        args = ["validate", str(workspace_path)]
        resolved_pack = None
        if pack_path:
            resolved_pack = _ensure_inside_allowlist(_resolve_user_path(pack_path, cfg.root), cfg)
        elif mode:
            resolved_pack = pack_json_path(workspace_path, resolve_mode(mode).value)
        if resolved_pack:
            _ensure_inside(resolved_pack, workspace_path)
            args.extend(["--pack", str(resolved_pack)])
        result = _run_cli(args)
        if result["code"] != 0:
            return _error_response(RuntimeError(result["stderr"] or result["stdout"] or "validate failed"), cfg, workspace_path)
        payload = _parse_json(result["stdout"])
        return _response(
            payload.get("status", "pass"),
            cfg,
            workspace=workspace_path,
            citation_report_path=workspace_path / "outputs" / "citation_report_validate.json",
            summary=payload.get("summary", {}),
            warnings=payload.get("warnings", []),
        )
    except Exception as exc:  # noqa: BLE001
        return _error_response(exc, cfg)


def source2study_run_eval(suite: str, *, config: McpToolConfig | None = None) -> dict[str, Any]:
    cfg = config or McpToolConfig.load()
    try:
        allowed = {"standard_demo", "personalized_demo", "degraded_demo"}
        if suite not in allowed:
            raise ValueError(f"Unsupported eval suite: {suite}")
        report = run_suite(suite)
        report_dir = _resolve_config_path("./tmp/source2study/eval_reports", cfg.root)
        _ensure_inside_allowlist(report_dir, cfg)
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"{suite}_eval_report.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return _response(
            report.get("status", "pass"),
            cfg,
            eval_report_path=report_path,
            suite=suite,
            metrics=report.get("metrics", {}),
            issues=report.get("issues", []),
        )
    except Exception as exc:  # noqa: BLE001
        return _error_response(exc, cfg)


def call_tool(name: str, arguments: dict[str, Any] | None = None, *, config: McpToolConfig | None = None) -> dict[str, Any]:
    args = dict(arguments or {})
    functions: dict[str, Callable[..., dict[str, Any]]] = {
        "source2study_policy_check": source2study_policy_check,
        "source2study_inspect_local": source2study_inspect_local,
        "source2study_ingest_local": source2study_ingest_local,
        "source2study_build_index": source2study_build_index,
        "source2study_generate_pack": source2study_generate_pack,
        "source2study_generate_personalized_pack": source2study_generate_personalized_pack,
        "source2study_validate_pack": source2study_validate_pack,
        "source2study_run_eval": source2study_run_eval,
    }
    if name == "tools/list":
        return {"status": "pass", "tools": list_tools(), "warnings": []}
    if name not in functions:
        return _error_response(ValueError(f"Unknown tool: {name}"), config or McpToolConfig.load())
    return functions[name](**args, config=config)


def _generate(
    workspace: str,
    mode: str,
    format: str,
    profile: dict[str, Any] | None,
    *,
    config: McpToolConfig | None,
) -> dict[str, Any]:
    cfg = config or McpToolConfig.load()
    try:
        workspace_path = _ensure_workspace_allowed(workspace, cfg)
        resolved_mode = resolve_mode(mode).value
        extension = _format_extension(format)
        output_path = workspace_path / "outputs" / f"learning_pack_{resolved_mode}.{extension}"
        args = ["generate", str(workspace_path), "--mode", mode, "--output", str(output_path)]
        profile_path = None
        if profile is not None:
            profile_dir = workspace_path / ".source2study"
            profile_dir.mkdir(parents=True, exist_ok=True)
            profile_path = profile_dir / f"mcp_profile_{resolved_mode}.json"
            profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
            args.extend(["--profile", str(profile_path)])
        if cfg.allow_degraded:
            args.append("--allow-degraded")
        result = _run_cli(args)
        if result["code"] != 0:
            return _error_response(RuntimeError(result["stderr"] or result["stdout"] or "generate failed"), cfg, workspace_path)
        payload = _parse_json(result["stdout"])
        pack_path = pack_json_path(workspace_path, resolved_mode)
        return _response(
            "pass",
            cfg,
            workspace=workspace_path,
            pack_path=pack_path,
            output_path=output_path,
            citation_report_path=citation_report_path(workspace_path, resolved_mode),
            learning_quality_report_path=learning_quality_report_path(workspace_path, resolved_mode),
            intake_summary_path=workspace_path / "intake_report.json",
            profile_path=profile_path,
            warnings=payload.get("warnings", []),
        )
    except Exception as exc:  # noqa: BLE001
        return _error_response(exc, cfg)


def _run_cli(args: list[str]) -> dict[str, Any]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = source2study_main(args)
    return {"code": code, "stdout": stdout.getvalue(), "stderr": stderr.getvalue()}


def _response(status: str, cfg: McpToolConfig, **payload: Any) -> dict[str, Any]:
    warnings = payload.pop("warnings", [])
    response = {"status": status, "warnings": warnings, "error": None, **payload}
    workspace = payload.get("workspace")
    return sanitize_for_response(response, workspace=workspace, root=cfg.root, max_chars=cfg.max_output_chars)


def _error_response(exc: Exception, cfg: McpToolConfig, workspace: Path | None = None) -> dict[str, Any]:
    payload = {
        "status": "fail",
        "warnings": [],
        "error": {
            "type": exc.__class__.__name__,
            "message": str(exc),
        },
    }
    return sanitize_for_response(payload, workspace=workspace, root=cfg.root, max_chars=cfg.max_output_chars)


def _parse_json(text: str) -> dict[str, Any]:
    if not text.strip():
        return {}
    return json.loads(text)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _format_extension(format_value: str | None) -> str:
    normalized = (format_value or "markdown").lower()
    if normalized in {"markdown", "md"}:
        return "md"
    if normalized in {"docx", "pdf"}:
        return normalized
    raise ValueError(f"Unsupported output format: {format_value}")


def _looks_like_path(value: str) -> bool:
    parsed = urlparse(value)
    return not parsed.scheme or parsed.scheme == "file"


def _reject_url_network(value: str, cfg: McpToolConfig) -> None:
    parsed = urlparse(value)
    if parsed.scheme in {"http", "https"} and not cfg.network_enabled:
        raise PermissionError("Network access is disabled for MCP tools.")


def _ensure_workspace_allowed(workspace: str, cfg: McpToolConfig) -> Path:
    path = _resolve_user_path(workspace, cfg.root)
    _ensure_inside_allowlist(path, cfg)
    return path


def _ensure_local_source_allowed(source: str, cfg: McpToolConfig) -> Path:
    _reject_url_network(source, cfg)
    source_path = _resolve_user_path(source, cfg.root)
    if not source_path.exists():
        raise FileNotFoundError(f"Local source does not exist: {source}")
    _ensure_inside_allowlist(source_path, cfg)
    _check_source_size(source_path, cfg)
    decision = PolicyEngine().check_source(str(source_path), SourcePolicy(allow_network=False))
    if not decision.allowed:
        raise PermissionError(decision.reason or BLOCKED_SOURCE_MESSAGE)
    return source_path


def _check_source_size(path: Path, cfg: McpToolConfig) -> None:
    max_bytes = cfg.max_source_size_mb * 1024 * 1024
    if path.is_file() and path.stat().st_size > max_bytes:
        raise PermissionError(f"Source exceeds max_source_size_mb={cfg.max_source_size_mb}.")
    if path.is_dir():
        total = 0
        for item in path.rglob("*"):
            if item.is_file():
                total += item.stat().st_size
                if total > max_bytes:
                    raise PermissionError(f"Source directory exceeds max_source_size_mb={cfg.max_source_size_mb}.")


def _ensure_inside_allowlist(path: Path, cfg: McpToolConfig) -> Path:
    resolved = path.resolve()
    for allowed in cfg.allowed_workspaces:
        if _is_inside(resolved, allowed):
            return resolved
    allowed_labels = [safe_display_path(item, root=cfg.root) for item in cfg.allowed_workspaces]
    raise PermissionError(f"Path is outside MCP workspace allowlist. Allowed roots: {allowed_labels}")


def _ensure_inside(path: Path, root: Path) -> None:
    if not _is_inside(path.resolve(), root.resolve()):
        raise PermissionError("Path must stay inside the workspace.")


def _is_inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _resolve_user_path(value: str, root: Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def _resolve_config_path(value: str, root: Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()
