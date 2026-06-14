#!/usr/bin/env python3
"""Generate TTS audio for topics with Piper.

Voices are read from <course>/course.yaml.

Outputs, per topic, under <course>/output/audio/<topic-folder>/:
- cards/<hash>.wav      one clip per flashcard front and example (German),
                        referenced by scripts/export-anki.py
- vocab-review.wav      passive-listening track: German word, Portuguese
                        translation, German example, Portuguese translation
- story.wav             the German story read aloud

Usage:
  .venv/bin/python scripts/generate-audio.py                         # all German topics
  .venv/bin/python scripts/generate-audio.py --course it-from-pt-br 22
  .venv/bin/python scripts/generate-audio.py courses/de-from-pt-br/topics/b2/104-partizip-i-como-adjetivo
  .venv/bin/python scripts/generate-audio.py --force 104
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (
    VOICES_DIR,
    audio_filename,
    load_course_config,
    resolve_course_root,
    resolve_topic_dirs,
    topic_audio_dir,
)

TARGET_RATE = 22050


def ensure_voices(voices: tuple[str, str]) -> None:
    missing = [
        voice
        for voice in voices
        if not (VOICES_DIR / f"{voice}.onnx").exists()
    ]
    if not missing:
        return
    VOICES_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Baixando vozes Piper: {', '.join(missing)}")
    subprocess.run(
        [sys.executable, "-m", "piper.download_voices", *missing, "--data-dir", str(VOICES_DIR)],
        check=True,
    )


class Synthesizer:
    """Lazy-loading wrapper around the two Piper voices."""

    def __init__(self) -> None:
        self._voices: dict[str, object] = {}

    def _voice(self, name: str):
        if name not in self._voices:
            from piper import PiperVoice

            self._voices[name] = PiperVoice.load(VOICES_DIR / f"{name}.onnx")
        return self._voices[name]

    def samples(self, text: str, voice_name: str) -> np.ndarray:
        """Synthesize text and return mono int16 samples at TARGET_RATE."""
        voice = self._voice(voice_name)
        chunks = list(voice.synthesize(text))
        if not chunks:
            return np.zeros(0, dtype=np.int16)
        rate = chunks[0].sample_rate
        audio = np.frombuffer(b"".join(c.audio_int16_bytes for c in chunks), dtype=np.int16)
        return self._resample(audio, rate)

    @staticmethod
    def _resample(audio: np.ndarray, rate: int) -> np.ndarray:
        if rate == TARGET_RATE or audio.size == 0:
            return audio
        length = int(round(audio.size * TARGET_RATE / rate))
        positions = np.linspace(0, audio.size - 1, length)
        return np.interp(positions, np.arange(audio.size), audio.astype(np.float32)).astype(np.int16)


def silence(seconds: float) -> np.ndarray:
    return np.zeros(int(TARGET_RATE * seconds), dtype=np.int16)


def output_exists(wav_path: Path) -> bool:
    """True when the WAV or its MP3 conversion already exists."""
    return wav_path.exists() or wav_path.with_suffix(".mp3").exists()


def write_wav(path: Path, samples: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(TARGET_RATE)
        wav_file.writeframes(samples.tobytes())


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # noqa: BLE001
        print(f"Aviso: YAML inválido ignorado: {path} ({exc})")
        return {}


def target_story_text(story_path: Path, story_heading: str) -> str:
    if not story_path.exists():
        return ""
    text = story_path.read_text(encoding="utf-8")
    start = text.find(story_heading)
    if start == -1:
        return ""
    start += len(story_heading)
    end = text.find("\n## ", start)
    section = text[start:end] if end != -1 else text[start:]
    section = re.sub(r"[„“”«»]", "", section)
    return " ".join(section.split())


def generate_card_clips(synth: Synthesizer, topic_dir: Path, course_root: Path, target_voice: str, force: bool) -> int:
    cards = load_yaml(topic_dir / "flashcards.yaml").get("cards") or []
    out_dir = topic_audio_dir(topic_dir, course_root) / "cards"
    written = 0
    for card in cards:
        if not isinstance(card, dict):
            continue
        for field in ("front", "example"):
            text = str(card.get(field) or "").strip()
            if not text:
                continue
            path = out_dir / audio_filename(text, target_voice)
            if output_exists(path) and not force:
                continue
            write_wav(path, synth.samples(text, target_voice))
            written += 1
    return written


def generate_vocab_review(
    synth: Synthesizer,
    topic_dir: Path,
    course_root: Path,
    target_voice: str,
    source_voice: str,
    target_word_field: str,
    force: bool,
) -> bool:
    words = load_yaml(topic_dir / "vocabulary.yaml").get("words") or []
    if not words:
        return False
    out_path = topic_audio_dir(topic_dir, course_root) / "vocab-review.wav"
    if output_exists(out_path) and not force:
        return False

    parts: list[np.ndarray] = []
    for word in words:
        if not isinstance(word, dict):
            continue
        target_word = str(word.get(target_word_field) or word.get("target") or word.get("german") or "").strip()
        translation = str(word.get("translation") or "").strip()
        example = str(word.get("example") or "").strip()
        example_translation = str(word.get("example_translation") or "").strip()
        if not target_word:
            continue
        parts.extend((synth.samples(target_word, target_voice), silence(0.7)))
        if translation:
            parts.extend((synth.samples(translation, source_voice), silence(0.5)))
        if example:
            parts.extend((synth.samples(example, target_voice), silence(0.6)))
        if example_translation:
            parts.extend((synth.samples(example_translation, source_voice),))
        parts.append(silence(1.2))

    if not parts:
        return False
    write_wav(out_path, np.concatenate(parts))
    return True


def generate_story_audio(synth: Synthesizer, topic_dir: Path, course_root: Path, target_voice: str, force: bool) -> bool:
    config = load_course_config(course_root)
    text = target_story_text(topic_dir / "story.md", config["story_heading"])
    if not text:
        return False
    out_path = topic_audio_dir(topic_dir, course_root) / "story.wav"
    if output_exists(out_path) and not force:
        return False
    write_wav(out_path, synth.samples(text, target_voice))
    return True


def convert_to_mp3(topic_dir: Path, course_root: Path) -> None:
    """Convert WAV files to MP3 in place when ffmpeg is available."""
    if not shutil.which("ffmpeg"):
        return
    for wav_path in topic_audio_dir(topic_dir, course_root).rglob("*.wav"):
        mp3_path = wav_path.with_suffix(".mp3")
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path), "-b:a", "64k", str(mp3_path)],
            check=True,
        )
        wav_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera áudio TTS por tópico com Piper.")
    parser.add_argument("topics", nargs="*", help="Números de ordem ou pastas de tópicos (vazio = todos)")
    parser.add_argument("--course", default=None, help="ID ou pasta do curso (padrão: courses/de-from-pt-br)")
    parser.add_argument("--force", action="store_true", help="Regenera arquivos existentes")
    parser.add_argument("--skip-cards", action="store_true", help="Não gera clipes de flashcards")
    parser.add_argument("--skip-vocab", action="store_true", help="Não gera a faixa de revisão de vocabulário")
    parser.add_argument("--skip-story", action="store_true", help="Não gera o áudio da história")
    args = parser.parse_args()

    course_root = resolve_course_root(args.course)
    config = load_course_config(course_root)
    target_voice = config["target_voice"]
    source_voice = config["source_voice"]
    target_word_field = config["target_word_field"]

    ensure_voices((target_voice, source_voice))
    synth = Synthesizer()
    topic_dirs = resolve_topic_dirs(args.topics, course_root)

    for topic_dir in topic_dirs:
        results: list[str] = []
        if not args.skip_cards:
            clips = generate_card_clips(synth, topic_dir, course_root, target_voice, args.force)
            if clips:
                results.append(f"{clips} clipe(s) de flashcards")
        if not args.skip_vocab and generate_vocab_review(
            synth,
            topic_dir,
            course_root,
            target_voice,
            source_voice,
            target_word_field,
            args.force,
        ):
            results.append("vocab-review")
        if not args.skip_story and generate_story_audio(synth, topic_dir, course_root, target_voice, args.force):
            results.append("story")
        convert_to_mp3(topic_dir, course_root)
        status = ", ".join(results) if results else "nada a fazer"
        print(f"{topic_dir.name}: {status}")

    print(f"Áudio gerado em {course_root / 'output' / 'audio'} para {len(topic_dirs)} tópico(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
