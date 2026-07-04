from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from source2study import __version__
from source2study.adapters.base import AdapterResult, SourceAdapter, SourceRequest
from source2study.adapters.utils import file_sha256
from source2study.models.evidence import EvidenceRecord
from source2study.models.source import SourceRecord


def cache_root(workspace: Path) -> Path:
    return workspace / ".source2study" / "cache"


def _local_source_hash(value: str) -> str | None:
    path = Path(value)
    if path.exists() and path.is_file():
        return file_sha256(path)
    if path.exists() and path.is_dir():
        items: list[str] = []
        for child in sorted(p for p in path.rglob("*") if p.is_file()):
            if any(part in {".git", "__pycache__", "node_modules", ".venv"} for part in child.parts):
                continue
            rel = child.relative_to(path).as_posix()
            stat = child.stat()
            items.append(f"{rel}:{stat.st_size}:{int(stat.st_mtime)}")
        return "dir:" + str(abs(hash("|".join(items))))
    return None


def cache_key(adapter: SourceAdapter, request: SourceRequest) -> str:
    from hashlib import sha256

    payload: dict[str, Any] = {
        "source_uri": request.value,
        "adapter_name": adapter.__class__.__name__,
        "adapter_version": getattr(adapter, "version", "1"),
        "content_hash": _local_source_hash(request.value),
        "extraction_options": {
            "allow_network": request.policy.allow_network,
            "allow_audio_asr": request.policy.allow_audio_asr,
            "allow_screenshots": request.policy.allow_screenshots,
            "source_type": request.source_type,
        },
        "authorization": request.authorization,
        "source2study_version": __version__,
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return sha256(raw.encode("utf-8")).hexdigest()


class CacheStore:
    def __init__(self, workspace: Path):
        self.root = cache_root(workspace)

    def result_path(self, key: str) -> Path:
        return self.root / "extracted" / key / "adapter_result.json"

    def get(self, key: str) -> AdapterResult | None:
        path = self.result_path(key)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return AdapterResult(
            source=SourceRecord.from_dict(data["source"]),
            evidence=[EvidenceRecord.from_dict(record) for record in data.get("evidence", [])],
            artifacts=[Path(item) for item in data.get("artifacts", [])],
            warnings=data.get("warnings", []) + ["cache hit"],
        )

    def put(self, key: str, result: AdapterResult) -> None:
        path = self.result_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "source": result.source.to_dict(),
            "evidence": [record.to_dict() for record in result.evidence],
            "artifacts": [str(path) for path in result.artifacts],
            "warnings": result.warnings,
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
