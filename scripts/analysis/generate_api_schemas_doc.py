"""Genere docs/API_SCHEMAS.md a partir des schemas Pydantic.

Usage:
    python scripts/analysis/generate_api_schemas_doc.py
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = ROOT / "src" / "api" / "schemas"
OUTPUT = ROOT / "docs" / "API_SCHEMAS.md"


@dataclass
class SchemaClass:
    module: str
    name: str
    fields: int


def _is_pydantic_class(node: ast.ClassDef) -> bool:
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id.endswith("BaseModel"):
            return True
        if isinstance(base, ast.Attribute) and base.attr.endswith("BaseModel"):
            return True
    return False


def _count_fields(node: ast.ClassDef) -> int:
    count = 0
    for item in node.body:
        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            count += 1
    return count


def _collect() -> list[SchemaClass]:
    items: list[SchemaClass] = []
    for path in sorted(SCHEMAS_DIR.glob("*.py")):
        if path.name == "__init__.py":
            continue
        try:
            contenu = path.read_text(encoding="utf-8-sig")
            tree = ast.parse(contenu, filename=str(path))
        except SyntaxError:
            # Ignore les fichiers non parsables pour conserver une generation robuste.
            continue
        module = path.stem
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and _is_pydantic_class(node):
                items.append(SchemaClass(module=module, name=node.name, fields=_count_fields(node)))
    return items


def _render(classes: list[SchemaClass]) -> str:
    total = len(classes)
    modules = sorted({c.module for c in classes})

    lines: list[str] = []
    lines.append("# API Schemas")
    lines.append("")
    lines.append("Documentation auto-generee depuis `src/api/schemas/*.py`.")
    lines.append("")
    lines.append(f"- Genere le: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    lines.append(f"- Nombre total de classes BaseModel: {total}")
    lines.append(f"- Nombre de modules schemas: {len(modules)}")
    lines.append("")

    for module in modules:
        subset = [c for c in classes if c.module == module]
        lines.append(f"## {module}")
        lines.append("")
        lines.append("| Classe | Champs annotes |")
        lines.append("|---|---:|")
        for c in sorted(subset, key=lambda x: x.name.lower()):
            lines.append(f"| {c.name} | {c.fields} |")
        lines.append("")

    lines.append("## Regeneration")
    lines.append("")
    lines.append("```bash")
    lines.append("python scripts/analysis/generate_api_schemas_doc.py")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    classes = _collect()
    OUTPUT.write_text(_render(classes), encoding="utf-8")
    print(f"Ecrit: {OUTPUT} ({len(classes)} schemas)")


if __name__ == "__main__":
    main()
