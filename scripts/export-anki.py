#!/usr/bin/env python3
"""Export flashcards.yaml files to an Anki deck (.apkg) with optional audio.

Builds one subdeck per topic from the selected course.
Each note creates two cards: target language -> PT and PT -> target language.
If scripts/generate-audio.py already produced clips under
<course>/output/audio/<topic>/cards/, they are embedded in the deck automatically.

Usage:
  .venv/bin/python scripts/export-anki.py                 # all German topics, nested by level/topic
  .venv/bin/python scripts/export-anki.py --course it-from-pt-br 22
  .venv/bin/python scripts/export-anki.py --course it-from-pt-br 22 104
  .venv/bin/python scripts/export-anki.py --output meu-deck.apkg 99 100 101
  .venv/bin/python scripts/export-anki.py --csv           # also write CSVs
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (
    audio_filename,
    exports_root,
    load_course_config,
    resolve_course_root,
    resolve_topic_dirs,
    topic_audio_dir,
)

def stable_id(name: str) -> int:
    return int(hashlib.sha1(name.encode("utf-8")).hexdigest()[:10], 16)


def build_model(model_name: str, target_language_pt: str):
    import genanki

    target_label = target_language_pt.capitalize()
    css = """
.card { font-family: sans-serif; font-size: 24px; text-align: center; color: #222; background: #fdfdfb; }
.example { font-size: 18px; color: #555; margin-top: 14px; }
.translation { font-size: 16px; color: #888; font-style: italic; }
"""
    return genanki.Model(
        stable_id(f"model:{model_name}"),
        model_name,
        fields=[
            {"name": "Front"},
            {"name": "Back"},
            {"name": "Example"},
            {"name": "ExampleTranslation"},
            {"name": "FrontAudio"},
            {"name": "ExampleAudio"},
        ],
        templates=[
            {
                "name": f"{target_label} → PT",
                "qfmt": "{{Front}}<br>{{FrontAudio}}",
                "afmt": (
                    "{{FrontSide}}<hr id=answer>{{Back}}"
                    '<div class="example">{{Example}} {{ExampleAudio}}</div>'
                    '<div class="translation">{{ExampleTranslation}}</div>'
                ),
            },
            {
                "name": f"PT → {target_label}",
                "qfmt": "{{Back}}",
                "afmt": (
                    "{{FrontSide}}<hr id=answer>{{Front}} {{FrontAudio}}"
                    '<div class="example">{{Example}} {{ExampleAudio}}</div>'
                    '<div class="translation">{{ExampleTranslation}}</div>'
                ),
            },
        ],
        css=css,
    )


def find_audio(topic_dir: Path, course_root: Path, text: str, target_voice: str) -> Path | None:
    base = topic_audio_dir(topic_dir, course_root) / "cards"
    for extension in ("mp3", "wav"):
        candidate = base / audio_filename(text, target_voice, extension)
        if candidate.exists():
            return candidate
    return None


def deck_name_for(topic_dir: Path, deck_root_name: str, selected_topics: bool) -> str:
    level = topic_dir.parent.name.upper()
    title = topic_dir.name.replace("-", " ")
    if selected_topics:
        return f"{deck_root_name} - {level} - {title}"
    return f"{deck_root_name}::{level}::{title}"


def load_cards(topic_dir: Path) -> list[dict]:
    path = topic_dir / "flashcards.yaml"
    if not path.exists():
        return []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # noqa: BLE001
        print(f"Aviso: YAML inválido ignorado: {path} ({exc})")
        return []
    cards = data.get("cards") or []
    return [card for card in cards if isinstance(card, dict) and card.get("front")]


def export_csv(topic_dir: Path, out_root: Path, cards: list[dict]) -> Path:
    out_dir = out_root / "anki-csv"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{topic_dir.name}.csv"
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter=";")
        for card in cards:
            writer.writerow(
                [
                    card.get("front", ""),
                    card.get("back", ""),
                    card.get("example", ""),
                    card.get("example_translation", ""),
                ]
            )
    return out_path


def default_output_path(out_root: Path, config: dict[str, str], topic_dirs: list[Path], selected_topics: bool) -> Path:
    if not selected_topics:
        return out_root / config["anki_output"]

    if len(topic_dirs) == 1:
        return out_root / "topics" / f"{topic_dirs[0].name}.apkg"

    output_stem = Path(config["anki_output"]).stem
    topic_ids = "-".join(topic.name.split("-", 1)[0] for topic in topic_dirs)
    return out_root / "selected" / f"{output_stem}-{topic_ids}.apkg"


def main() -> int:
    parser = argparse.ArgumentParser(description="Exporta flashcards para Anki.")
    parser.add_argument("topics", nargs="*", help="Números de ordem ou pastas de tópicos (vazio = todos)")
    parser.add_argument("--course", default=None, help="ID ou pasta do curso (padrão: courses/de-from-pt-br)")
    parser.add_argument(
        "--output",
        default=None,
        help=(
            "Arquivo .apkg de saída. Padrão: sem tópicos = <course>/output/exports/<course>.apkg "
            "com subdecks por nível/tópico; um tópico = output/exports/topics/<topic>.apkg; "
            "vários tópicos = output/exports/selected/<course>-<ids>.apkg com decks independentes por tópico"
        ),
    )
    parser.add_argument("--csv", action="store_true", help="Também exporta CSVs por tópico (sem áudio)")
    args = parser.parse_args()

    try:
        import genanki
    except ImportError:
        print("Erro: genanki não instalado. Rode: uv pip install --python .venv/bin/python -r requirements.txt")
        return 2

    course_root = resolve_course_root(args.course)
    config = load_course_config(course_root)
    out_root = exports_root(course_root)
    target_voice = config["target_voice"]
    deck_root_name = config["anki_deck_name"]

    topic_dirs = resolve_topic_dirs(args.topics, course_root)
    selected_topics = bool(args.topics)
    model = build_model(config["anki_model_name"], config["target_language_pt"])
    decks = []
    media_files: list[str] = []
    total_notes = 0
    skipped: list[str] = []

    for topic_dir in topic_dirs:
        cards = load_cards(topic_dir)
        if not cards:
            skipped.append(topic_dir.name)
            continue

        deck_name = deck_name_for(topic_dir, deck_root_name, selected_topics)
        deck = genanki.Deck(stable_id(deck_name), deck_name)

        for card in cards:
            fields = {
                "Front": str(card.get("front", "")),
                "Back": str(card.get("back", "")),
                "Example": str(card.get("example", "")),
                "ExampleTranslation": str(card.get("example_translation", "")),
                "FrontAudio": "",
                "ExampleAudio": "",
            }
            for text_field, audio_field in (("Front", "FrontAudio"), ("Example", "ExampleAudio")):
                text = fields[text_field].strip()
                if not text:
                    continue
                audio_path = find_audio(topic_dir, course_root, text, target_voice)
                if audio_path:
                    fields[audio_field] = f"[sound:{audio_path.name}]"
                    media_files.append(str(audio_path))

            note = genanki.Note(
                model=model,
                fields=list(fields.values()),
                guid=genanki.guid_for(topic_dir.name, fields["Front"]),
                tags=[topic_dir.parent.name, topic_dir.name],
            )
            deck.add_note(note)
            total_notes += 1

        decks.append(deck)
        if args.csv:
            export_csv(topic_dir, out_root, cards)

    if not decks:
        print("Nenhum flashcard encontrado para exportar.")
        return 1

    out_root.mkdir(parents=True, exist_ok=True)
    output_path = Path(args.output) if args.output else default_output_path(out_root, config, topic_dirs, selected_topics)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    package = genanki.Package(decks)
    package.media_files = sorted(set(media_files))
    package.write_to_file(str(output_path))

    print(f"Exportado: {output_path}")
    print(f"- {len(decks)} subdeck(s), {total_notes} nota(s), {len(set(media_files))} arquivo(s) de áudio")
    if skipped:
        print(f"- Sem flashcards (pulados): {', '.join(skipped)}")
    if args.csv:
        print(f"- CSVs em {out_root / 'anki-csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
