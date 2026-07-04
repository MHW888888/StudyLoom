from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def template_pack_dir() -> Path:
    repo_dir = Path(__file__).resolve().parents[2]
    return repo_dir / "templates" / "packs"


def list_template_packs() -> list[dict[str, Any]]:
    directory = template_pack_dir()
    packs = []
    for path in sorted(directory.glob("*.json")) if directory.exists() else []:
        data = json.loads(path.read_text(encoding="utf-8"))
        data.setdefault("id", path.stem)
        packs.append(data)
    return packs


def load_template_pack(template_id: str) -> dict[str, Any]:
    normalized = template_id.lower().strip()
    for pack in list_template_packs():
        if pack.get("id") == normalized or pack.get("name", "").lower() == normalized:
            return pack
    raise ValueError(f"Unknown template pack: {template_id}")


def copy_template_pack(template_id: str, workspace: Path, output_dir: Path | None = None) -> Path:
    pack = load_template_pack(template_id)
    target_dir = output_dir or workspace / "templates" / pack["id"]
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "pack.json").write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
    (target_dir / "README.md").write_text(_readme(pack), encoding="utf-8")
    return target_dir


def copy_all_template_packs(workspace: Path, output_dir: Path | None = None) -> Path:
    target_root = output_dir or workspace / "templates"
    target_root.mkdir(parents=True, exist_ok=True)
    for pack in list_template_packs():
        copy_template_pack(pack["id"], workspace, target_root / pack["id"])
    return target_root


def _readme(pack: dict[str, Any]) -> str:
    lines = [
        f"# {pack.get('name', pack.get('id', 'Template Pack'))}",
        "",
        pack.get("description", "StudyLoom template pack."),
        "",
        "## Intended Use",
        "",
        f"- Use case: `{pack.get('use_case', 'general')}`",
        f"- Mode: `{pack.get('mode', 'beginner')}`",
        "",
        "## Required Blocks",
        "",
    ]
    lines.extend(f"- `{block}`" for block in pack.get("required_blocks", []))
    lines.extend(
        [
            "",
            "## Required Quality Gates",
            "",
            "- Include `Source Intake Summary` so readers can see extraction status and warnings.",
            "- Include `Source Appendix` so every pack stays audit-ready.",
            "- Run citation validation before sharing the generated pack.",
            "",
            "## Safety Notes",
            "",
        ]
    )
    lines.extend(f"- {note}" for note in pack.get("safety_notes", []))
    lines.append("")
    return "\n".join(lines)
