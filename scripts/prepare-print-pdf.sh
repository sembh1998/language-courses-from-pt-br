#!/usr/bin/env bash
set -euo pipefail

start_at="1"
make_booklet="1"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --start)
      if [ "$#" -lt 2 ]; then
        printf 'Error: --start requires a page number\n' >&2
        exit 1
      fi
      start_at="$2"
      shift 2
      ;;
    --no-booklet)
      make_booklet="0"
      shift
      ;;
    -h|--help)
      printf 'Usage: %s [--start <number>] [--no-booklet] <input.pdf>\n' "$0"
      printf 'Creates <input>-numbered.pdf and, unless --no-booklet is used, <input>-booklet.pdf.\n'
      exit 0
      ;;
    --*)
      printf 'Error: unknown option: %s\n' "$1" >&2
      exit 1
      ;;
    *)
      break
      ;;
  esac
done

if [ "$#" -ne 1 ]; then
  printf 'Usage: %s [--start <number>] [--no-booklet] <input.pdf>\n' "$0" >&2
  exit 1
fi

input_pdf="${1%/}"
if [ ! -f "$input_pdf" ]; then
  printf 'Error: PDF not found: %s\n' "$input_pdf" >&2
  exit 1
fi

if [[ ! "$start_at" =~ ^[0-9]+$ ]] || [ "$start_at" -lt 1 ]; then
  printf 'Error: --start must be a positive integer\n' >&2
  exit 1
fi

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

if ! command -v mutool >/dev/null 2>&1; then
  printf 'Error: mutool not found. Install mupdf-tools to read PDF page counts.\n' >&2
  exit 1
fi

pdf_info="$(mutool info "$input_pdf")"
page_count="$(awk '/^Pages:/ { print $2; exit }' <<< "$pdf_info")"
if [[ ! "$page_count" =~ ^[0-9]+$ ]] || [ "$page_count" -lt 1 ]; then
  printf 'Error: could not determine page count for %s\n' "$input_pdf" >&2
  exit 1
fi

input_dir="$(dirname "$input_pdf")"
input_name="$(basename "$input_pdf")"
stem="${input_name%.pdf}"
numbered_pdf="$input_dir/$stem-numbered.pdf"
booklet_pdf="$input_dir/$stem-booklet.pdf"

input_for_typst="$(realpath --relative-to=templates "$input_pdf")"
numbered_for_typst="$(realpath --relative-to=templates "$numbered_pdf")"

"${typst_cmd[@]}" compile --root . templates/pdf-numbered.typ "$numbered_pdf" \
  --input input="$input_for_typst" \
  --input pages="$page_count" \
  --input start="$start_at"

printf 'Created %s\n' "$numbered_pdf"

if [ "$make_booklet" = "1" ]; then
  padded_count=$(( ((page_count + 3) / 4) * 4 ))
  "${typst_cmd[@]}" compile --root . templates/pdf-booklet.typ "$booklet_pdf" \
    --input input="$numbered_for_typst" \
    --input pages="$page_count"
  printf 'Created %s (%s source pages padded to %s booklet pages)\n' "$booklet_pdf" "$page_count" "$padded_count"
fi
