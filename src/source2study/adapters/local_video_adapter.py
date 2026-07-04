from __future__ import annotations

import re
from pathlib import Path

from source2study.adapters.base import AdapterError, AdapterResult, SourceAdapter, SourceRequest
from source2study.adapters.utils import file_sha256, read_text_lossy, split_paragraphs, stable_id, utc_now
from source2study.models.evidence import EvidenceLocation, EvidenceRecord
from source2study.models.source import AdapterCapability, SourceRecord


class LocalVideoAdapter(SourceAdapter):
    name = "local_video_transcript"
    source_types = ("video",)
    risk_level = "low"
    default_enabled = True
    allowed_methods = ("user_provided_transcript", "companion_subtitle")
    blocked_methods = ("default_asr", "bulk_media_download", "drm_bypass")
    source_type_aliases = ("local_video", "local_audio", "media")
    video_suffixes = {".mp4", ".mov", ".mkv", ".webm", ".mp3", ".wav", ".m4a"}
    transcript_suffixes = {".vtt", ".srt", ".txt"}

    def can_handle(self, request: SourceRequest) -> bool:
        path = Path(request.value)
        return path.exists() and path.is_file() and path.suffix.lower() in (self.video_suffixes | self.transcript_suffixes)

    def capability(self) -> AdapterCapability:
        return AdapterCapability(
            source_type="local_video",
            availability="medium",
            supported_methods=["user_provided_transcript", "companion_subtitle"],
            required_authorization=["user_authorized_local_processing"],
            expected_outputs=["timestamped transcript evidence when subtitles exist"],
            known_risks=["ASR not enabled in MVP", "private content"],
            fallbacks=["provide .vtt/.srt/.txt transcript", "enable ASR in future version"],
            risk_level=self.risk_level,
            default_enabled=self.default_enabled,
            allowed_methods=list(self.allowed_methods),
            blocked_methods=list(self.blocked_methods),
        )

    def ingest(self, request: SourceRequest) -> AdapterResult:
        path = Path(request.value).resolve()
        transcript_path = self._find_transcript(path)
        if transcript_path is None:
            raise AdapterError(
                "No transcript or subtitle file found for local media.",
                "Provide a .vtt, .srt, or .txt transcript next to the media file.",
            )

        text = read_text_lossy(transcript_path)
        source_id = stable_id("src_media", str(path))
        source = SourceRecord(
            source_id=source_id,
            source_type="video",
            source_url_or_path=str(path),
            title=path.stem,
            platform="local_media",
            capture_time=utc_now(),
            transcript_source="manual" if transcript_path.suffix.lower() == ".txt" else "subtitle",
            language="unknown",
            files_created=[str(transcript_path)],
            hashes={"media_or_transcript": file_sha256(transcript_path)},
            capability=self.capability(),
        )
        evidence = self._transcript_evidence(source_id, text)
        return AdapterResult(source=source, evidence=evidence, artifacts=[transcript_path])

    def _find_transcript(self, path: Path) -> Path | None:
        if path.suffix.lower() in self.transcript_suffixes:
            return path
        for suffix in (".vtt", ".srt", ".txt"):
            candidate = path.with_suffix(suffix)
            if candidate.exists():
                return candidate
        return None

    def _transcript_evidence(self, source_id: str, text: str) -> list[EvidenceRecord]:
        chunks = split_paragraphs(self._strip_subtitle_noise(text), max_chars=700)
        records: list[EvidenceRecord] = []
        for index, chunk in enumerate(chunks, start=1):
            start, end = self._extract_time(chunk)
            clean = re.sub(r"\d{2}:\d{2}:\d{2}[,\.]\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}[,\.]\d{3}", "", chunk).strip()
            records.append(
                EvidenceRecord(
                    evidence_id=f"ev_{source_id}_{index}",
                    source_id=source_id,
                    source_type="video",
                    text=clean or chunk,
                    location=EvidenceLocation(timestamp_start=start, timestamp_end=end, section=f"subtitle chunk {index}"),
                    confidence=0.9,
                )
            )
        return records

    def _strip_subtitle_noise(self, text: str) -> str:
        text = re.sub(r"WEBVTT[^\n]*", "", text)
        text = re.sub(r"^\d+\s*$", "", text, flags=re.MULTILINE)
        return text.strip()

    def _extract_time(self, text: str) -> tuple[str | None, str | None]:
        match = re.search(r"(\d{2}:\d{2}:\d{2})[,\.]\d{3}\s+-->\s+(\d{2}:\d{2}:\d{2})[,\.]\d{3}", text)
        if not match:
            return None, None
        return match.group(1), match.group(2)
