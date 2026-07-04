from __future__ import annotations

from pathlib import Path
from typing import Any

from source2study.indexing.evidence_index import EvidenceIndex
from source2study.models.study_pack import StudyPack


def render_markdown(pack: StudyPack, index: EvidenceIndex | None = None) -> str:
    profile = pack.metadata.get("learner_profile") if pack.metadata else None
    spec = pack.metadata.get("learning_pack_spec") if pack.metadata else None
    graph = pack.metadata.get("concept_graph") if pack.metadata else None
    intake_summary = pack.metadata.get("intake_summary") if pack.metadata else None
    lines: list[str] = []
    lines.extend(_cover_lines(pack, profile, spec))
    lines.extend(_source_intake_summary(intake_summary, index))
    lines.extend(_table_of_contents(pack))
    lines.extend(_learning_goals(profile, graph))
    lines.extend(_learning_map(pack, spec, graph))
    if pack.limitations:
        lines.extend(["## Known Limitations", ""])
        lines.extend(f"- {item}" for item in pack.limitations)
        lines.append("")
    lines.extend(["## Study Sections", ""])
    for section in pack.sections:
        lines.extend([f"### {section.title}", ""])
        lines.extend([f"Chapter objective: {_chapter_objective(section.title, spec)}", ""])
        lines.extend([section.body, ""])
        if section.evidence_ids:
            joined = ", ".join(f"`{evidence_id}`" for evidence_id in section.evidence_ids)
            lines.extend([f"Evidence: {joined}", ""])
            if index is not None:
                lines.extend(["#### Citation Card", ""])
                lines.extend(_citation_card_lines(section.evidence_ids, index, limit=5))
                lines.append("")
    lines.extend(_one_page_review(graph))
    if index is not None:
        lines.extend(_source_appendix(index))
    return "\n".join(lines).rstrip() + "\n"


def _cover_lines(pack: StudyPack, profile: dict[str, Any] | None, spec: dict[str, Any] | None) -> list[str]:
    goal = _value(profile, "goal", "not specified")
    level = _value(profile, "current_level", "not specified")
    use_case = _value(profile, "use_case", "general study")
    time_budget = _value(profile, "time_budget", "not specified")
    style = _value(profile, "preferred_style", "source-grounded")
    pack_type = _value(spec, "pack_type", pack.mode.value)
    persona = _value(spec, "persona", use_case)
    return [
        f"# {pack.title}",
        "",
        "Source2Study Learning Pack",
        "",
        "## Cover",
        "",
        f"- Mode: `{pack.mode.value}`",
        f"- Language: `{pack.language}`",
        f"- Pack type: {pack_type}",
        f"- Suitable learner: {persona} / {level}",
        f"- Learning goal: {goal}",
        f"- Estimated study time: {time_budget}",
        f"- Preferred style: {style}",
        "",
        "This document is designed as a source-grounded learning journey, not as a raw transcript or generic summary.",
        "",
        "## Personalization",
        "",
        f"- Goal: {goal}",
        f"- Level: {level}",
        f"- Use case: {use_case}",
        f"- Time budget: {time_budget}",
        f"- Style: {style}",
        "",
    ]


def _table_of_contents(pack: StudyPack) -> list[str]:
    lines = ["## Table Of Contents", ""]
    lines.extend(
        [
            "1. Cover and learner context",
            "2. Learning goals",
            "3. Learning map",
            "4. Study sections",
        ]
    )
    for index, section in enumerate(pack.sections, start=1):
        lines.append(f"   {index}. {section.title}")
    lines.extend(["5. One-page review", "6. Source appendix", ""])
    return lines


def _source_intake_summary(summary: dict[str, Any] | None, index: EvidenceIndex | None) -> list[str]:
    lines = ["## Source Intake Summary", ""]
    if not summary:
        lines.extend(["- Intake report metadata is not attached to this pack.", ""])
    else:
        status = summary.get("status", "unknown")
        lines.append(f"- Intake status: `{status}`")
        lines.append(f"- Source count: {summary.get('source_count', len(summary.get('sources', [])))}")
        if status != "pass":
            lines.append("")
            lines.append("This learning pack is based on partially successful source extraction. Review the warnings before relying on it.")
        sources = summary.get("sources", [])
        if sources:
            lines.extend(["", "Detected sources:"])
            for item in sources:
                assets = item.get("detected_assets", {})
                quality = item.get("extraction_quality", {})
                lines.append(
                    f"- `{item.get('source_id')}` {item.get('source_title')} "
                    f"({item.get('source_type')}, {item.get('status')}): "
                    f"text_blocks={assets.get('text_blocks', 0)}, images={assets.get('images', 0)}, "
                    f"tables={assets.get('tables', 0)}, transcript_segments={assets.get('transcript_segments', 0)}, "
                    f"ocr={quality.get('ocr', 'not_needed')}"
                )
        warnings = summary.get("warnings", [])
        if warnings:
            lines.extend(["", "### Extraction Warnings", ""])
            lines.extend(f"- {warning}" for warning in warnings)
    low_confidence = []
    if index is not None:
        low_confidence = [record for record in index.evidence.values() if record.confidence < 0.75]
    if low_confidence:
        lines.extend(["", "### Low Confidence Evidence", ""])
        for record in low_confidence[:20]:
            lines.append(f"- `{record.evidence_id}`: confidence={record.confidence:.2f}, location={record.location.label()}")
    lines.append("")
    return lines


