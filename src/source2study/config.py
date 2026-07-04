from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SourcePolicy:
    allow_video_download: bool = False
    allow_audio_asr: bool = False
    allow_browser_cookies: bool = False
    allow_private_sources: bool = False
    allow_full_copyrighted_text_output: bool = False
    allow_screenshots: bool = True
    allow_network: bool = False


@dataclass(frozen=True)
class RenderConfig:
    formats: tuple[str, ...] = ("md",)


@dataclass(frozen=True)
class QualityConfig:
    require_source_ledger: bool = True
    require_evidence_for_key_claims: bool = True
    fail_on_secret_leak: bool = True
    fail_on_unverified_major_claim: bool = True


@dataclass(frozen=True)
class AppConfig:
    output_dir: Path = Path("outputs")
    language: str = "zh"
    mode: str = "beginner_full"
    source_policy: SourcePolicy = field(default_factory=SourcePolicy)
    render: RenderConfig = field(default_factory=RenderConfig)
    quality: QualityConfig = field(default_factory=QualityConfig)
