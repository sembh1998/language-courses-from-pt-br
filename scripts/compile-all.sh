#!/usr/bin/env bash
set -euo pipefail

course_dir="${1:-courses/de-from-pt-br}"

if [ ! -d "$course_dir" ]; then
  printf 'Error: course folder not found: %s\n' "$course_dir" >&2
  exit 1
fi

for topic_dir in "$course_dir"/topics/*/*; do
  if [ -d "$topic_dir" ] && [ -f "$topic_dir/lesson.md" ]; then
    scripts/compile-topic.sh --course "$course_dir" "$topic_dir"
  fi
done
