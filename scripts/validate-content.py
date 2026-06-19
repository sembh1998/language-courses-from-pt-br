#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import extract_story_text, load_course_config


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TOPICS_ROOT = REPO_ROOT / "courses" / "de-from-pt-br" / "topics"
REQUIRED_SOURCE_FILES = (
    "lesson.md",
    "vocabulary.yaml",
    "flashcards.yaml",
    "exercises.yaml",
    "test.yaml",
    "story.md",
    "answers.md",
)
YAML_SOURCE_FILES = (
    "vocabulary.yaml",
    "flashcards.yaml",
    "exercises.yaml",
    "test.yaml",
)
SCHEMA_FILES = {
    "vocabulary.yaml": "vocabulary.schema.yaml",
    "flashcards.yaml": "flashcards.schema.yaml",
    "exercises.yaml": "exercises.schema.yaml",
    "test.yaml": "test.schema.yaml",
    "content.json": "content.schema.json",
    "content.yaml": "content.schema.json",
}

TYPE_ALIASES = {
    "fill_in_the_blank": "fill_blank",
    "complete": "fill_blank",
    "complete lacuna": "fill_blank",
    "complete lacunas": "fill_blank",
    "múltipla escolha": "multiple_choice",
    "tradução": "translation",
    "traducao": "translation",
    "transformação": "transformation",
    "transformacao": "transformation",
    "sentence_transformation": "transformation",
    "transform": "transformation",
    "rewrite": "transformation",
    "replacement": "transformation",
    "error_correction": "correction",
    "correção": "correction",
    "categorization": "classification",
    "classify": "classification",
    "sorting": "classification",
    "case_choice": "classification",
    "short_production": "production",
    "produção curta": "production",
    "producao_curta": "production",
    "writing": "production",
    "identify": "identification",
    "reconhecimento": "identification",
    "word_order": "ordering",
    "order_sentence": "ordering",
    "sentence_building": "ordering",
    "sentence_completion": "fill_blank",
}

ENGLISH_MARKDOWN_LABELS = {
    "# Story:",
    "# Answers:",
    "Level:",
    "## Goal",
    "## Explanation",
    "## Examples",
    "## Common mistakes",
    "## Summary",
    "## German Story",
    "## Line-by-line translation",
    "## Vocabulary notes",
    "## Comprehension questions",
    "## Exercises answer key",
    "## Test answer key",
    "## Story questions",
    "| German | Translation | Note |",
    "| German | Translation |",
    "| ID | Answer | Note |",
    "| ID | Answer | Points |",
    "| Question | Answer |",
}

COMMAND_PREFIX_RE = re.compile(
    r"^(transforme|traduza|complete|corrija|ordene|responda)\b\s*:?\s*",
    flags=re.IGNORECASE,
)


def issue(issues: list[str], path: Path, message: str) -> None:
    try:
        display_path = path.relative_to(REPO_ROOT)
    except ValueError:
        display_path = path
    issues.append(f"{display_path}: {message}")


def baseline_keys(item: str) -> set[str]:
    """Return equivalent issue keys for pre/post multi-course baseline paths."""
    keys = {item}
    if item.startswith("courses/"):
        parts = item.split("/", 3)
        if len(parts) == 4:
            keys.add(f"{parts[2]}/{parts[3]}")
    return keys


def normalize_text(value: object) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = COMMAND_PREFIX_RE.sub("", text)
    text = text.replace("ß", "ss")
    text = re.sub(r"[_*`\"'“”.,!?;:()\[\]{}<>/\\|-]+", " ", text)
    return " ".join(text.split())


def looks_reused(left: object, right: object) -> bool:
    left_norm = normalize_text(left)
    right_norm = normalize_text(right)
    if not left_norm or not right_norm:
        return False
    if left_norm == right_norm and len(left_norm) >= 6:
        return True
    shorter, longer = sorted((left_norm, right_norm), key=len)
    return len(shorter) >= 12 and shorter in longer


def answers_equivalent(left: object, right: object) -> bool:
    left_norm = normalize_text(left)
    right_norm = normalize_text(right)
    if not left_norm or not right_norm:
        return False
    if left_norm == right_norm:
        return True
    shorter, longer = sorted((left_norm, right_norm), key=len)
    if len(shorter) < 4:
        return shorter in longer.split()
    return shorter in longer


def load_yaml(path: Path, issues: list[str]) -> object:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # noqa: BLE001 - validation should report parser details.
        issue(issues, path, f"YAML inválido: {exc}")
        return {}


