from __future__ import annotations

import zipfile
from xml.etree import ElementTree as ET
from pathlib import Path

from source2study.adapters.base import AdapterError, AdapterResult, SourceAdapter, SourceRequest
from source2study.adapters.utils import file_sha256, split_paragraphs, stable_id, utc_now
from source2study.models.evidence import EvidenceLocation, EvidenceRecord
from source2study.models.source import AdapterCapability
from source2study.models.source import SourceRecord


W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


class DocxAdapter(SourceAdapter):
    name = "docx_document"
    source_types = ("docx",)
    risk_level = "low"
    default_enabled = True
    allowed_methods = ("user_uploaded_docx", "openxml_text_extraction")
    blocked_methods = ("silent_table_loss", "silent_image_loss", "comment_loss")
    source_type_aliases = ("word", "docx", "word_document")

    def can_handle(self, request: SourceRequest) -> bool:
        path = Path(request.value)
        return path.exists() and path.is_file() and path.suffix.lower() == ".docx"

    def capability(self) -> AdapterCapability:
        return AdapterCapability(
            source_type="docx",
            availability="medium",
            supported_methods=["user_uploaded_docx", "openxml_text_extraction"],
            required_authorization=["user_authorized_local_processing"],
            expected_outputs=["headings", "body text", "tables", "images", "comments", "headers and footers"],
            known_risks=["complex table formatting simplified", "image content counted but not OCR-parsed", "tracked changes not fully modeled"],
            fallbacks=["export DOCX to PDF/Markdown", "paste key sections", "upload images/screenshots with OCR sidecars"],
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
            parsed = _parse_docx(path)
        except (KeyError, ET.ParseError, zipfile.BadZipFile) as exc:
            raise AdapterError("DOCX file could not be parsed as Office Open XML.", "Export to Markdown/PDF or provide screenshots/OCR sidecars.") from exc

        source_id = stable_id("src_docx", str(path))
        warnings: list[str] = []
        if parsed["images_count"]:
            warnings.append("DOCX contains embedded images; image pixels are counted but not OCR-parsed by the alpha extractor.")
        if parsed["tables_count"]:
            warnings.append("DOCX tables were extracted as text; complex merged-cell layout may be simplified.")
        if not parsed["blocks"] and parsed["images_count"]:
            warnings.append("DOCX has images but no extractable text; generated learning material will be low-confidence.")

        source = SourceRecord(
            source_id=source_id,
            source_type="docx",
            source_url_or_path=str(path),
            title=path.stem,
            platform="local_docx",
            capture_time=utc_now(),
            transcript_source="docx_openxml",
            language="unknown",
            duration_or_page_count=f"{len(parsed['blocks'])} blocks",
            files_created=[str(path)],
            hashes={"content": file_sha256(path)},
            available_metadata={
                "capture_method": "user_uploaded_docx",
                "headings_count": parsed["headings_count"],
                "tables_count": parsed["tables_count"],
                "images_count": parsed["images_count"],
                "comments_count": parsed["comments_count"],
                "footnotes_count": parsed["footnotes_count"],
                "headers_footers_count": parsed["headers_footers_count"],
                "policy": decision.to_dict(),
            },
            known_failures=warnings,
            capability=self.capability(),
        )

        evidence: list[EvidenceRecord] = []
        for index, block in enumerate(parsed["blocks"], start=1):
            for chunk_index, chunk in enumerate(split_paragraphs(block["text"], max_chars=900), start=1):
                evidence.append(
                    EvidenceRecord(
                        evidence_id=f"ev_{source_id}_{index}_{chunk_index}",
                        source_id=source_id,
                        source_type="docx",
                        text=chunk,
                        location=EvidenceLocation(section=block["section"], path=block["path"]),
                        kind=block["kind"],
                        confidence=block["confidence"],
                        metadata={
                            "capture_method": "user_uploaded_docx",
                            "block_kind": block["kind"],
                            "source_title": path.stem,
                            "source_url_or_path": str(path),
                        },
                    )
                )
        if not evidence:
            evidence.append(
                EvidenceRecord(
                    evidence_id=f"ev_{source_id}_asset_1",
                    source_id=source_id,
                    source_type="docx",
                    text=f"DOCX contains {parsed['images_count']} embedded image(s), but no extractable text was found.",
                    location=EvidenceLocation(section="docx asset summary", path=path.name),
                    kind="asset_summary",
                    confidence=0.35,
                    metadata={"images_count": parsed["images_count"], "capture_method": "user_uploaded_docx"},
                )
            )

        return AdapterResult(source=source, evidence=evidence, artifacts=[path], warnings=warnings)


def _parse_docx(path: Path) -> dict:
    blocks: list[dict] = []
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        document = ET.fromstring(archive.read("word/document.xml"))
        headings_count = 0
        tables_count = 0
        body = document.find(f".//{W_NS}body")
        for child in list(body) if body is not None else []:
            if child.tag == f"{W_NS}p":
                text = _text(child)
                if not text:
                    continue
                style = _paragraph_style(child)
                kind = "heading" if style.lower().startswith("heading") else "text"
                headings_count += 1 if kind == "heading" else 0
                blocks.append({"kind": kind, "text": text, "section": style or "paragraph", "path": "word/document.xml", "confidence": 0.95})
            elif child.tag == f"{W_NS}tbl":
                table_text = _table_text(child)
                if table_text:
                    tables_count += 1
                    blocks.append(
                        {
                            "kind": "table",
                            "text": table_text,
                            "section": f"table {tables_count}",
                            "path": "word/document.xml",
                            "confidence": 0.86,
                        }
                    )

        comments_count = _append_part_blocks(archive, names, "word/comments.xml", "comment", blocks)
        footnotes_count = _append_part_blocks(archive, names, "word/footnotes.xml", "footnote", blocks)
        footnotes_count += _append_part_blocks(archive, names, "word/endnotes.xml", "endnote", blocks)
        headers_footers_count = 0
        for name in sorted(n for n in names if n.startswith("word/header") or n.startswith("word/footer")):
            headers_footers_count += _append_part_blocks(archive, names, name, "header_footer", blocks)
        images_count = sum(1 for name in names if name.startswith("word/media/"))

    return {
        "blocks": blocks,
        "headings_count": headings_count,
        "tables_count": tables_count,
        "images_count": images_count,
        "comments_count": comments_count,
        "footnotes_count": footnotes_count,
        "headers_footers_count": headers_footers_count,
    }


def _text(element: ET.Element) -> str:
    return " ".join((node.text or "").strip() for node in element.iter(f"{W_NS}t") if (node.text or "").strip()).strip()


def _paragraph_style(paragraph: ET.Element) -> str:
    style = paragraph.find(f".//{W_NS}pStyle")
    return style.attrib.get(f"{W_NS}val", "paragraph") if style is not None else "paragraph"


def _table_text(table: ET.Element) -> str:
    rows: list[str] = []
    for row in table.findall(f".//{W_NS}tr"):
        cells = [_text(cell) for cell in row.findall(f"{W_NS}tc")]
        cells = [cell for cell in cells if cell]
        if cells:
            rows.append(" | ".join(cells))
    return "\n".join(rows)


def _append_part_blocks(archive: zipfile.ZipFile, names: set[str], name: str, kind: str, blocks: list[dict]) -> int:
    if name not in names:
        return 0
    root = ET.fromstring(archive.read(name))
    count = 0
    for paragraph in root.iter(f"{W_NS}p"):
        text = _text(paragraph)
        if not text:
            continue
        count += 1
        blocks.append({"kind": kind, "text": text, "section": f"{kind} {count}", "path": name, "confidence": 0.88})
    return count
