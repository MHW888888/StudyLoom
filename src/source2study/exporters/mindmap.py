from __future__ import annotations

import json
import re
from pathlib import Path

from source2study.indexing.evidence_index import EvidenceIndex
from source2study.knowledge.concept_graph import ConceptGraph, ConceptGraphBuilder


def export_mindmap(index: EvidenceIndex, output_path: Path, export_format: str, graph: ConceptGraph | None = None) -> Path:
    graph = graph or ConceptGraphBuilder().build(index)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if export_format == "markmap":
        output_path.write_text(render_markmap(graph), encoding="utf-8")
    elif export_format == "mermaid":
        output_path.write_text(render_mermaid(graph), encoding="utf-8")
    elif export_format == "json":
        output_path.write_text(json.dumps(render_json(graph), ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        raise ValueError(f"Unsupported mindmap format: {export_format}")
    return output_path


def render_markmap(graph: ConceptGraph) -> str:
    lines = ["# StudyLoom Concept Map", ""]
    for node in graph.nodes:
        evidence = ", ".join(node.evidence_ids) or "no-evidence"
        lines.append(f"## {node.concept.title()} [{evidence}]")
        lines.append(f"### Importance: {node.importance}")
        lines.append(f"### Difficulty: {node.difficulty}")
        if node.prerequisites:
            lines.append("### Prerequisites")
            lines.extend(f"- {item}" for item in node.prerequisites)
        if node.common_misconceptions:
            lines.append("### Misconceptions")
            lines.extend(f"- {item}" for item in node.common_misconceptions[:2])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_mermaid(graph: ConceptGraph) -> str:
    lines = ["graph TD", '  root["StudyLoom Concept Map"]']
    for index, node in enumerate(graph.nodes, start=1):
        concept_id = f"c{index}"
        evidence = ", ".join(node.evidence_ids) or "no evidence"
        lines.append(f'  {concept_id}["{_escape(node.concept.title())}<br/>{_escape(evidence)}"]')
        lines.append(f"  root --> {concept_id}")
        for prerequisite_index, prerequisite in enumerate(node.prerequisites[:3], start=1):
            prereq_id = f"{concept_id}_p{prerequisite_index}"
            lines.append(f'  {prereq_id}["{_escape(prerequisite)}"]')
            lines.append(f"  {prereq_id} --> {concept_id}")
    return "\n".join(lines) + "\n"


def render_json(graph: ConceptGraph) -> dict:
    nodes = [{"id": _slug(node.concept), **node.to_dict()} for node in graph.nodes]
    edges = []
    for node in graph.nodes:
        concept_id = _slug(node.concept)
        for prerequisite in node.prerequisites:
            edges.append({"source": _slug(prerequisite), "target": concept_id, "relation": "prerequisite"})
        for evidence_id in node.evidence_ids:
            edges.append({"source": concept_id, "target": evidence_id, "relation": "supported_by"})
    return {"nodes": nodes, "edges": edges}


def validate_mindmap_text(text: str) -> dict:
    stripped = text.strip()
    if stripped.startswith("{"):
        try:
            data = json.loads(stripped)
        except json.JSONDecodeError:
            data = {}
        evidence_edges = [
            edge
            for edge in data.get("edges", [])
            if edge.get("relation") == "supported_by" and str(edge.get("target", "")).startswith("ev_")
        ]
        issues = []
        if not data.get("nodes"):
            issues.append({"level": "error", "type": "missing_nodes", "message": "JSON mindmap has no nodes."})
        if not evidence_edges:
            issues.append({"level": "error", "type": "missing_evidence", "message": "JSON mindmap has no evidence edges."})
        return {"status": "pass" if not issues else "fail", "issues": issues}

    issues = []
    if "StudyLoom Concept Map" not in text:
        issues.append({"level": "error", "type": "missing_root", "message": "Mindmap root is missing."})
    if "ev_" not in text:
        issues.append({"level": "error", "type": "missing_evidence", "message": "Mindmap has no evidence ids."})
    return {"status": "pass" if not issues else "fail", "issues": issues}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_") or "concept"


def _escape(value: str) -> str:
    return value.replace('"', "'").replace("\n", " ")