def course_root_for(path: Path) -> Path | None:
    for candidate in (path, *path.parents):
        if (candidate / "course.yaml").exists():
            return candidate
    return None


def topic_dirs(paths: list[Path]) -> list[Path]:
    if not paths:
        paths = [DEFAULT_TOPICS_ROOT]

    found: set[Path] = set()
    topic_name = re.compile(r"^\d{3}-")
    for path in paths:
        path = path.resolve()
        if path.is_file():
            path = path.parent
        if path.is_dir() and topic_name.match(path.name):
            found.add(path)
            continue
        if path.is_dir():
            for candidate in path.rglob("*"):
                if candidate.is_dir() and topic_name.match(candidate.name):
                    found.add(candidate)

    return sorted(found)


def canonical_type(value: object, has_options: bool = False) -> str:
    if value is None:
        return "multiple_choice" if has_options else "short_answer"
    raw = str(value).strip()
    return TYPE_ALIASES.get(raw.casefold(), raw)


def normalized_for_schema(name: str, data: object) -> object:
    normalized = copy.deepcopy(data)
    if not isinstance(normalized, dict):
        return normalized
    if name == "exercises.yaml":
        for group in normalized.get("exercises", []) or []:
            if not isinstance(group, dict):
                continue
            items = group.get("items", []) or []
            group["type"] = canonical_type(
                group.get("type"),
                any(isinstance(item, dict) and item.get("options") for item in items),
            )
    elif name == "test.yaml":
        for question in normalized.get("questions", []) or []:
            if isinstance(question, dict):
                question["type"] = canonical_type(question.get("type"), bool(question.get("options")))
    return normalized


def schema_issues(path: Path, data: object, issues: list[str]) -> None:
    schema_name = SCHEMA_FILES.get(path.name)
    if not schema_name:
        return
    schema_path = REPO_ROOT / "schemas" / schema_name
    if schema_path.suffix == ".json":
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    else:
        schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    normalized = normalized_for_schema(path.name, data)
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        # Dependencies installed from requirements.txt perform full validation.
        # Keep the CLI useful in minimal environments with essential checks.
        if not isinstance(normalized, dict):
            issue(issues, path, "estrutura YAML deve ser um objeto")
            return
        for field in schema.get("required", []):
            if field not in normalized:
                issue(issues, path, f"campo obrigatório ausente: {field}")
        return

    validator = Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(normalized), key=lambda item: list(item.absolute_path)):
        location = ".".join(str(part) for part in error.absolute_path) or "<raiz>"
        issue(issues, path, f"schema em {location}: {error.message}")


def iter_exercise_items(exercises_data: object):
    if not isinstance(exercises_data, dict):
        return
    for group_index, group in enumerate(exercises_data.get("exercises", []) or [], start=1):
        if not isinstance(group, dict):
            continue
        for item_index, item in enumerate(group.get("items", []) or [], start=1):
            if isinstance(item, dict):
                yield str(item.get("id") or f"{group_index}.{item_index}"), item


def iter_test_questions(test_data: object):
    if not isinstance(test_data, dict):
        return
    for question_index, question in enumerate(test_data.get("questions", []) or [], start=1):
        if isinstance(question, dict):
            yield str(question_index), question


def check_reused_test_items(topic_dir: Path, issues: list[str], exercises_data: object, test_data: object) -> None:
    exercise_items = list(iter_exercise_items(exercises_data))
    for test_id, question in iter_test_questions(test_data):
        test_question = question.get("question", "")
        test_answer = question.get("answer", "")
        for exercise_id, item in exercise_items:
            same_question = looks_reused(test_question, item.get("question", ""))
            same_pair = same_question and looks_reused(test_answer, item.get("answer", ""))
            if same_question or same_pair:
                issue(
                    issues,
                    topic_dir / "test.yaml",
                    f"questão {test_id} parece repetir o exercício {exercise_id}",
                )
                break


def check_multiple_choice_distribution(path: Path, label: str, rows: list[tuple[str, dict]], issues: list[str]) -> None:
    positions: list[int] = []
    for item_id, item in rows:
        options = item.get("options")
        if not options:
            continue
        if not isinstance(options, list):
            issue(issues, path, f"{label} {item_id} tem `options` que não é lista")
            continue
        if len(options) != 3:
            issue(issues, path, f"{label} {item_id} tem {len(options)} opções; use 3 por padrão")
        answer = item.get("answer")
        try:
            position = [normalize_text(option) for option in options].index(normalize_text(answer)) + 1
        except ValueError:
            issue(issues, path, f"{label} {item_id} tem resposta que não aparece nas opções")
            continue
        positions.append(position)

    total = len(positions)
    if total < 3:
        return

    counts = {position: positions.count(position) for position in (1, 2, 3)}
    if counts[3] == 0:
        issue(issues, path, "nenhuma resposta correta está na posição 3")
    if total >= 4 and any(count == 0 for count in counts.values()):
        issue(issues, path, f"distribuição de respostas pouco variada: {counts}")
    if total >= 4 and max(counts.values()) > math.ceil(total * 0.7):
        issue(issues, path, f"respostas corretas concentradas demais: {counts}")