def _learning_goals(profile: dict[str, Any] | None, graph: dict[str, Any] | None) -> list[str]:
    goal = _value(profile, "goal", "understand the source material")
    concepts = _concept_names(graph, limit=4)
    concept_line = ", ".join(concepts) if concepts else "the core source ideas"
    return [
        "## Learning Goals",
        "",
        f"By the end, you should be able to connect `{goal}` with source-backed concepts.",
        "",
        "- Explain the main ideas in your own words.",
        f"- Navigate the key concepts: {concept_line}.",
        "- Use citations to check where important claims came from.",
        "- Complete the quiz, practice, or review tasks without rereading the whole source.",
        "",
    ]


def _learning_map(pack: StudyPack, spec: dict[str, Any] | None, graph: dict[str, Any] | None) -> list[str]:
    lines = ["## Learning Map", ""]
    concepts = _concept_names(graph, limit=6)
    if concepts:
        lines.append("Concept route:")
        for index, concept in enumerate(concepts, start=1):
            lines.append(f"{index}. {concept}")
    else:
        lines.append("Concept route: use the section order below.")
    structure = spec.get("structure", []) if spec else []
    route = structure or [section.title for section in pack.sections]
    if route:
        lines.extend(["", "Document route:"])
        for index, item in enumerate(route, start=1):
            lines.append(f"{index}. {item}")
    lines.append("")
    return lines


def _chapter_objective(title: str, spec: dict[str, Any] | None) -> str:
    normalized = title.lower()
    if "map" in normalized:
        return "Build a mental route before reading details."
    if "prerequisite" in normalized:
        return "Patch background knowledge before the main concepts."
    if "concept" in normalized or "definition" in normalized:
        return "Understand core terms and bind them to evidence."
    if "quiz" in normalized or "question" in normalized:
        return "Use retrieval practice to check retention."
    if "practice" in normalized or "project" in normalized or "homework" in normalized:
        return "Turn the source ideas into an action or deliverable."
    if "appendix" in normalized:
        return "Audit the source trail behind the learning pack."
    persona = _value(spec, "persona", "learner")
    return f"Move the {persona} learner one step closer to the pack goal."


def _citation_card_lines(evidence_ids: list[str], index: EvidenceIndex, limit: int) -> list[str]:
    lines: list[str] = []
    seen: set[str] = set()
    for evidence_id in evidence_ids:
        if evidence_id in seen:
            continue
        seen.add(evidence_id)
        record = index.evidence.get(evidence_id)
        if record is None:
            lines.append(f"- `{evidence_id}`: missing from EvidenceIndex.")
            continue
        source = index.sources.get(record.source_id)
        source_title = source.title if source else record.source_id
        lines.append(
            f"- `{record.evidence_id}` from `{record.source_id}` ({source_title}), "
            f"{record.location.label()}, confidence={record.confidence:.2f}"
        )
        if len(lines) >= limit:
            break
    return lines or ["- No citation card available."]


def _one_page_review(graph: dict[str, Any] | None) -> list[str]:
    nodes = _concept_nodes(graph, limit=8)
    lines = ["## One-Page Review", ""]
    if not nodes:
        lines.extend(["- Revisit each section and check the cited evidence ids.", ""])
        return lines
    for node in nodes:
        prereqs = ", ".join(node.get("prerequisites", [])) or "source context"
        lines.append(
            f"- {str(node.get('concept', 'concept')).title()}: "
            f"{node.get('importance', 'supporting')}, difficulty={node.get('difficulty', 'unknown')}; "
            f"prerequisites: {prereqs}"
        )
    lines.extend(["", "Use this page for quick review before returning to the full evidence appendix.", ""])
    return lines


def _source_appendix(index: EvidenceIndex) -> list[str]:
    lines = ["## Source Appendix", "", "### Source Ledger", ""]
    for source in index.sources.values():
        lines.append(f"- `{source.source_id}`: {source.title} ({source.source_type}, {source.platform})")
    lines.extend(["", "### Evidence Ledger", ""])
    for record in index.evidence.values():
        lines.append(f"- `{record.evidence_id}`: {record.source_id}, {record.location.label()}, confidence={record.confidence:.2f}")
    lines.extend(["", "### Citation Cards", ""])
    for record in list(index.evidence.values())[:20]:
        excerpt = record.text.strip().replace("\n", " ")
        if len(excerpt) > 180:
            excerpt = excerpt[:177].rstrip() + "..."
        lines.append(f"- `{record.evidence_id}`: {excerpt} [{record.citation()}]")
    return lines


def _value(data: dict[str, Any] | None, key: str, default: str) -> str:
    value = data.get(key) if data else None
    if value in (None, "", []):
        return default
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def _concept_nodes(graph: dict[str, Any] | None, limit: int) -> list[dict[str, Any]]:
    nodes = graph.get("nodes", []) if graph else []
    return [node for node in nodes[:limit] if isinstance(node, dict)]


def _concept_names(graph: dict[str, Any] | None, limit: int) -> list[str]:
    return [str(node.get("concept", "concept")).title() for node in _concept_nodes(graph, limit)]


def write_markdown(pack: StudyPack, index: EvidenceIndex, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(pack, index), encoding="utf-8")
    return path
