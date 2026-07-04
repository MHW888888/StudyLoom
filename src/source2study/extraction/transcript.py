from __future__ import annotations

from pathlib import Path

from source2study.adapters.local_video_adapter import LocalVideoAdapter
from source2study.adapters.base import SourceRequest


def transcript_from_file(path: Path, request: SourceRequest):
    return LocalVideoAdapter().ingest(SourceRequest(str(path), request.workspace, request.policy, request.authorization))