def check_multiple_choice(topic_dir: Path, issues: list[str], exercises_data: object, test_data: object) -> None:
    exercise_rows = [(item_id, item) for item_id, item in iter_exercise_items(exercises_data)]
    test_rows = [(item_id, item) for item_id, item in iter_test_questions(test_data)]
    check_multiple_choice_distribution(topic_dir / "exercises.yaml", "exercício", exercise_rows, issues)
    check_multiple_choice_distribution(topic_dir / "test.yaml", "questão", test_rows, issues)


def markdown_section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    next_heading = text.find("\n## ", start + len(heading))
    if next_heading == -1:
        return text[start:]
    return text[start:next_heading]


def split_markdown_row(line: str) -> list[str]:
    return [
        cell.replace(r"\|", "|").strip()
        for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))
    ]


def answer_rows(text: str, heading: str) -> dict[str, str]:
    section = markdown_section(text, heading)
    lines = [line for line in section.splitlines() if line.startswith("|")]
    rows = {}
    for line in lines[2:]:
        cells = split_markdown_row(line)
        if len(cells) >= 2:
            rows[cells[0]] = cells[1]
    return rows


def check_answer_consistency(
    topic_dir: Path,
    issues: list[str],
    exercises_data: object,
    test_data: object,
) -> None:
    path = topic_dir / "answers.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    exercise_answers = answer_rows(text, "## Gabarito dos exercícios")
    test_answers = answer_rows(text, "## Gabarito do teste")

    for item_id, item in iter_exercise_items(exercises_data):
        if item_id not in exercise_answers:
            issue(issues, path, f"gabarito ausente para exercício {item_id}")
        elif not answers_equivalent(item.get("answer"), exercise_answers[item_id]):
            issue(issues, path, f"resposta do exercício {item_id} diverge de exercises.yaml")

    for item_id, item in iter_test_questions(test_data):
        if item_id not in test_answers:
            issue(issues, path, f"gabarito ausente para questão {item_id}")
        elif not answers_equivalent(item.get("answer"), test_answers[item_id]):
            issue(issues, path, f"resposta da questão {item_id} diverge de test.yaml")


def check_answer_explanations(topic_dir: Path, issues: list[str]) -> None:
    path = topic_dir / "answers.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")

    for heading in ("## Gabarito dos exercícios", "## Gabarito do teste"):
        section = markdown_section(text, heading)
        if not section:
            issue(issues, path, f"seção ausente: {heading}")
            continue

        lines = [line for line in section.splitlines() if line.startswith("|")]
        if len(lines) < 2:
            issue(issues, path, f"{heading} não tem tabela de respostas")
            continue

        headers = split_markdown_row(lines[0])
        explanation_index = next(
            (index for index, header in enumerate(headers) if header.casefold() in {"explicação", "observação"}),
            None,
        )
        if explanation_index is None:
            issue(issues, path, f"{heading} não tem coluna de explicação")
            continue

        for line_number, line in enumerate(lines[2:], start=3):
            cells = split_markdown_row(line)
            if len(cells) <= explanation_index or not cells[explanation_index]:
                issue(issues, path, f"{heading}, linha de tabela {line_number}, explicação vazia")


def check_markdown_labels(topic_dir: Path, issues: list[str]) -> None:
    for name in ("lesson.md", "story.md", "answers.md"):
        path = topic_dir / name
        if not path.exists():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if stripped in ENGLISH_MARKDOWN_LABELS or any(stripped.startswith(prefix) for prefix in ("# Story:", "# Answers:")):
                issue(issues, path, f"rótulo em inglês na linha {line_number}: {stripped}")


