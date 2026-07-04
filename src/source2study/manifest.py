from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from source2study import __version__
from source2study.adapters.utils import stable_id, utc_now


def manifest_path(workspace: Path) -> Path:
    return workspace / "manifest.json"


def new_manifest(workspace: Path) -> dict[str, Any]:
    now = utc_now()
    return {
        "workspace_id": stable_id("ws", str(workspace.resolve())),
        "source2study_version": __version__,
        "created_at": now,
        "updated_at": now,
        "sources": [],
        "outputs": [],
        "validations": [],
        "jobs": [],
        "cache": {"hits": 0, "misses": 0},
    }


def load_manifest(workspace: Path) -> dict[str, Any]:
    path = manifest_path(workspace)
    if not path.exists():
        return new_manifest(workspace)
    return json.loads(path.read_text(encoding="utf-8"))


def write_manifest(workspace: Path, manifest: dict[str, Any]) -> None:
    manifest["updated_at"] = utc_now()
    manifest["source2study_version"] = __version__
    path = manifest_path(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def record_job(manifest: dict[str, Any], command: str, status: str, params: dict[str, Any] | None = None) -> None:
    manifest.setdefault("jobs", []).append(
        {
            "command": command,
            "status": status,
            "params": params or {},
            "time": utc_now(),
        }
    )


def record_source(
    manifest: dict[str, Any],
    source_id: str | None,
    source_type: str,
    value: str,
    status: str,
    adapter: str,
    cache_key: str | None = None,
    error: str | None = None,
) -> None:
    entry = {
        "source_id": source_id,
        "type": source_type,
        "value": value,
        "status": status,
        "adapter": adapter,
        "cache_key": cache_key,
        "time": utc_now(),
    }
    if error:
        entry["error"] = error
    manifest.setdefault("sources", []).append(entry)


def record_output(
    manifest: dict[str, Any],
    mode: str,
    output_format: str,
    path: Path,
    status: str,
    report_path: Path | None = None,
) -> None:
    entry = {
        "mode": mode,
        "format": output_format,
        "path": str(path),
        "status": status,
        "time": utc_now(),
    }
    if report_path:
        entry["citation_report_path"] = str(report_path)
    manifest.setdefault("outputs", []).append(entry)


def record_validation(manifest: dict[str, Any], status: str, report_path: Path | None, summary: dict[str, Any]) -> None:
    manifest.setdefault("validations", []).append(
        {
            "status": status,
            "report_path": str(report_path) if report_path else None,
            "summary": summary,
            "time": utc_now(),
        }
    )


def record_cache(manifest: dict[str, Any], hit: bool) -> None:
    cache = manifest.setdefault("cache", {"hits": 0, "misses": 0})
    cache["hits" if hit else "misses"] = int(cache.get("hits" if hit else "misses", 0)) + 1
