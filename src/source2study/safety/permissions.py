from __future__ import annotations

from source2study.config import SourcePolicy


def require_network(policy: SourcePolicy) -> None:
    if not policy.allow_network:
        raise PermissionError("Network access is disabled by default. Use --allow-network for public sources.")


def require_asr(policy: SourcePolicy) -> None:
    if not policy.allow_audio_asr:
        raise PermissionError("ASR is disabled by default and requires explicit authorization.")