def check_topic_metadata(topic_dir: Path, parsed_yaml: dict[str, object], issues: list[str]) -> None:
    course_root = course_root_for(topic_dir)
    if course_root is None:
        issue(issues, topic_dir, "não foi possível localizar course.yaml")
        return
    config = load_course_config(course_root)
    expected_level = topic_dir.parent.name.upper()

    for name, data in parsed_yaml.items():
        if not isinstance(data, dict):
            continue
        if data.get("level") and str(data["level"]).upper() != expected_level:
            issue(issues, topic_dir / name, f"nível {data['level']!r} difere da pasta {expected_level!r}")

    vocabulary = parsed_yaml.get("vocabulary.yaml")
    if isinstance(vocabulary, dict):
        target_field = config["target_word_field"]
        for index, word in enumerate(vocabulary.get("words", []) or [], start=1):
            if not isinstance(word, dict) or not str(word.get(target_field) or "").strip():
                issue(issues, topic_dir / "vocabulary.yaml", f"item {index} sem `{target_field}`")

    story_path = topic_dir / "story.md"
    if story_path.exists():
        story_text = story_path.read_text(encoding="utf-8")
        heading = config["story_heading"]
        if heading not in story_text:
            issue(issues, story_path, f"título obrigatório ausente: {heading}")
        elif not extract_story_text(story_path, heading):
            issue(issues, story_path, "seção da história não contém texto extraível para áudio")


def validate_topic(topic_dir: Path, issues: list[str]) -> None:
    parsed_yaml: dict[str, object] = {}
    for name in REQUIRED_SOURCE_FILES:
        path = topic_dir / name
        if not path.exists():
            issue(issues, path, "arquivo obrigatório ausente")
        elif path.stat().st_size == 0:
            issue(issues, path, "arquivo obrigatório vazio")

    for name in YAML_SOURCE_FILES:
        path = topic_dir / name
        if path.exists() and path.stat().st_size > 0:
            parsed_yaml[name] = load_yaml(path, issues)
            schema_issues(path, parsed_yaml[name], issues)

    content_paths = [path for path in (topic_dir / "content.json", topic_dir / "content.yaml") if path.exists()]
    if len(content_paths) > 1:
        issue(issues, topic_dir, "use apenas content.json ou content.yaml, não ambos")
    elif content_paths:
        content_path = content_paths[0]
        if content_path.suffix == ".json":
            try:
                content_data = json.loads(content_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                issue(issues, content_path, f"JSON inválido: {exc}")
                content_data = {}
        else:
            content_data = load_yaml(content_path, issues)
        schema_issues(content_path, content_data, issues)

    allowed_files = set(REQUIRED_SOURCE_FILES) | {"content.json", "content.yaml"}
    for path in topic_dir.iterdir():
        if path.is_file() and path.suffix in {".json", ".md", ".yaml"} and path.name not in allowed_files:
            issue(issues, path, "arquivo fonte inesperado na pasta do tópico")

    check_markdown_labels(topic_dir, issues)
    check_answer_explanations(topic_dir, issues)
    check_topic_metadata(topic_dir, parsed_yaml, issues)
    check_answer_consistency(
        topic_dir,
        issues,
        parsed_yaml.get("exercises.yaml", {}),
        parsed_yaml.get("test.yaml", {}),
    )
    check_reused_test_items(
        topic_dir,
        issues,
        parsed_yaml.get("exercises.yaml", {}),
        parsed_yaml.get("test.yaml", {}),
    )
    check_multiple_choice(
        topic_dir,
        issues,
        parsed_yaml.get("exercises.yaml", {}),
        parsed_yaml.get("test.yaml", {}),
    )


def main(argv: list[str]) -> int:
    baseline_path: Path | None = None
    paths: list[Path] = []
    args = iter(argv)
    for arg in args:
        if arg == "--baseline":
            try:
                baseline_path = Path(next(args))
            except StopIteration:
                print("Erro: --baseline requer um arquivo.", file=sys.stderr)
                return 2
        else:
            paths.append(Path(arg))

    if baseline_path and not baseline_path.exists():
        print(f"Erro: baseline não encontrada: {baseline_path}", file=sys.stderr)
        return 2

    issues: list[str] = []
    topics = topic_dirs(paths)

    if not topics:
        print("Nenhum tópico encontrado.", file=sys.stderr)
        return 2

    for topic_dir in topics:
        validate_topic(topic_dir, issues)

    if baseline_path:
        known = {
            line.strip()
            for line in baseline_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        }
        ignored = [item for item in issues if baseline_keys(item) & known]
        issues = [item for item in issues if not (baseline_keys(item) & known)]
        if ignored:
            print(f"({len(ignored)} problema(s) conhecidos ignorados pela baseline)")

    if issues:
        print(f"Content QA encontrou {len(issues)} problema(s):")
        for item in issues:
            print(f"- {item}")
        return 1

    print(f"Content QA OK: {len(topics)} tópico(s) verificado(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
