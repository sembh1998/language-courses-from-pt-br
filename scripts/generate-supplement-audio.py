#!/usr/bin/env python3
"""Generate TTS audio for compiled topic supplement stories."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import VOICES_DIR, extract_story_text, load_course_config, resolve_course_root, resolve_topic_dirs, topic_audio_dir


TARGET_RATE = 22050


def fail(message: str) -> None:
    raise SystemExit(f"Erro: {message}")


def ensure_voices(voices: tuple[str, ...]) -> None:
    missing = [voice for voice in voices if not (VOICES_DIR / f"{voice}.onnx").exists()]
    if not missing:
        return
    VOICES_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Baixando vozes Piper: {', '.join(missing)}")
    subprocess.run(
        [sys.executable, "-m", "piper.download_voices", *missing, "--data-dir", str(VOICES_DIR)],
        check=True,
    )


class Synthesizer:
    def __init__(self) -> None:
        self._voices: dict[str, object] = {}

    def _voice(self, name: str):
        if name not in self._voices:
            from piper import PiperVoice

            self._voices[name] = PiperVoice.load(VOICES_DIR / f"{name}.onnx")
        return self._voices[name]

    def samples(self, text: str, voice_name: str) -> np.ndarray:
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


def output_exists(wav_path: Path) -> bool:
    return wav_path.exists() or wav_path.with_suffix(".mp3").exists()


def write_wav(path: Path, samples: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(TARGET_RATE)
        wav_file.writeframes(samples.tobytes())


def convert_to_mp3(out_dir: Path) -> None:
    if not shutil.which("ffmpeg"):
        return
    for wav_path in out_dir.rglob("*.wav"):
        mp3_path = wav_path.with_suffix(".mp3")
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path), "-b:a", "64k", str(mp3_path)],
            check=True,
        )
        wav_path.unlink()


def story_paths_for(topic_dir: Path, name: str | None) -> list[Path]:
    supplements_dir = topic_dir / "supplements"
    if name:
        story_path = supplements_dir / f"{name}-story.md"
        if not story_path.exists():
            fail(f"arquivo ausente: {story_path}. Compile o suplemento primeiro.")
        return [story_path]
    if not supplements_dir.exists():
        return []
    return sorted(supplements_dir.glob("*-story.md"))


def all_topic_dirs_with_supplement_stories(course_root: Path) -> list[Path]:
    return sorted({path.parent.parent for path in (course_root / "topics").rglob("supplements/*-story.md")})


def generate_story_audio(
    synth: Synthesizer,
    story_path: Path,
    topic_dir: Path,
    course_root: Path,
    story_heading: str,
    target_voice: str,
    force: bool,
) -> bool:
    text = extract_story_text(story_path, story_heading)
    if not text:
        print(f"Aviso: história sem seção de áudio: {story_path}")
        return False
    name = story_path.name.removesuffix("-story.md")
    out_path = topic_audio_dir(topic_dir, course_root) / "supplements" / f"{name}-story.wav"
    if output_exists(out_path) and not force:
        return False
    write_wav(out_path, synth.samples(text, target_voice))
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera áudio TTS para histórias extras de suplementos.")
    parser.add_argument("topic", nargs="?", help="Número ou pasta do tópico; vazio = todos com supplements/*-story.md")
    parser.add_argument("name", nargs="?", help="Nome do suplemento sem sufixo; vazio = todos do tópico")
    parser.add_argument("--course", default=None, help="ID ou pasta do curso")
    parser.add_argument("--force", action="store_true", help="Regenera arquivos existentes")
    args = parser.parse_args()

    course_root = resolve_course_root(args.course)
    config = load_course_config(course_root)
    target_voice = config["target_voice"]
    story_heading = config["story_heading"]
    global np
    import numpy as np

    ensure_voices((target_voice,))
    synth = Synthesizer()

    if args.topic:
        topic_dirs = resolve_topic_dirs([args.topic], course_root)
    else:
        topic_dirs = all_topic_dirs_with_supplement_stories(course_root)
    if not topic_dirs:
        fail("nenhuma história extra compilada encontrada")

    written = 0
    seen = 0
    for topic_dir in topic_dirs:
        story_paths = story_paths_for(topic_dir, args.name)
        topic_written = 0
        for story_path in story_paths:
            seen += 1
            if generate_story_audio(synth, story_path, topic_dir, course_root, story_heading, target_voice, args.force):
                written += 1
                topic_written += 1
        convert_to_mp3(topic_audio_dir(topic_dir, course_root) / "supplements")
        status = f"{topic_written} história(s)" if topic_written else "nada a fazer"
        print(f"{topic_dir.name}: {status}")

    if seen == 0:
        fail("nenhum arquivo *-story.md encontrado em supplements/")
    print(f"Áudio de suplementos gerado em {course_root / 'output' / 'audio'} ({written} novo(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
