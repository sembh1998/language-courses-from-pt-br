#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  printf 'Usage: %s courses/de-from-pt-br/topics/a1/003-topic-name\n' "$0" >&2
  exit 1
fi

topic_dir="$1"
mkdir -p "$topic_dir"

touch \
  "$topic_dir/lesson.md" \
  "$topic_dir/vocabulary.yaml" \
  "$topic_dir/flashcards.yaml" \
  "$topic_dir/exercises.yaml" \
  "$topic_dir/test.yaml" \
  "$topic_dir/story.md" \
  "$topic_dir/answers.md"

printf 'Created topic scaffold: %s\n' "$topic_dir"
printf 'Use the course prompts folder to fill each file.\n'
