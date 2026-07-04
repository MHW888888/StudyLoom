from __future__ import annotations

import re
from pathlib import Path

from source2study.adapters.base import AdapterError, AdapterResult, SourceAdapter, SourceRequest
from source2study.adapters.utils import file_sha256, read_text_lossy, split_paragraphs, stable_id, utc_now
from source2study.models.evidence import EvidenceLocation, EvidenceRecord
from source2study.models.source import AdapterCapability, SourceRecord


class TranscriptAdapter(SourceAdapter):
    name = "transcript_import"
    source_types = ("transcript",)
    risk_level = "low"
    default_enabled = True
    allowed_methods = ("user_uploaded_srt", "user_uploaded_vtt", "user_uploaded_transcript_txt")
    blocked_methods = ("video_download", "default_asr", "drm_bypass", "paywall_bypass")
    source_type_aliases = ("transcript", "subtitle", "srt", "vtt", "bilibili_transcript", "youtube_transcript")
    transcript_suffixes = {".srt", ".vtt"}

    def can_handle(self, request: SourceRequest) -> bool:
        path = Path(request.value)
        if not path.exists() or not path.is_file():
            return False
        if path.suffix.lower() in self.transcript_suffixes:
            return True
        return bool(request.source_type and self.matches_source_type(request.source_type) and path.suffix.lower() == ".txt")

    def capability(self) -> AdapterCapability:
        return AdapterCapability(
            source_type="transcript",
            availability="high",
            supported_methods=["user_uploaded_srt", "user_uploaded_vtt", "user_uploaded_transcript_txt"],
            required_authorization=["user_authorized_local_processing"],
            expected_outputs=["timestamped transcript evidence", "source ledger"],
            known_risks=["copyrighted transcripts", "caption errors", "missing speaker/visual context"],
            fallbacks=["upload transcript file", "upload local notes", "upload screenshots for OCR"],
            last_verified="local_import",
            risk_level=self.risk_level,
            default_enabled=self.default_enabled,
            allowed_methods=list(self.allowed_methods),
            blocked_methods=list(self.blocked_methods),
        )

    def ingest(self, request: SourceRequest) -> AdapterResult:
        decision = self.policy_check(request)
        if not decision.allowed:
            raise AdapterError(decision.reason, "; ".join(decision.safe_alternatives))

        path = Path(request.value).resolve()
        text = read_text_lossy(path)
        if not text.strip():
            raise AdapterError("Transcript file is empty.", "Provide a non-empty .srt, .vtt, or transcript .txt file.")

        source_id = stable_id("src_transcript", str(path))
        transcript_source = "subtitle" if path.suffix.lower() in self.transcript_suffixes else "manual_transcript"
        source = SourceRecord(
            source_id=source_id,
            source_type="transcript",
            source_url_or_path=str(path),
            title=path.stem,
            platform="user_transcript",
            capture_time=utc_now(),
            transcript_source=transcript_source,
            language="unknown",
            duration_or_page_count=str(len(text)),
            files_created=[str(path)],
            hashes={"transcript": file_sha256(path)},
            available_metadata={
                "capture_method": "user_uploaded_transcript",
                "policy": decision.to_dict(),
            },
            capability=self.capability(),
        )
        evidence = self._transcript_evidence(source_id, path, text)
        return AdapterResult(source=source, evidence=evidence, artifacts=[path])

    def _transcript_evidence(self, source_id: str, path: Path, text: str) -> list[EvidenceRecord]:
        chunks = split_paragraphs(self._strip_noise(text), max_chars=700)
        records: list[EvidenceRecord] = []
        for index, chunk in enumerate(chunks, start=1):
            start, end = self._extract_time(chunk)
            clean = re.sub(r"\d{2}:\d{2}:\d{2}[,\.]\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}[,\.]\d{3}", "", chunk).strip()
            records.append(
                EvidenceRecord(
                    evidence_id=f"ev_{source_id}_{index}",
                    source_id=source_id,
                    source_type="transcript",
                    text=clean or chunk,
                    location=EvidenceLocation(timestamp_start=start, timestamp_end=end, section=f"transcript chunk {index}", path=path.name),
                    confidence=0.9,
                    metadata={
                        "capture_method": "user_uploaded_transcript",
                        "source_title": path.stem,
                        "source_url_or_path": str(path),
                    },
                )
            )
        return records

    def _strip_noise(self, text: str) -> str:
        text = re.sub(r"WEBVTT[^\n]*", "", text)
        text = re.sub(r"^\d+\s*$", "", text, flags=re.MULTILINE)
        return text.strip()

    def _extract_time(self, text: str) -> tuple[str | None, str | None]:
        match = re.search(r"(\d{2}:\d{2}:\d{2})[,\.]\d{3}\s+-->\s+(\d{2}:\d{2}:\d{2})[,\.]\d{3}", text)
        if not match:
            return None, None
        return match.group(1), match.group(2)
