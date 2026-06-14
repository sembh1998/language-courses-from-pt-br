#!/usr/bin/env python3
"""Shared helpers for course/topic resolution and audio file naming."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
COURSES_ROOT = REPO_ROOT / "courses"
DEFAULT_COURSE_ROOT = COURSES_ROOT / "de-from-pt-br"

VOICES_DIR = REPO_ROOT / ".cache" / "piper-voices"


def resolve_course_root(course: str | Path | None = None) -> Path:
    """Resolve a course id/path to its root directory."""
    if course is None:
        return DEFAULT_COURSE_ROOT

    path = Path(course)
    if path.is_absolute() and path.is_dir():
        return path.resolve()
    if path.is_dir():
        return path.resolve()
    candidate = COURSES_ROOT / str(course)
    if candidate.is_dir():
        return candidate.resolve()
    raise SystemExit(f"Erro: curso não encontrado: {course}")


def load_course_config(course_root: Path) -> dict[str, str]:
    """Load course.yaml with sensible defaults for the German course."""
    config_path = course_root / "course.yaml"
    defaults = {
        "id": course_root.name,
        "target_language_pt": "alemão",
        "target_voice": "de_DE-karlsson-low",
        "source_voice": "pt_BR-cadu-medium",
        "anki_deck_name": "Alemão",
        "anki_model_name": "Alemão PT-BR (com áudio)",
        "anki_output": "alemao.apkg",
        "story_heading": "## História em alemão",
        "target_word_field": "german",
    }
    if not config_path.exists():
        return defaults
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    defaults.update({key: str(value) for key, value in data.items() if value is not None})
    return defaults


def topics_root(course_root: Path) -> Path:
    return course_root / "topics"


def audio_root(course_root: Path) -> Path:
    return course_root / "output" / "audio"


def exports_root(course_root: Path) -> Path:
    return course_root / "output" / "exports"


def resolve_topic_dirs(args: list[str], course_root: Path | None = None) -> list[Path]:
    """Resolve CLI args (topic numbers or folder paths) to topic directories.

    With no args, returns every topic folder containing a lesson.md.
    """
    course_root = course_root or DEFAULT_COURSE_ROOT
    root = topics_root(course_root)

    if not args:
        return sorted(
            lesson.parent for lesson in root.rglob("lesson.md")
        )

    found: list[Path] = []
    for arg in args:
        if re.fullmatch(r"\d+", arg):
            order = f"{int(arg):03d}"
            matches = sorted(root.glob(f"*/{order}-*"))
            if not matches:
                raise SystemExit(f"Erro: nenhum tópico encontrado para a ordem {arg}.")
            if len(matches) > 1:
                listing = "\n  ".join(str(m) for m in matches)
                raise SystemExit(f"Erro: múltiplos tópicos para a ordem {arg}:\n  {listing}")
            found.append(matches[0])
        else:
            path = Path(arg).resolve()
            if not path.is_dir():
                raise SystemExit(f"Erro: pasta de tópico não encontrada: {arg}")
            found.append(path)
    return found


def audio_filename(text: str, voice: str, extension: str = "wav") -> str:
    """Deterministic audio file name for a snippet of spoken text.

    Both generate-audio.py and export-anki.py use this so exported decks
    reference the exact files produced by the TTS step.
    """
    digest = hashlib.sha1(f"{voice}|{text}".encode("utf-8")).hexdigest()[:16]
    return f"{digest}.{extension}"


def topic_audio_dir(topic_dir: Path, course_root: Path | None = None) -> Path:
    if course_root is None:
        try:
            course_root = next(parent for parent in topic_dir.resolve().parents if (parent / "course.yaml").exists())
        except StopIteration:
            course_root = DEFAULT_COURSE_ROOT
    return audio_root(course_root) / topic_dir.name
