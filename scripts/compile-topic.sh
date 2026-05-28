#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  printf 'Usage: %s topics/a1/02-greetings\n' "$0" >&2
  exit 1
fi

topic_dir="${1%/}"
topic_name="$(basename "$topic_dir")"
topic_input="$(realpath --relative-to=templates "$topic_dir")"
out_dir="output/pdf/$topic_name"

mkdir -p "$out_dir"

typst compile --root . templates/lesson.typ "$out_dir/lesson.pdf" --input topic="$topic_input"
typst compile --root . templates/flashcards.typ "$out_dir/flashcards.pdf" --input topic="$topic_input"
typst compile --root . templates/exercises.typ "$out_dir/exercises.pdf" --input topic="$topic_input"
typst compile --root . templates/test.typ "$out_dir/test.pdf" --input topic="$topic_input"
typst compile --root . templates/story.typ "$out_dir/story.pdf" --input topic="$topic_input"

printf 'Compiled PDFs to %s\n' "$out_dir"
