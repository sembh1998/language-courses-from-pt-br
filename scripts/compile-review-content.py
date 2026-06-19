#!/usr/bin/env python3
"""Compile review.json into review test.yaml and answers.md.

Legacy review.yaml remains supported.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import resolve_course_root


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "review-content.schema.json"


def fail(message: str) -> None:
    raise SystemExit(f"Erro: {message}")


def validate(data: object, path: Path) -> dict:
    if not isinstance(data, dict):
        fail(f"{path} deve conter um objeto YAML")
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        missing = [key for key in ("topic", "level", "questions") if key not in data]
        if missing:
            fail(f"{path} não contém: {', '.join(missing)}")
        return data
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda item: list(item.absolute_path))
    if errors:
        details = []
        for error in errors:
            location = ".".join(str(part) for part in error.absolute_path) or "<raiz>"
            details.append(f"{location}: {error.message}")
        fail(f"{path} não segue o schema:\n- " + "\n- ".join(details))
    return data


def source_path_for(review_dir: Path) -> Path:
    json_path = review_dir / "review.json"
    yaml_path = review_dir / "review.yaml"
    if json_path.exists() and yaml_path.exists():
        fail(f"use apenas review.json ou review.yaml em {review_dir}, não ambos")
    if json_path.exists():
        return json_path
    if yaml_path.exists():
        return yaml_path
    fail(f"arquivo ausente: {json_path}")


def load_source(source_path: Path) -> object:
    try:
        if source_path.suffix == ".json":
            return json.loads(source_path.read_text(encoding="utf-8"))
        return yaml.safe_load(source_path.read_text(encoding="utf-8")) or {}
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        fail(f"{source_path.suffix[1:].upper()} inválido em {source_path}: {exc}")


def options_for(item: dict, index: int) -> list[str]:
    answer = str(item["answer"])
    distractors = [str(value) for value in item.get("distractors", [])]
    if len(distractors) != 2:
        fail(f"múltipla escolha requer dois distractors: {item['question']}")
    if len({answer.casefold(), *(value.casefold() for value in distractors)}) != 3:
        fail(f"alternativas duplicadas: {item['question']}")
    options = copy.copy(distractors)
    options.insert(index % 3, answer)
    return options


def table_cell(value: object) -> str:
    return str(value).replace("|", r"\|").replace("\n", "<br>")


def compile_review(data: dict) -> tuple[str, str]:
    questions = []
    answer_rows = []
    multiple_choice_index = 0
    for index, source in enumerate(data["questions"], start=1):
        question = {
            "id": index,
            "type": source["type"],
            "question": source["question"],
            "answer": source["answer"],
        }
        if source["type"] == "multiple_choice":
            question["options"] = options_for(source, multiple_choice_index)
            multiple_choice_index += 1
        questions.append(question)
        answer_rows.append(
            (
                index,
                source["answer"],
                source["explanation"],
                source.get("points", 1),
            )
        )

    test_text = yaml.safe_dump(
        {"topic": data["topic"], "level": data["level"], "questions": questions},
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )
    lines = [
        f"# {data['topic']}: respostas",
        "",
        f"Nível: {data['level']}",
        "",
        "## Gabarito do teste",
        "",
        "| ID | Resposta | Explicação | Pontos |",
        "|---|---|---|---|",
    ]
    lines.extend(
        f"| {index} | {table_cell(answer)} | {table_cell(explanation)} | {points} |"
        for index, answer, explanation, points in answer_rows
    )
    lines.append("")
    return test_text, "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compila review.json para teste e gabarito.")
    parser.add_argument("reviews", nargs="*", help="Faixas 001-010 ou pastas; vazio = todas estruturadas")
    parser.add_argument("--course", default=None, help="ID ou pasta do curso")
    parser.add_argument("--check", action="store_true", help="Falha quando saídas estão desatualizadas")
    args = parser.parse_args()

    course_root = resolve_course_root(args.course)
    if args.reviews:
        review_dirs = []
        for value in args.reviews:
            path = course_root / "reviews" / value if value.replace("-", "").isdigit() else Path(value)
            if not path.is_dir():
                fail(f"pasta de revisão não encontrada: {path}")
            review_dirs.append(path.resolve())
    else:
        review_dirs = sorted(
            {
                path.parent
                for pattern in ("review.json", "review.yaml")
                for path in (course_root / "reviews").rglob(pattern)
            }
        )
    if not review_dirs:
        fail("nenhum review.json ou review.yaml encontrado")

    changed = []
    for review_dir in review_dirs:
        source_path = source_path_for(review_dir)
        raw = load_source(source_path)
        data = validate(raw, source_path)
        test_text, answers_text = compile_review(data)
        for name, expected in (("test.yaml", test_text), ("answers.md", answers_text)):
            path = review_dir / name
            current = path.read_text(encoding="utf-8") if path.exists() else None
            if current == expected:
                continue
            changed.append(path)
            if not args.check:
                path.write_text(expected, encoding="utf-8")

    if changed and args.check:
        print("Revisões compiladas estão desatualizadas:")
        for path in changed:
            print(f"- {path.relative_to(REPO_ROOT)}")
        return 1
    print(
        f"Revisões {'compiladas' if changed else 'já compiladas'}: "
        f"{len(review_dirs)} faixa(s), {len(changed)} arquivo(s) alterado(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
