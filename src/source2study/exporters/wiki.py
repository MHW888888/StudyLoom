from __future__ import annotations

import re
from pathlib import Path

from source2study.indexing.evidence_index import EvidenceIndex
from source2study.knowledge.concept_graph import ConceptGraph, ConceptGraphBuilder, ConceptNode


def write_wiki(index: EvidenceIndex, output_dir: Path, graph: ConceptGraph | None = None) -> Path:
    graph = graph or ConceptGraphBuilder().build(index)
    output_dir.mkdir(parents=True, exist_ok=True)
    concepts_dir = output_dir / "concepts"
    concepts_dir.mkdir(exist_ok=True)

    concept_pages: list[tuple[ConceptNode, Path]] = []
    for node in graph.nodes:
        path = concepts_dir / f"{_slug(node.concept)}.md"
        path.write_text(_concept_page(node, graph, index), encoding="utf-8")
        concept_pages.append((node, path))

    (output_dir / "index.md").write_text(_index_page(graph, concept_pages), encoding="utf-8")
    (output_dir / "glossary.md").write_text(_glossary_page(graph), encoding="utf-8")
    (output_dir / "sources.md").write_text(_sources_page(index), encoding="utf-8")
    return output_dir


def validate_wiki(output_dir: Path, index: EvidenceIndex) -> dict:
    issues: list[dict] = []
    evidence_ids = set(index.evidence)
    concept_dir = output_dir / "concepts"
    if not (output_dir / "index.md").exists():
        issues.append({"level": "error", "type": "missing_index", "message": "wiki/index.md is missing."})
    if not concept_dir.exists():
        issues.append({"level": "error", "type": "missing_concepts", "message": "wiki/concepts directory is missing."})
    for page in sorted(concept_dir.glob("*.md")) if concept_dir.exists() else []:
        text = page.read_text(encoding="utf-8")
        ids = set(re.findall(r"\bev_[A-Za-z0-9_\\-]+", text))
        if not ids:
            issues.append({"level": "error", "type": "missing_evidence", "message": f"{page.name} has no evidence id."})
        missing = sorted(ids - evidence_ids)
        if missing:
            issues.append({"level": "error", "type": "unknown_evidence", "message": f"{page.name} references unknown evidence: {', '.join(missing)}"})
        if "Source Warnings" in text and "degraded" not in text.lower():
            issues.append({"level": "warning", "type": "warning_without_context", "message": f"{page.name} has warnings without degraded context."})
    return {"status": "pass" if not any(issue["level"] == "error" for issue in issues) else "fail", "issues": issues}


def _concept_page(node: ConceptNode, graph: ConceptGraph, index: EvidenceIndex) -> str:
    evidence_lines = []
    warning_lines = []
    for evidence_id in node.evidence_ids:
        record = index.evidence.get(evidence_id)
        if record is None:
            evidence_lines.append(f"- `{evidence_id}`: missing from EvidenceIndex")
            continue
        evidence_lines.append(f"- `{evidence_id}`: {record.location.label()}, confidence={record.confidence:.2f}")
        if record.confidence < 0.75:
            warning_lines.append(f"- `{evidence_id}` is low-confidence evidence.")
    related = [other.concept for other in graph.nodes if other.concept != node.concept][:5]
    lines = [
        f"# {node.concept.title()}",
        "",
        "## One-Sentence Explanation",
        "",
        f"{node.concept.title()} is a source-backed concept extracted from the user's materials.",
        "",
        "## Why It Matters",
        "",
        f"- Importance: `{node.importance}`",
        f"- Difficulty: `{node.difficulty}`",
        f"- Recommended treatment: `{node.recommended_treatment}`",
        "",
        "## Prerequisites",
        "",
    ]
    lines.extend(f"- {item}" for item in node.prerequisites or ["source context"])
    lines.extend(["", "## Common Misconceptions", ""])
    lines.extend(f"- {item}" for item in node.common_misconceptions or ["Do not treat this page as source-free generated truth."])
    lines.extend(["", "## Related Concepts", ""])
    lines.extend(f"- [[{_slug(item)}|{item.title()}]]" for item in related) if related else lines.append("- No related concepts yet.")
    lines.extend(["", "## Source Evidence", ""])
    lines.extend(evidence_lines or ["- No evidence ids available."])
    if warning_lines:
        lines.extend(["", "## Source Warnings", ""])
        lines.extend(warning_lines)
    lines.append("")
    return "\n".join(lines)


def _index_page(graph: ConceptGraph, pages: list[tuple[ConceptNode, Path]]) -> str:
    lines = [
        "# StudyLoom Wiki",
        "",
        "This is a source-grounded personal learning wiki generated from EvidenceIndex and ConceptGraph.",
        "",
        "## Concepts",
        "",
    ]
    for node, path in pages:
        ids = ", ".join(f"`{item}`" for item in node.evidence_ids)
        lines.append(f"- [{node.concept.title()}](concepts/{path.name}) - evidence: {ids}")
    lines.extend(["", "## Navigation", "", "- [Glossary](glossary.md)", "- [Sources](sources.md)", ""])
    return "\n".join(lines)


def _glossary_page(graph: ConceptGraph) -> str:
    lines = ["# Glossary", ""]
    for node in graph.nodes:
        lines.append(f"- **{node.concept.title()}**: {node.importance}; difficulty={node.difficulty}; evidence={', '.join(node.evidence_ids)}")
    lines.append("")
    return "\n".join(lines)


def _sources_page(index: EvidenceIndex) -> str:
    lines = ["# Sources", ""]
    for source in index.sources.values():
        lines.append(f"- `{source.source_id}`: {source.title} ({source.source_type}, {source.platform})")
    lines.extend(["", "## Evidence", ""])
    for record in index.evidence.values():
        lines.append(f"- `{record.evidence_id}`: {record.source_id}, {record.location.label()}, confidence={record.confidence:.2f}")
    lines.append("")
    return "\n".join(lines)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "concept"
