from __future__ import annotations

from pathlib import Path

from source2study.exporters.markdown import render_markdown
from source2study.indexing.evidence_index import EvidenceIndex
from source2study.models.study_pack import StudyPack


def _pdf_escape(text: str) -> str:
    text = text.encode("latin-1", errors="replace").decode("latin-1")
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def write_pdf(pack: StudyPack, index: EvidenceIndex, path: Path) -> Path:
    """Write a small text PDF using standard PDF core fonts.

    Non-Latin glyphs are replaced in this MVP renderer. Markdown remains the
    source of truth for full Unicode output. A same-name Markdown sidecar is
    written before PDF rendering so users can convert with Pandoc, Typst, or
    another production document tool.
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    markdown = render_markdown(pack, index)
    path.with_suffix(".md").write_text(markdown, encoding="utf-8")
    text_lines = markdown.splitlines()
    pages = []
    for page_start in range(0, len(text_lines), 42):
        pages.append(text_lines[page_start : page_start + 42])

    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{3 + i * 2} 0 R" for i in range(len(pages)))
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>".encode("ascii"))
    for idx, lines in enumerate(pages):
        page_obj = 3 + idx * 2
        content_obj = page_obj + 1
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /Contents {content_obj} 0 R >>".encode(
                "ascii"
            )
        )
        content_lines = ["BT", "/F1 10 Tf", "50 750 Td", "14 TL"]
        for line in lines:
            content_lines.append(f"({_pdf_escape(line[:100])}) Tj")
            content_lines.append("T*")
        content_lines.append("ET")
        stream = "\n".join(content_lines).encode("latin-1", errors="replace")
        objects.append(b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream")

    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{number} 0 obj\n".encode("ascii"))
        output.extend(obj)
        output.extend(b"\nendobj\n")
    xref_start = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF\n".encode("ascii")
    )
    path.write_bytes(bytes(output))
    return path
