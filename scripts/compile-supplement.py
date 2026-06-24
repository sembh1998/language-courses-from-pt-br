#!/usr/bin/env python3
"""Compile optional topic supplement JSON into separate learner-facing files.

Supplements live under a topic's ``supplements/`` directory and never overwrite
the normal topic outputs produced from content.json.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_course_config, resolve_course_root, resolve_topic_dirs


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "supplement.schema.json"


def fail(message: str) -> None:
    raise SystemExit(f"Erro: {message}")


def validate_source(data: object, source_path: Path) -> dict:
    if not isinstance(data, dict):
        fail(f"{source_path} deve conter um objeto JSON")

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        missing = [field for field in schema["required"] if field not in data]
        if missing:
            fail(f"{source_path} não contém: {', '.join(missing)}")
        if not any(key in data for key in ("exercises", "test", "stories")):
            fail(f"{source_path} deve conter exercises, test ou stories")
        return data

    errors = sorted(
        Draft202012Validator(schema).iter_errors(data),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        lines = []
        for error in errors:
            location = ".".join(str(part) for part in error.absolute_path) or "<raiz>"
            lines.append(f"{location}: {error.message}")
        fail(f"{source_path} não segue o schema:\n- " + "\n- ".join(lines))
    return data


def load_source(source_path: Path) -> dict:
    try:
        return validate_source(json.loads(source_path.read_text(encoding="utf-8")), source_path)
    except json.JSONDecodeError as exc:
        fail(f"JSON inválido em {source_path}: {exc}")


def yaml_text(data: object) -> str:
    return yaml.safe_dump(
        data,
        allow_unicode=True,
        sort_keys=False,
        width=120,
        default_flow_style=False,
    )


def table_cell(value: object) -> str:
    return str(value).replace("|", r"\|").replace("\n", "<br>")


def safe_name(source_path: Path) -> str:
    name = source_path.stem
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", name):
        fail(f"nome de suplemento inválido: {source_path.name}")
    return name


def balanced_options(item: dict, multiple_choice_index: int) -> list[str]:
    answer = str(item["answer"])
    distractors = [str(value) for value in item.get("distractors", [])]
    if len(distractors) != 2:
        fail(f"questão de múltipla escolha requer exatamente 2 distractors: {item['question']}")
    values = [answer, *distractors]
    if len({value.casefold().strip() for value in values}) != 3:
        fail(f"alternativas duplicadas: {item['question']}")
    correct_position = multiple_choice_index % 3
    options = copy.copy(distractors)
    options.insert(correct_position, answer)
    return options


def compile_assessment(data: dict, source_key: str) -> tuple[str, list[dict]]:
    multiple_choice_index = 0
    answer_rows: list[dict] = []

    if source_key == "exercises":
        groups = []
        for group_index, source_group in enumerate(data.get("exercises", []), start=1):
            group = {"type": source_group["type"]}
            if source_group.get("title"):
                group["title"] = source_group["title"]
            group["instruction"] = source_group["instruction"]
            items = []
            for item_index, source_item in enumerate(source_group["items"], start=1):
                item = {
                    "question": source_item["question"],
                    "answer": source_item["answer"],
                }
                if source_item["type"] == "multiple_choice":
                    item["options"] = balanced_options(source_item, multiple_choice_index)
                    multiple_choice_index += 1
                items.append(item)
                answer_rows.append(
                    {
                        "id": f"{group_index}.{item_index}",
                        "answer": source_item["answer"],
                        "explanation": source_item["explanation"],
                    }
                )
            group["items"] = items
            groups.append(group)
        output = {"topic": data["topic"], "level": data["level"], "exercises": groups}
    else:
        questions = []
        for question_index, source_item in enumerate(data.get("test", []), start=1):
            item = {
                "type": source_item["type"],
                "question": source_item["question"],
                "answer": source_item["answer"],
            }
            if source_item["type"] == "multiple_choice":
                item["options"] = balanced_options(source_item, multiple_choice_index)
                multiple_choice_index += 1
            questions.append(item)
            answer_rows.append(
                {
                    "id": str(question_index),
                    "answer": source_item["answer"],
                    "explanation": source_item["explanation"],
                    "points": source_item.get("points", 1),
                }
            )
        output = {"topic": data["topic"], "level": data["level"], "questions": questions}

    return yaml_text(output), answer_rows


def compile_stories(data: dict, config: dict[str, str]) -> tuple[str, list[dict], list[dict]]:
    target_label = config["target_language_pt"].capitalize()
    lines = [
        f"# Histórias extras: {data['topic']}",
        "",
        f"Nível: {data['level']}",
        "",
        config["story_heading"],
        "",
    ]
    sentence_pairs = []
    notes = []
    question_rows = []
    practice_rows = []

    for story_index, story in enumerate(data.get("stories", []), start=1):
        lines.extend([f"### {story['title']}", ""])
        for section in story["sections"]:
            if section.get("heading"):
                lines.extend([f"#### {section['heading']}", ""])
            lines.append(" ".join(sentence["target"].strip() for sentence in section["sentences"]))
            lines.append("")
            for sentence in section["sentences"]:
                sentence_pairs.append({"story": story["title"], **sentence})
        for note in story["vocabulary_notes"]:
            notes.append({"story": story["title"], **note})
        for question_index, item in enumerate(story["questions"], start=1):
            question_rows.append({"id": f"{story_index}.{question_index}", **item})
        for practice_index, item in enumerate(story.get("practice", []), start=1):
            practice_rows.append({"id": f"{story_index}.{practice_index}", **item})

    lines.extend(
        [
            "## Tradução linha por linha",
            "",
            f"| História | {target_label} | Tradução |",
            "|---|---|---|",
        ]
    )
    for sentence in sentence_pairs:
        lines.append(
            f"| {table_cell(sentence['story'])} | {table_cell(sentence['target'])} | "
            f"{table_cell(sentence['translation'])} |"
        )

    lines.extend(["", "## Notas de vocabulário", ""])
    if notes:
        lines.extend(f"- {note['target']} = {note['note']} ({note['story']})" for note in notes)
    else:
        lines.append("- Sem notas adicionais para este texto.")

    lines.extend(["", "## Perguntas de compreensão", ""])
    lines.extend(f"{row['id']}. {row['question']}" for row in question_rows)
    if practice_rows:
        lines.extend(["", "## Prática com a história", ""])
        lines.extend(f"{row['id']}. {row['question']}" for row in practice_rows)
    lines.append("")
    return "\n".join(lines), question_rows, practice_rows


def compile_answers(data: dict, exercise_rows: list[dict], test_rows: list[dict], question_rows: list[dict], practice_rows: list[dict]) -> str:
    lines = [
        f"# Respostas extras: {data['topic']}",
        "",
        f"Nível: {data['level']}",
        "",
    ]
    if exercise_rows:
        lines.extend(["## Gabarito dos exercícios extras", "", "| ID | Resposta | Explicação |", "|---|---|---|"])
        lines.extend(f"| {row['id']} | {table_cell(row['answer'])} | {table_cell(row['explanation'])} |" for row in exercise_rows)
        lines.append("")
    if test_rows:
        lines.extend(["## Gabarito do teste extra", "", "| ID | Resposta | Explicação | Pontos |", "|---|---|---|---|"])
        lines.extend(
            f"| {row['id']} | {table_cell(row['answer'])} | {table_cell(row['explanation'])} | {row['points']} |"
            for row in test_rows
        )
        lines.append("")
    if question_rows:
        lines.extend(["## Respostas das perguntas de compreensão", "", "| ID | Resposta | Observação |", "|---|---|---|"])
        lines.extend(
            f"| {row['id']} | {table_cell(row['answer'])} | "
            f"{table_cell(row.get('explanation', 'Resposta baseada na história.'))} |"
            for row in question_rows
        )
        lines.append("")
    if practice_rows:
        lines.extend(["## Respostas da prática com a história", "", "| ID | Resposta | Explicação |", "|---|---|---|"])
        lines.extend(
            f"| {row['id']} | {table_cell(row['answer'])} | "
            f"{table_cell(row.get('explanation', 'Aplicação do conteúdo-alvo.'))} |"
            for row in practice_rows
        )
        lines.append("")
    return "\n".join(lines)


def compile_outputs(source_path: Path, data: dict, config: dict[str, str]) -> dict[str, str]:
    name = safe_name(source_path)
    outputs: dict[str, str] = {}
    exercise_rows: list[dict] = []
    test_rows: list[dict] = []
    question_rows: list[dict] = []
    practice_rows: list[dict] = []

    if data.get("exercises"):
        outputs[f"{name}-exercises.yaml"], exercise_rows = compile_assessment(data, "exercises")
    if data.get("test"):
        outputs[f"{name}-test.yaml"], test_rows = compile_assessment(data, "test")
    if data.get("stories"):
        outputs[f"{name}-story.md"], question_rows, practice_rows = compile_stories(data, config)
    outputs[f"{name}-answers.md"] = compile_answers(data, exercise_rows, test_rows, question_rows, practice_rows)
    return outputs


def source_paths_for(topic_dir: Path, name: str | None) -> list[Path]:
    supplements_dir = topic_dir / "supplements"
    if name:
        source_path = supplements_dir / f"{name}.json"
        if not source_path.exists():
            fail(f"arquivo ausente: {source_path}")
        return [source_path]
    if not supplements_dir.exists():
        return []
    return sorted(path for path in supplements_dir.glob("*.json") if path.is_file())


def all_topic_dirs_with_supplements(course_root: Path) -> list[Path]:
    return sorted({path.parent.parent for path in (course_root / "topics").rglob("supplements/*.json")})


def main() -> int:
    parser = argparse.ArgumentParser(description="Compila suplementos opcionais de tópicos.")
    parser.add_argument("topic", nargs="?", help="Número ou pasta do tópico; vazio = todos com supplements/*.json")
    parser.add_argument("name", nargs="?", help="Nome do suplemento sem .json; vazio = todos do tópico")
    parser.add_argument("--course", default=None, help="ID ou pasta do curso")
    parser.add_argument("--check", action="store_true", help="Não escreve; falha se os arquivos compilados divergirem")
    args = parser.parse_args()

    course_root = resolve_course_root(args.course)
    config = load_course_config(course_root)
    if args.topic:
        topic_dirs = resolve_topic_dirs([args.topic], course_root)
    else:
        topic_dirs = all_topic_dirs_with_supplements(course_root)
    if not topic_dirs:
        fail("nenhum suplemento encontrado")

    changed = []
    compiled = 0
    for topic_dir in topic_dirs:
        source_paths = source_paths_for(topic_dir, args.name)
        for source_path in source_paths:
            data = load_source(source_path)
            outputs = compile_outputs(source_path, data, config)
            compiled += 1
            for file_name, expected in outputs.items():
                path = source_path.parent / file_name
                current = path.read_text(encoding="utf-8") if path.exists() else None
                if current == expected:
                    continue
                changed.append(path)
                if not args.check:
                    path.write_text(expected, encoding="utf-8")

    if compiled == 0:
        fail("nenhum supplement/*.json encontrado")
    if changed and args.check:
        print("Suplementos compilados estão desatualizados:")
        for path in changed:
            print(f"- {path.relative_to(REPO_ROOT)}")
        return 1
    if changed:
        print(f"Compilados {len(changed)} arquivo(s) de {compiled} suplemento(s).")
    else:
        print(f"Suplementos já compilados: {compiled} suplemento(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
