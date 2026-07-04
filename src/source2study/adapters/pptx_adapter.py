from __future__ import annotations

import re
import zipfile
from xml.etree import ElementTree as ET
from pathlib import Path

from source2study.adapters.base import AdapterError, AdapterResult, SourceAdapter, SourceRequest
from source2study.adapters.utils import file_sha256, split_paragraphs, stable_id, utc_now
from source2study.models.evidence import EvidenceLocation, EvidenceRecord
from source2study.models.source import AdapterCapability
from source2study.models.source import SourceRecord


A_NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}"


class PptxAdapter(SourceAdapter):
    name = "pptx_deck"
    source_types = ("pptx",)
    risk_level = "low"
    default_enabled = True
    allowed_methods = ("user_uploaded_pptx", "openxml_slide_text_extraction")
    blocked_methods = ("silent_slide_loss", "silent_speaker_note_loss", "chart_data_loss")
    source_type_aliases = ("ppt", "pptx", "slides", "slide_deck")

    def can_handle(self, request: SourceRequest) -> bool:
        path = Path(request.value)
        return path.exists() and path.is_file() and path.suffix.lower() == ".pptx"

    def capability(self) -> AdapterCapability:
        return AdapterCapability(
            source_type="pptx",
            availability="medium",
            supported_methods=["user_uploaded_pptx", "openxml_slide_text_extraction", "speaker_note_extraction"],
            required_authorization=["user_authorized_local_processing"],
            expected_outputs=["slides", "titles", "body text", "images", "charts", "speaker notes"],
            known_risks=["image pixels counted but not OCR-parsed", "chart data not parsed yet", "animation order not preserved yet"],
            fallbacks=["export slides to PDF", "upload speaker notes", "upload slide screenshots with OCR sidecars"],
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
        try:
            parsed = _parse_pptx(path)
        except (KeyError, ET.ParseError, zipfile.BadZipFile) as exc:
            raise AdapterError("PPTX file could not be parsed as Office Open XML.", "Export slides to PDF or upload screenshots plus speaker notes.") from exc

        source_id = stable_id("src_pptx", str(path))
        warnings: list[str] = []
        if parsed["images_count"]:
            warnings.append("PPTX contains embedded images; image pixels are counted but not OCR-parsed by the alpha extractor.")
        if parsed["charts_count"]:
            warnings.append("PPTX contains charts; chart data is counted but not reconstructed as structured table data.")
        if parsed["slides_count"] and not parsed["slide_blocks"]:
            warnings.append("PPTX slides were found but no readable slide text was extracted.")

        source = SourceRecord(
            source_id=source_id,
            source_type="pptx",
            source_url_or_path=str(path),
            title=path.stem,
            platform="local_pptx",
            capture_time=utc_now(),
            transcript_source="pptx_openxml",
            language="unknown",
            duration_or_page_count=f"{parsed['slides_count']} slides",
            files_created=[str(path)],
            hashes={"content": file_sha256(path)},
            available_metadata={
                "capture_method": "user_uploaded_pptx",
                "slides_count": parsed["slides_count"],
                "speaker_notes_count": parsed["speaker_notes_count"],
                "images_count": parsed["images_count"],
                "charts_count": parsed["charts_count"],
                "policy": decision.to_dict(),
            },
            known_failures=warnings,
            capability=self.capability(),
        )

        evidence: list[EvidenceRecord] = []
        for block in parsed["slide_blocks"] + parsed["note_blocks"]:
            for chunk_index, chunk in enumerate(split_paragraphs(block["text"], max_chars=900), start=1):
                evidence.append(
                    EvidenceRecord(
                        evidence_id=f"ev_{source_id}_{block['kind']}_{block['slide']}_{chunk_index}",
                        source_id=source_id,
                        source_type="pptx",
                        text=chunk,
                        location=EvidenceLocation(page=block["slide"], section=block["section"], path=block["path"]),
                        kind=block["kind"],
                        confidence=block["confidence"],
                        metadata={
                            "capture_method": "user_uploaded_pptx",
                            "slide": block["slide"],
                            "block_kind": block["kind"],
                            "source_title": path.stem,
                            "source_url_or_path": str(path),
                        },
                    )
                )
        if not evidence and parsed["images_count"]:
            evidence.append(
                EvidenceRecord(
                    evidence_id=f"ev_{source_id}_asset_1",
                    source_id=source_id,
                    source_type="pptx",
                    text=f"PPTX contains {parsed['slides_count']} slide(s) and {parsed['images_count']} embedded image(s), but no readable text was found.",
                    location=EvidenceLocation(section="pptx asset summary", path=path.name),
                    kind="asset_summary",
                    confidence=0.35,
                    metadata={"slides_count": parsed["slides_count"], "images_count": parsed["images_count"], "capture_method": "user_uploaded_pptx"},
                )
            )
        if not evidence:
            raise AdapterError("No extractable PPTX text found.", "Export slides to PDF/Markdown or upload screenshots plus speaker notes.")

        return AdapterResult(source=source, evidence=evidence, artifacts=[path], warnings=warnings)


def _parse_pptx(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        slide_names = sorted((name for name in names if re.match(r"ppt/slides/slide\d+\.xml$", name)), key=_number)
        note_names = sorted((name for name in names if re.match(r"ppt/notesSlides/notesSlide\d+\.xml$", name)), key=_number)
        slide_blocks = []
        note_blocks = []
        for name in slide_names:
            slide_number = _number(name)
            text = _part_text(archive, name)
            if text:
                slide_blocks.append(
                    {
                        "kind": "slide_text",
                        "text": text,
                        "slide": slide_number,
                        "section": f"slide {slide_number}",
                        "path": name,
                        "confidence": 0.92,
                    }
                )
        for name in note_names:
            slide_number = _number(name)
            text = _part_text(archive, name)
            if text:
                note_blocks.append(
                    {
                        "kind": "speaker_note",
                        "text": text,
                        "slide": slide_number,
                        "section": f"speaker notes for slide {slide_number}",
                        "path": name,
                        "confidence": 0.88,
                    }
                )
        return {
            "slides_count": len(slide_names),
            "speaker_notes_count": len(note_blocks),
            "images_count": sum(1 for name in names if name.startswith("ppt/media/")),
            "charts_count": sum(1 for name in names if name.startswith("ppt/charts/")),
            "slide_blocks": slide_blocks,
            "note_blocks": note_blocks,
        }


def _part_text(archive: zipfile.ZipFile, name: str) -> str:
    root = ET.fromstring(archive.read(name))
    chunks = [(node.text or "").strip() for node in root.iter(f"{A_NS}t") if (node.text or "").strip()]
    return "\n".join(chunks).strip()


def _number(name: str) -> int:
    match = re.search(r"(\d+)", name)
    return int(match.group(1)) if match else 0
