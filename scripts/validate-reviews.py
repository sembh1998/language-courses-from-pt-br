#!/usr/bin/env python3
"""Validate review folders and report missing completed ten-topic blocks."""
from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from pathlib import Path

import yaml

from common import resolve_course_root


REPO_ROOT = Path(__file__).resolve().parents[1]


def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "").casefold())
    text = "".join(character for character in text if not unicodedata.combining(character))
    text = re.sub(r"[_*`\"'“”.,!?;:()\[\]{}<>/\\|-]+", " ", text)
    return " ".join(text.split())


def source_pairs(course_root: Path, block: str) -> set[tuple[str, str]]:
    start, end = map(int, block.split("-"))
    pairs = set()
    for order in range(start, end + 1):
        matches = list((course_root / "topics").glob(f"*/{order:03d}-*"))
        if not matches:
            continue
        topic = matches[0]
        for name, root_key in (("exercises.yaml", "exercises"), ("test.yaml", "questions")):
            path = topic / name
            if not path.exists():
                continue
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if name == "exercises.yaml":
                items = [
                    item
                    for group in data.get(root_key, []) or []
                    if isinstance(group, dict)
                    for item in group.get("items", []) or []
                ]
            else:
                items = data.get(root_key, []) or []
            for item in items:
                if isinstance(item, dict):
                    pairs.add((normalize(item.get("question")), normalize(item.get("answer"))))
    return pairs


def completed_blocks(course_root: Path) -> list[str]:
    completed = set()
    with (course_root / "roadmap.tsv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            try:
                order = int(row["Ordem"])
            except (KeyError, ValueError):
                continue
            if row.get("Status") == "Concluído":
                completed.add(order)
    blocks = []
    maximum = max(completed, default=0)
    for start in range(1, maximum + 1, 10):
        end = start + 9
        if all(order in completed for order in range(start, end + 1)):
            blocks.append(f"{start:03d}-{end:03d}")
    return blocks


def answer_table_has_explanations(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    section_start = text.find("## Gabarito do teste")
    if section_start == -1:
        return False
    lines = [line for line in text[section_start:].splitlines() if line.startswith("|")]
    if len(lines) < 3:
        return False
    headers = [cell.strip().casefold() for cell in lines[0].strip("|").split("|")]
    explanation = next(
        (index for index, value in enumerate(headers) if value in {"explicação", "observação"}),
        None,
    )
    if explanation is None:
        return False
    return all(
        len(cells := [cell.strip() for cell in line.strip("|").split("|")]) > explanation
        and bool(cells[explanation])
        for line in lines[2:]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida revisões cumulativas.")
    parser.add_argument("course", nargs="?", help="ID ou pasta do curso")
    parser.add_argument("--baseline", help="Arquivo de problemas legados conhecidos")
    args = parser.parse_args()

    course_root = resolve_course_root(args.course)
    issues = []
    expected = completed_blocks(course_root)
    for block in expected:
        review_dir = course_root / "reviews" / block
        if not review_dir.is_dir():
            issues.append(f"revisão ausente: {block}")
            continue
        for name in ("test.yaml", "answers.md"):
            path = review_dir / name
            if not path.exists() or path.stat().st_size == 0:
                issues.append(f"{block}: arquivo ausente ou vazio: {name}")
        test_path = review_dir / "test.yaml"
        if test_path.exists():
            try:
                data = yaml.safe_load(test_path.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError as exc:
                issues.append(f"{block}: test.yaml inválido: {exc}")
                data = {}
            questions = data.get("questions") if isinstance(data, dict) else None
            if not isinstance(questions, list) or not 20 <= len(questions) <= 30:
                issues.append(f"{block}: revisão deve conter 20-30 questões")
            positions = []
            originals = source_pairs(course_root, block)
            for index, question in enumerate(questions or [], start=1):
                if not isinstance(question, dict) or not question.get("question") or question.get("answer") is None:
                    issues.append(f"{block}: questão {index} incompleta")
                    continue
                options = question.get("options")
                pair = (normalize(question.get("question")), normalize(question.get("answer")))
                if pair in originals:
                    issues.append(f"{block}: questão {index} repete item de tópico")
                if options:
                    if not isinstance(options, list) or len(options) != 3:
                        issues.append(f"{block}: questão {index} deve ter 3 opções")
                        continue
                    try:
                        positions.append([str(value) for value in options].index(str(question["answer"])) + 1)
                    except ValueError:
                        issues.append(f"{block}: resposta da questão {index} não aparece nas opções")
            if len(positions) >= 3 and set(positions) != {1, 2, 3}:
                issues.append(f"{block}: respostas de múltipla escolha não usam as três posições")
        answers_path = review_dir / "answers.md"
        if answers_path.exists() and not answer_table_has_explanations(answers_path):
            issues.append(f"{block}: gabarito sem explicações completas")

    baseline = set()
    if args.baseline:
        baseline_path = Path(args.baseline)
        if not baseline_path.exists():
            raise SystemExit(f"Erro: baseline não encontrada: {baseline_path}")
        baseline = {
            line.strip()
            for line in baseline_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        }
    ignored = [item for item in issues if item in baseline]
    issues = [item for item in issues if item not in baseline]
    if ignored:
        print(f"({len(ignored)} problema(s) de revisão conhecidos ignorados pela baseline)")
    if issues:
        print(f"Review QA encontrou {len(issues)} problema(s):")
        for item in issues:
            print(f"- {item}")
        return 1
    print(f"Review QA OK: {len(expected)} bloco(s) concluído(s) verificado(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
