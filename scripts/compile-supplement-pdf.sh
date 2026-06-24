#!/usr/bin/env bash
set -euo pipefail

course_dir="courses/de-from-pt-br"
if [ "${1:-}" = "--course" ]; then
  if [ "$#" -lt 4 ]; then
    printf 'Usage: %s [--course <course-folder>] <topic-folder|topic-order> <supplement-name>\n' "$0" >&2
    exit 1
  fi
  course_dir="${2%/}"
  shift 2
fi

if [ "$#" -ne 2 ]; then
  printf 'Usage: %s [--course <course-folder>] <topic-folder|topic-order> <supplement-name>\n' "$0" >&2
  printf 'Examples:\n' >&2
  printf '  %s --course courses/de-from-pt-br 34 mastery-001\n' "$0" >&2
  exit 1
fi

if [ ! -d "$course_dir" ]; then
  printf 'Error: course folder not found: %s\n' "$course_dir" >&2
  exit 1
fi

topic_arg="${1%/}"
supplement_name="$2"

if [[ ! "$supplement_name" =~ ^[A-Za-z0-9][A-Za-z0-9_-]*$ ]]; then
  printf 'Error: invalid supplement name: %s\n' "$supplement_name" >&2
  exit 1
fi

if [[ "$topic_arg" =~ ^[0-9]+$ ]]; then
  topic_order="$(printf '%03d' "$topic_arg")"
  shopt -s nullglob
  matches=("$course_dir"/topics/*/"$topic_order"-*)
  shopt -u nullglob

  if [ "${#matches[@]}" -eq 0 ]; then
    printf 'Error: no topic found for order %s under %s/topics/*/%s-*\n' "$topic_arg" "$course_dir" "$topic_order" >&2
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

supplement_dir="$topic_dir/supplements"
if [ ! -d "$supplement_dir" ]; then
  printf 'Error: supplements folder not found: %s\n' "$supplement_dir" >&2
  exit 1
fi

topic_name="$(basename "$topic_dir")"
topic_order_prefix="${topic_name%%-*}"
topic_number="$topic_order_prefix"
if [[ "$topic_order_prefix" =~ ^[0-9]+$ ]]; then
  topic_number="$(printf '%d' "$((10#$topic_order_prefix))")"
fi

target_language_pt="$(awk -F': ' '$1 == "target_language_pt" { gsub(/^"|"$/, "", $2); print $2; exit }' "$course_dir/course.yaml")"
if [ -z "$target_language_pt" ]; then
  target_language_pt="alemão"
fi
course_label="${target_language_pt^} para PT-BR"

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

out_dir="$course_dir/output/pdf/$topic_name/supplements/$supplement_name"
work_dir=".cache/supplement-pdf/$topic_name/$supplement_name"
rm -rf "$work_dir"
mkdir -p "$work_dir" "$out_dir"

compiled=()

if [ -f "$supplement_dir/$supplement_name-exercises.yaml" ]; then
  ln -s "$(realpath "$supplement_dir/$supplement_name-exercises.yaml")" "$work_dir/exercises.yaml"
  work_input="$(realpath --relative-to=templates "$work_dir")"
  "${typst_cmd[@]}" compile --root . templates/exercises.typ "$out_dir/exercises.pdf" --input topic="$work_input" --input course-label="$course_label" --input target-language-pt="$target_language_pt" --input lesson-number="$topic_number"
  compiled+=("$out_dir/exercises.pdf")
fi

if [ -f "$supplement_dir/$supplement_name-story.md" ]; then
  story_input="$(realpath --relative-to=templates "$supplement_dir/$supplement_name-story.md")"
  "${typst_cmd[@]}" compile --root . templates/markdown.typ "$out_dir/story.pdf" --input file="$story_input" --input title="História extra em $target_language_pt" --input kind="História extra" --input course-label="$course_label" --input lesson-number="$topic_number"
  compiled+=("$out_dir/story.pdf")
fi

if [ -f "$supplement_dir/$supplement_name-test.yaml" ]; then
  ln -s "$(realpath "$supplement_dir/$supplement_name-test.yaml")" "$work_dir/test.yaml"
  work_input="$(realpath --relative-to=templates "$work_dir")"
  "${typst_cmd[@]}" compile --root . templates/test.typ "$out_dir/test.pdf" --input topic="$work_input" --input course-label="$course_label" --input target-language-pt="$target_language_pt" --input lesson-number="$topic_number"
  compiled+=("$out_dir/test.pdf")
fi

if [ -f "$supplement_dir/$supplement_name-answers.md" ]; then
  answers_input="$(realpath --relative-to=templates "$supplement_dir/$supplement_name-answers.md")"
  "${typst_cmd[@]}" compile --root . templates/markdown.typ "$out_dir/answers.pdf" --input file="$answers_input" --input title="Respostas extras" --input kind="Gabarito" --input course-label="$course_label" --input lesson-number="$topic_number"
  compiled+=("$out_dir/answers.pdf")
fi

if [ "${#compiled[@]}" -eq 0 ]; then
  printf 'Error: no compiled supplement files found for %s in %s\n' "$supplement_name" "$supplement_dir" >&2
  exit 1
fi

if command -v gs >/dev/null 2>&1; then
  gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite "-sOutputFile=$out_dir/combined.pdf" "${compiled[@]}"
else
  printf 'Warning: gs not found; skipped combined.pdf\n' >&2
fi

printf 'Compiled supplement PDFs to %s\n' "$out_dir"
