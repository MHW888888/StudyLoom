from __future__ import annotations

import html
import zipfile
from pathlib import Path

from source2study.exporters.markdown import render_markdown
from source2study.indexing.evidence_index import EvidenceIndex
from source2study.models.study_pack import StudyPack


def write_docx(pack: StudyPack, index: EvidenceIndex, path: Path) -> Path:
    """Write a minimal DOCX without external dependencies.

    The renderer keeps the dependency-free MVP contract while preserving
    learning-pack hierarchy: title, headings, table-of-contents placeholder,
    concept-card-like paragraphs, quiz blocks, and source appendix sections.
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    paragraphs = [_paragraph_for_markdown_line(line) for line in render_markdown(pack, index).splitlines()]
    body = "".join(paragraphs)
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{body}</w:body></w:document>"
    )
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
            "</Types>",
        )
        archive.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            "</Relationships>",
        )
        archive.writestr(
            "word/_rels/document.xml.rels",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
            "</Relationships>",
        )
        archive.writestr("word/document.xml", document)
        archive.writestr("word/styles.xml", _styles_xml())
    return path


def _paragraph_for_markdown_line(line: str) -> str:
    if not line:
        return _paragraph("")
    if line.startswith("# "):
        return _paragraph(line[2:].strip(), "Title")
    if line.startswith("## "):
        return _paragraph(line[3:].strip(), "Heading1")
    if line.startswith("### "):
        return _paragraph(line[4:].strip(), "Heading2")
    if line.startswith("#### "):
        return _paragraph(line[5:].strip(), "Heading3")
    if line.startswith("- "):
        return _paragraph(line, "ListParagraph")
    if line.startswith(("Concept:", "Common misconceptions:", "Source evidence:", "Checkpoint quiz:", "Practice task:", "Creator task:")):
        return _paragraph(line, "IntenseQuote")
    if line.startswith("Chapter objective:"):
        return _paragraph(line, "Subtitle")
    return _paragraph(line)


def _paragraph(text: str, style: str | None = None) -> str:
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    return f"<w:p>{style_xml}<w:r><w:t>{html.escape(text)}</w:t></w:r></w:p>"


def _styles_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/></w:style>'
        '<w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/></w:style>'
        '<w:style w:type="paragraph" w:styleId="ListParagraph"><w:name w:val="List Paragraph"/></w:style>'
        '<w:style w:type="paragraph" w:styleId="IntenseQuote"><w:name w:val="Intense Quote"/></w:style>'
        "</w:styles>"
    )
