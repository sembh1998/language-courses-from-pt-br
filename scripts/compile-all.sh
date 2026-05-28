#!/usr/bin/env bash
set -euo pipefail

for topic_dir in topics/*/*; do
  if [ -d "$topic_dir" ] && [ -f "$topic_dir/lesson.md" ]; then
    scripts/compile-topic.sh "$topic_dir"
  fi
done
