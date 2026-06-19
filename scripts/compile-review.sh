#!/usr/bin/env bash
set -euo pipefail

course_dir="courses/de-from-pt-br"
if [ "${1:-}" = "--course" ]; then
  if [ "$#" -lt 3 ]; then
    printf 'Usage: %s [--course <course-folder>] <review-folder|review-range>\n' "$0" >&2
    exit 1
  fi
  course_dir="${2%/}"
  shift 2
fi

if [ "$#" -ne 1 ]; then
  printf 'Usage: %s [--course <course-folder>] <review-folder|review-range>\n' "$0" >&2
  printf 'Examples:\n' >&2
  printf '  %s 001-010\n' "$0" >&2
  printf '  %s --course courses/it-from-pt-br 001-010\n' "$0" >&2
  printf '  %s courses/de-from-pt-br/reviews/001-010\n' "$0" >&2
  exit 1
fi

if [ ! -d "$course_dir" ]; then
  printf 'Error: course folder not found: %s\n' "$course_dir" >&2
  exit 1
fi

review_arg="${1%/}"

if [[ "$review_arg" =~ ^[0-9]{3}-[0-9]{3}$ ]]; then
  review_dir="$course_dir/reviews/$review_arg"
else
  review_dir="$review_arg"
fi

if [ ! -d "$review_dir" ]; then
  printf 'Error: review folder not found: %s\n' "$review_dir" >&2
  exit 1
fi

if [ ! -f "$review_dir/test.yaml" ]; then
  printf 'Error: missing %s/test.yaml\n' "$review_dir" >&2
  exit 1
fi

review_name="revisao-$(basename "$review_dir")"
review_input="$(realpath --relative-to=templates "$review_dir")"
out_dir="$course_dir/output/pdf/$review_name"
target_language_pt="$(awk -F': ' '$1 == "target_language_pt" { gsub(/^"|"$/, "", $2); print $2; exit }' "$course_dir/course.yaml")"
if [ -z "$target_language_pt" ]; then
  target_language_pt="alemão"
fi
course_label="${target_language_pt^} para PT-BR"

mkdir -p "$out_dir"

typst compile --root . templates/test.typ "$out_dir/test.pdf" \
  --input topic="$review_input" \
  --input course-label="$course_label" \
  --input target-language-pt="$target_language_pt"

printf 'Compiled review test to %s\n' "$out_dir/test.pdf"
