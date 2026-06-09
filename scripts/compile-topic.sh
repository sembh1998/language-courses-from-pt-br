#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  printf 'Usage: %s <topic-folder|topic-order>\n' "$0" >&2
  printf 'Examples:\n' >&2
  printf '  %s 18\n' "$0" >&2
  printf '  %s topics/a1/018-presente-dos-verbos-regulares\n' "$0" >&2
  exit 1
fi

topic_arg="${1%/}"

if [[ "$topic_arg" =~ ^[0-9]+$ ]]; then
  topic_order="$(printf '%03d' "$topic_arg")"
  shopt -s nullglob
  matches=(topics/*/"$topic_order"-*)
  shopt -u nullglob

  if [ "${#matches[@]}" -eq 0 ]; then
    printf 'Error: no topic found for order %s under topics/*/%s-*\n' "$topic_arg" "$topic_order" >&2
    exit 1
  fi

  if [ "${#matches[@]}" -gt 1 ]; then
    printf 'Error: multiple topics found for order %s:\n' "$topic_arg" >&2
    printf '  %s\n' "${matches[@]}" >&2
    exit 1
  fi

  topic_dir="${matches[0]}"
else
  topic_dir="$topic_arg"
fi

if [ ! -d "$topic_dir" ]; then
  printf 'Error: topic folder not found: %s\n' "$topic_dir" >&2
  exit 1
fi

topic_name="$(basename "$topic_dir")"
topic_input="$(realpath --relative-to=templates "$topic_dir")"
out_dir="output/pdf/$topic_name"

typst_cmd=(typst)
if ! command -v typst >/dev/null 2>&1; then
  typst_winget=""
  for candidate in /mnt/c/Users/*/AppData/Local/Microsoft/WinGet/Packages/Typst.Typst_*/*/typst.exe; do
    if [ -x "$candidate" ]; then
      typst_winget="$candidate"
      break
    fi
  done

  if [ -n "$typst_winget" ]; then
    typst_cmd=("$typst_winget")
  else
    printf 'Error: typst not found. Install Typst in WSL or with winget.\n' >&2
    exit 1
  fi
fi

mkdir -p "$out_dir"

"${typst_cmd[@]}" compile --root . templates/lesson.typ "$out_dir/lesson.pdf" --input topic="$topic_input"
"${typst_cmd[@]}" compile --root . templates/flashcards.typ "$out_dir/flashcards.pdf" --input topic="$topic_input"
"${typst_cmd[@]}" compile --root . templates/exercises.typ "$out_dir/exercises.pdf" --input topic="$topic_input"
"${typst_cmd[@]}" compile --root . templates/test.typ "$out_dir/test.pdf" --input topic="$topic_input"
"${typst_cmd[@]}" compile --root . templates/story.typ "$out_dir/story.pdf" --input topic="$topic_input"

gs \
  -dBATCH \
  -dNOPAUSE \
  -q \
  -sDEVICE=pdfwrite \
  "-sOutputFile=$out_dir/combined.pdf" \
  "$out_dir/lesson.pdf" \
  "$out_dir/flashcards.pdf" \
  "$out_dir/exercises.pdf" \
  "$out_dir/story.pdf" \
  "$out_dir/test.pdf"

printf 'Compiled PDFs to %s\n' "$out_dir"
