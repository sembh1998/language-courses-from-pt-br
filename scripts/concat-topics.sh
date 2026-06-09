#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  printf 'Usage: %s <topic-order|topic-folder> [topic-order|topic-folder ...]\n' "$0" >&2
  printf 'Examples:\n' >&2
  printf '  %s 18 26     # topics 18 through 26\n' "$0" >&2
  printf '  %s 18 20 26  # only topics 18, 20, and 26\n' "$0" >&2
  exit 1
fi

if ! command -v gs >/dev/null 2>&1; then
  printf 'Error: gs not found. Install Ghostscript to concatenate PDFs.\n' >&2
  exit 1
fi

resolve_topic_dir() {
  local topic_arg="${1%/}"

  if [[ "$topic_arg" =~ ^[0-9]+$ ]]; then
    local topic_order
    topic_order="$(printf '%03d' "$topic_arg")"

    shopt -s nullglob
    local matches=(topics/*/"$topic_order"-*)
    shopt -u nullglob

    if [ "${#matches[@]}" -eq 0 ]; then
      printf 'Error: no topic found for order %s under topics/*/%s-*\n' "$topic_arg" "$topic_order" >&2
      return 1
    fi

    if [ "${#matches[@]}" -gt 1 ]; then
      printf 'Error: multiple topics found for order %s:\n' "$topic_arg" >&2
      printf '  %s\n' "${matches[@]}" >&2
      return 1
    fi

    printf '%s\n' "${matches[0]}"
    return 0
  fi

  if [ ! -d "$topic_arg" ]; then
    printf 'Error: topic folder not found: %s\n' "$topic_arg" >&2
    return 1
  fi

  printf '%s\n' "$topic_arg"
}

topic_args=("$@")

if [ "$#" -eq 2 ] && [[ "$1" =~ ^[0-9]+$ ]] && [[ "$2" =~ ^[0-9]+$ ]]; then
  start="$1"
  end="$2"

  if [ "$start" -gt "$end" ]; then
    printf 'Error: range start must be lower than or equal to range end: %s %s\n' "$start" "$end" >&2
    exit 1
  fi

  topic_args=()
  for ((order = start; order <= end; order++)); do
    topic_args+=("$order")
  done
fi

topic_dirs=()
combined_pdfs=()
output_parts=()

for topic_arg in "${topic_args[@]}"; do
  topic_dir="$(resolve_topic_dir "$topic_arg")"
  topic_dirs+=("$topic_dir")

  topic_name="$(basename "$topic_dir")"
  combined_pdf="output/pdf/$topic_name/combined.pdf"

  if [ ! -f "$combined_pdf" ]; then
    scripts/compile-topic.sh "$topic_dir"
  fi

  if [ ! -f "$combined_pdf" ]; then
    printf 'Error: combined PDF was not created for %s\n' "$topic_dir" >&2
    exit 1
  fi

  combined_pdfs+=("$combined_pdf")
  output_parts+=("${topic_name%%-*}")
done

out_dir="output/pdf/concat"
mkdir -p "$out_dir"

out_name="$(IFS=-; printf '%s' "${output_parts[*]}")-combined.pdf"
out_file="$out_dir/$out_name"

gs \
  -dBATCH \
  -dNOPAUSE \
  -q \
  -sDEVICE=pdfwrite \
  "-sOutputFile=$out_file" \
  "${combined_pdfs[@]}"

printf 'Concatenated %s topic PDFs into %s\n' "${#combined_pdfs[@]}" "$out_file"
