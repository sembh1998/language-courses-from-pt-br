#!/usr/bin/env python3
"""Compile one structured content.json into the seven topic source files.

The model writes semantic content once. This compiler owns deterministic
formatting, IDs, points, answer tables, story duplication, flashcard derivation,
and multiple-choice answer positioning. Legacy content.yaml remains supported.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_course_config, resolve_course_root, resolve_topic_dirs


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "content.schema.json"
OUTPUT_FILES = (
    "lesson.md",
    "vocabulary.yaml",
    "flashcards.yaml",
    "exercises.yaml",
    "test.yaml",
    "story.md",
    "answers.md",
)


def fail(message: str) -> None:
    raise SystemExit(f"Erro: {message}")


def validate_source(data: object, source_path: Path) -> dict:
    if not isinstance(data, dict):
        fail(f"{source_path} deve conter um objeto YAML")

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        required = schema["required"]
        missing = [field for field in required if field not in data]
        if missing:
            fail(f"{source_path} não contém: {', '.join(missing)}")
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


def source_path_for(topic_dir: Path) -> Path:
    json_path = topic_dir / "content.json"
    yaml_path = topic_dir / "content.yaml"
    if json_path.exists() and yaml_path.exists():
        fail(f"use apenas content.json ou content.yaml em {topic_dir}, não ambos")
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


def compile_lesson(data: dict, config: dict[str, str]) -> str:
    lesson = data["lesson"]
    target_label = config["target_language_pt"].capitalize()
    lines = [
        f"# {data['topic']}",
        "",
        f"Nível: {data['level']}",
        "",
        "## Objetivo",
        "",
        lesson["objective"].strip(),
        "",
        "## Explicação",
        "",
        lesson["explanation"].strip(),
        "",
        "## Exemplos",
        "",
        f"| {target_label} | Tradução | Observação |",
        "|---|---|---|",
    ]
    for example in lesson["examples"]:
        lines.append(
            f"| {table_cell(example['target'])} | {table_cell(example['translation'])} | "
            f"{table_cell(example.get('note', ''))} |"
        )
    lines.extend(["", "## Erros comuns", ""])
    lines.extend(f"- {mistake.strip()}" for mistake in lesson["common_mistakes"])
    if lesson.get("guided_practice"):
        lines.extend(["", "## Prática guiada", "", lesson["guided_practice"].strip()])
    lines.extend(["", "## Resumo", "", lesson["summary"].strip(), ""])
    return "\n".join(lines)


def compile_vocabulary(data: dict, config: dict[str, str]) -> str:
    target_field = config["target_word_field"]
    words = []
    for entry in data["vocabulary"]:
        word = {
            target_field: entry["target"],
            "translation": entry["translation"],
        }
        for key in ("type", "gender", "plural"):
            if key in entry:
                word[key] = entry[key]
        word["example"] = entry["example"]
        word["example_translation"] = entry["example_translation"]
        if entry.get("note"):
            word["note"] = entry["note"]
        words.append(word)
    return yaml_text({"topic": data["topic"], "level": data["level"], "words": words})


def compile_flashcards(data: dict) -> str:
    cards = []
    for entry in data["vocabulary"]:
        if entry.get("flashcard", True):
            cards.append(
                {
                    "front": entry.get("flashcard_front") or entry["target"],
                    "back": entry.get("flashcard_back") or entry["translation"],
                    "example": entry["example"],
                    "example_translation": entry["example_translation"],
                }
            )
    cards.extend(data.get("flashcards", []))
    output = {"topic": data["topic"], "level": data["level"], "cards": cards}
    if not cards:
        output["note"] = data.get("flashcards_note") or "Flashcards omitidos intencionalmente para este tópico."
    return yaml_text(output)


def compile_assessment(data: dict, source_key: str) -> tuple[str, list[dict]]:
    multiple_choice_index = 0
    answer_rows: list[dict] = []

    if source_key == "exercises":
        groups = []
        for group_index, source_group in enumerate(data["exercises"], start=1):
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
        for question_index, source_item in enumerate(data["test"], start=1):
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


def compile_story(data: dict, config: dict[str, str]) -> str:
    story = data["story"]
    target_label = config["target_language_pt"].capitalize()
    lines = [
        f"# História: {data['topic']}",
        "",
        f"Nível: {data['level']}",
        "",
        config["story_heading"],
        "",
    ]
    sentence_pairs = []
    for section in story["sections"]:
        if section.get("heading"):
            lines.extend([f"### {section['heading']}", ""])
        lines.append(" ".join(sentence["target"].strip() for sentence in section["sentences"]))
        lines.append("")
        sentence_pairs.extend(section["sentences"])

    lines.extend(
        [
            "## Tradução linha por linha",
            "",
            f"| {target_label} | Tradução |",
            "|---|---|",
        ]
    )
    for sentence in sentence_pairs:
        lines.append(f"| {table_cell(sentence['target'])} | {table_cell(sentence['translation'])} |")

    lines.extend(["", "## Notas de vocabulário", ""])
    if story["vocabulary_notes"]:
        lines.extend(
            f"- {note['target']} = {note['note']}"
            for note in story["vocabulary_notes"]
        )
    else:
        lines.append("- Sem notas adicionais para este texto.")

    lines.extend(["", "## Perguntas de compreensão", ""])
    lines.extend(
        f"{index}. {item['question']}"
        for index, item in enumerate(story["questions"], start=1)
    )
    if story.get("practice"):
        lines.extend(["", "## Prática com a história", ""])
        lines.extend(
            f"{index}. {item['question']}"
            for index, item in enumerate(story["practice"], start=1)
        )
    lines.append("")
    return "\n".join(lines)


def compile_answers(
    data: dict,
    exercise_rows: list[dict],
    test_rows: list[dict],
) -> str:
    lines = [
        f"# Respostas: {data['topic']}",
        "",
        f"Nível: {data['level']}",
        "",
        "## Gabarito dos exercícios",
        "",
        "| ID | Resposta | Explicação |",
        "|---|---|---|",
    ]
    lines.extend(
        f"| {row['id']} | {table_cell(row['answer'])} | {table_cell(row['explanation'])} |"
        for row in exercise_rows
    )
    lines.extend(
        [
            "",
            "## Gabarito do teste",
            "",
            "| ID | Resposta | Explicação | Pontos |",
            "|---|---|---|---|",
        ]
    )
    lines.extend(
        f"| {row['id']} | {table_cell(row['answer'])} | {table_cell(row['explanation'])} | {row['points']} |"
        for row in test_rows
    )

    lines.extend(
        [
            "",
            "## Respostas das perguntas de compreensão",
            "",
            "| Pergunta | Resposta | Observação |",
            "|---|---|---|",
        ]
    )
    for item in data["story"]["questions"]:
        lines.append(
            f"| {table_cell(item['question'])} | {table_cell(item['answer'])} | "
            f"{table_cell(item.get('explanation', 'Resposta baseada na história.'))} |"
        )

    if data["story"].get("practice"):
        lines.extend(
            [
                "",
                "## Respostas da prática com a história",
                "",
                "| ID | Resposta | Explicação |",
                "|---|---|---|",
            ]
        )
        for index, item in enumerate(data["story"]["practice"], start=1):
            lines.append(
                f"| {index} | {table_cell(item['answer'])} | "
                f"{table_cell(item.get('explanation', 'Aplicação do conteúdo-alvo.'))} |"
            )
    lines.append("")
    return "\n".join(lines)


def compile_outputs(data: dict, config: dict[str, str]) -> dict[str, str]:
    exercises, exercise_rows = compile_assessment(data, "exercises")
    test, test_rows = compile_assessment(data, "test")
    return {
        "lesson.md": compile_lesson(data, config),
        "vocabulary.yaml": compile_vocabulary(data, config),
        "flashcards.yaml": compile_flashcards(data),
        "exercises.yaml": exercises,
        "test.yaml": test,
        "story.md": compile_story(data, config),
        "answers.md": compile_answers(data, exercise_rows, test_rows),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compila content.json para os sete arquivos de tópico.")
    parser.add_argument("topics", nargs="*", help="Números ou pastas de tópicos; vazio = tópicos estruturados")
    parser.add_argument("--course", default=None, help="ID ou pasta do curso")
    parser.add_argument("--check", action="store_true", help="Não escreve; falha se os arquivos compilados divergirem")
    args = parser.parse_args()

    course_root = resolve_course_root(args.course)
    config = load_course_config(course_root)
    if args.topics:
        topic_dirs = resolve_topic_dirs(args.topics, course_root)
    else:
        topic_dirs = sorted(
            {
                path.parent
                for pattern in ("content.json", "content.yaml")
                for path in (course_root / "topics").rglob(pattern)
            }
        )
    if not topic_dirs:
        fail("nenhum content.json ou content.yaml encontrado")

    changed = []
    for topic_dir in topic_dirs:
        source_path = source_path_for(topic_dir)
        source_data = load_source(source_path)
        data = validate_source(source_data, source_path)
        outputs = compile_outputs(data, config)
        for name in OUTPUT_FILES:
            path = topic_dir / name
            expected = outputs[name]
            current = path.read_text(encoding="utf-8") if path.exists() else None
            if current == expected:
                continue
            changed.append(path)
            if not args.check:
                path.write_text(expected, encoding="utf-8")

    if changed and args.check:
        print("Conteúdo compilado está desatualizado:")
        for path in changed:
            print(f"- {path.relative_to(REPO_ROOT)}")
        return 1
    if changed:
        print(f"Compilados {len(changed)} arquivo(s) em {len(topic_dirs)} tópico(s).")
    else:
        print(f"Conteúdo já compilado: {len(topic_dirs)} tópico(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
