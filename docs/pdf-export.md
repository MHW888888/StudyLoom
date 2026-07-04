# PDF Export

Source2Study treats Markdown as the canonical document source. The current PDF exporter is intentionally basic and dependency-free.

## Current Behavior

When a PDF is requested, Source2Study:

1. Renders the full learning pack to Markdown.
2. Writes a same-name Markdown sidecar next to the PDF.
3. Renders a simple text PDF with standard PDF core fonts.

Example:

```bash
source2study generate ./workspace/demo \
  --mode beginner \
  --output ./workspace/demo/outputs/beginner.pdf
```

This creates:

```text
./workspace/demo/outputs/beginner.pdf
./workspace/demo/outputs/beginner.md
```

## Why Markdown Comes First

Markdown preserves:

- full Unicode text
- Chinese content
- source appendix
- citation cards
- learning maps
- quiz and practice blocks
- one-page review sections

The basic PDF renderer is useful for smoke tests and lightweight sharing, but it is not the final production layout engine.

## Production Conversion Path

For better PDF output, use the generated Markdown sidecar with a document tool such as Pandoc, Typst, or a future Source2Study rich renderer.

Recommended future production features:

- Chinese font configuration
- generated table of contents
- page headers and footers
- citation footnotes
- screenshot evidence cards
- concept-card styling
- visual QA by rendered pages

## Boundary

The PDF exporter should not block learning-pack generation. If the basic PDF has limited typography, the Markdown remains the complete source of truth.
