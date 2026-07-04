# Wiki And MindMap Extension

`StudyLoom / source2study` can export a source-grounded personal wiki and concept map from an existing workspace.

This is not Wikipedia scraping, external encyclopedia expansion, or free-form LLM knowledge generation. The exporter only uses:

- `EvidenceIndex`
- `ConceptGraph`
- source metadata already captured by intake

Every concept page and core mindmap node must keep evidence ids.

## Commands

```bash
source2study wiki build ./workspace/demo
source2study graph export ./workspace/demo --format markmap
source2study graph export ./workspace/demo --format mermaid
source2study graph export ./workspace/demo --format json
```

Default outputs:

```text
workspace/wiki/
  index.md
  glossary.md
  sources.md
  concepts/*.md

workspace/visuals/
  concept_graph.md
  concept_graph.mmd
  concept_graph.json
```

## Safety Rules

- Do not invent concepts that are not linked to evidence.
- Do not create wiki pages without evidence ids.
- Do not use this feature to crawl Wikipedia or external knowledge bases.
- Degraded or low-confidence evidence should remain visible in generated pages.
- Mind maps are navigation aids, not replacements for the evidence ledger.

## Viewing

Markmap Markdown can be rendered with Markmap-compatible tools. Mermaid output can be pasted into GitHub Markdown fenced as `mermaid`, or rendered by Mermaid-compatible viewers.
