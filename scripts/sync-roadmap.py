#!/usr/bin/env python3
"""Sync a course roadmap.tsv status columns with topic folders on disk.

For every roadmap row whose topic folder exists under <course>/topics/ with all seven
required files, sets:
- Status: Concluído
- Material Gerado: Sim
- Flashcards: Sim (or "Pulado" when flashcards.yaml has cards: [])
- Exercícios: Sim
- Teste: Sim

Never touches the Revisado column and never downgrades rows.

Usage:
  python3 scripts/sync-roadmap.py                         # default German course
  python3 scripts/sync-roadmap.py courses/it-from-pt-br   # selected course
  python3 scripts/sync-roadmap.py --check                 # exit 1 if out of sync (CI)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import resolve_course_root, topics_root

REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "lesson.md",
    "vocabulary.yaml",
    "flashcards.yaml",
    "exercises.yaml",
    "test.yaml",
    "story.md",
    "answers.md",
)
COLUMNS = {
    "status": 5,
    "material": 7,
    "flashcards": 8,
    "exercicios": 9,
    "teste": 10,
}
ORDER_COLUMN = 1


def topics_on_disk(root: Path) -> dict[int, Path]:
    found: dict[int, Path] = {}
    for folder in root.glob("*/[0-9][0-9][0-9]-*"):
        if not folder.is_dir():
            continue
        match = re.match(r"^(\d{3})-", folder.name)
        if not match:
            continue
        order = int(match.group(1))
        if order in found:
            raise SystemExit(
                f"Erro: ordem {order} duplicada em disco: {found[order]} e {folder}"
            )
        found[order] = folder
    return found


def is_complete(folder: Path) -> bool:
    return all((folder / name).exists() and (folder / name).stat().st_size > 0 for name in REQUIRED_FILES)


def flashcards_status(folder: Path) -> str:
    try:
        data = yaml.safe_load((folder / "flashcards.yaml").read_text(encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001
        return "Sim"
    return "Sim" if data.get("cards") else "Pulado"


def main() -> int:
    parser = argparse.ArgumentParser(description="Sincroniza roadmap.tsv com as pastas topics/ de um curso.")
    parser.add_argument("course", nargs="?", help="ID ou pasta do curso (padrão: courses/de-from-pt-br)")
    parser.add_argument("--check", action="store_true", help="Não escreve; sai com erro se houver divergência")
    args = parser.parse_args()

    course_root = resolve_course_root(args.course)
    roadmap = course_root / "roadmap.tsv"
    topics = topics_root(course_root)

    lines = roadmap.read_text(encoding="utf-8").splitlines()
    disk = topics_on_disk(topics)
    changes: list[str] = []

    for index, line in enumerate(lines[1:], start=1):
        cells = line.split("\t")
        if len(cells) <= max(COLUMNS.values()):
            continue
        try:
            order = int(cells[ORDER_COLUMN])
        except ValueError:
            continue

        folder = disk.get(order)
        if folder is None or not is_complete(folder):
            continue

        desired = {
            "status": "Concluído",
            "material": "Sim",
            "flashcards": flashcards_status(folder),
            "exercicios": "Sim",
            "teste": "Sim",
        }
        row_changes = []
        for key, column in COLUMNS.items():
            if cells[column] != desired[key]:
                row_changes.append(f"{key}: {cells[column]!r} -> {desired[key]!r}")
                cells[column] = desired[key]
        if row_changes:
            changes.append(f"ordem {order:03d} ({folder.name}): " + "; ".join(row_changes))
            lines[index] = "\t".join(cells)

    if not changes:
        print(f"{roadmap.relative_to(REPO_ROOT)} já está sincronizado.")
        return 0

    if args.check:
        print(f"{roadmap.relative_to(REPO_ROOT)} está desatualizado ({len(changes)} linha(s)):")
        for change in changes:
            print(f"- {change}")
        print(f"Rode: python3 scripts/sync-roadmap.py {course_root.relative_to(REPO_ROOT)}")
        return 1

    roadmap.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{roadmap.relative_to(REPO_ROOT)} atualizado ({len(changes)} linha(s)):")
    for change in changes:
        print(f"- {change}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
