# Agent Instructions

## Repo Shape

- This repo generates language-learning source content for Brazilian Portuguese speakers; Markdown/YAML under `courses/<course-id>/` is the source of truth, not PDFs/audio/Anki exports.
- Default course is `courses/de-from-pt-br`; scripts also support `it-from-pt-br`, `en-from-pt-br`, and `fr-from-pt-br` via `--course` or a course path.
- Course-local truth lives in `course.yaml`, `roadmap.tsv`, `prompts/`, `topics/`, `reviews/`, `qa-baseline.txt`, and `output/`; shared scripts/templates/schemas are at repo root.
- Before creating content, read the exact row in the selected `roadmap.tsv` and the relevant course prompt files; do not invent topics outside the roadmap unless explicitly asked.

## Roadmap Lookup

- For a topic number, search the tab-delimited `Ordem` column directly instead of reading the whole roadmap: `^([^\t]*\t)<N>\t`; use `^([^\t]*\t)0?<N>\t` when leading zeroes are ambiguous.
- Important roadmap columns: `Nível`, `Ordem`, `Bloco`, `Tópico Principal`, `Subtópicos / Conteúdo`, `Status`, `Material Gerado`, `Flashcards`, `Exercícios`, `Teste`, `Revisado`.
- Topic folders are `courses/<course-id>/topics/<level>/<three-digit-order>-<slug>/`; keep slugs unique inside the selected course.
- Never edit roadmap status columns by hand; after source files exist, run `python3 scripts/sync-roadmap.py courses/<course-id>` or `python3 scripts/sync-roadmap.py --check courses/<course-id>`.

## Required Topic Sources

- Every topic folder must contain exactly these source files: `lesson.md`, `vocabulary.yaml`, `flashcards.yaml`, `exercises.yaml`, `test.yaml`, `story.md`, `answers.md`.
- Use Brazilian Portuguese for explanations, headings, labels, instructions, and answer explanations; use the target language only where the learner should read or produce it.
- Follow `courses/<course-id>/prompts/*.prompt.md` as the output contract and keep YAML field names compatible with the scripts; target vocabulary field is configured by `course.yaml` `target_word_field`.
- `story.md` must contain the heading configured by `course.yaml` `story_heading` so `scripts/generate-audio.py` can extract the target-language story.
- `answers.md` must include `## Gabarito dos exercícios` and `## Gabarito do teste` tables with an `Explicação` or `Observação` column; empty explanations fail validation.

## Content QA Rules

- Do not copy exercise items into `test.yaml`; `scripts/validate-content.py` checks for reused questions/answers.
- Multiple-choice items should have three options; distribute correct answers across positions 1, 2, and 3.
- Avoid English UI labels/headings in generated Markdown such as `Story`, `German Story`, `Line-by-line translation`, `Vocabulary notes`, or `Comprehension questions`.
- If flashcards are not useful, still create `flashcards.yaml` with `cards: []` and a short `note` explaining the intentional skip; `sync-roadmap.py` records this as `Pulado`.
- Scale lesson/story/exercises/test volume to roadmap level plus topic difficulty/importance; prefer varied practice over long prose for foundational or error-prone topics.

## Commands

- Scaffold empty topic files: `scripts/generate-topic.sh courses/<course-id>/topics/<level>/<order-slug>`.
- Validate one topic: `python3 scripts/validate-content.py courses/<course-id>/topics/<level>/<order-slug>`.
- Validate default German topics: `python3 scripts/validate-content.py`; legacy issues can be filtered with `--baseline courses/<course-id>/qa-baseline.txt`, but new topics should pass with zero unbaselined issues.
- Compile one topic PDF set: `scripts/compile-topic.sh --course courses/<course-id> <topic-order-or-folder>`; this needs Typst and Ghostscript (`gs`) and writes to `courses/<course-id>/output/pdf/<topic-folder>/`.
- Compile a course: `scripts/compile-all.sh courses/<course-id>`.
- Compile a review: `scripts/compile-review.sh --course courses/<course-id> 001-010`.
- Concatenate topics: `scripts/concat-topics.sh --course courses/<course-id> 1 10` for a range, or pass explicit topic numbers/folders.
- Install Python deps for audio/Anki: `uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt`.
- Generate audio: `.venv/bin/python scripts/generate-audio.py --course courses/<course-id> <topic-order-or-folder>`; it downloads Piper voices under `.cache/piper-voices/` and converts WAV to MP3 when `ffmpeg` exists.
- Export Anki: `.venv/bin/python scripts/export-anki.py --course courses/<course-id> <topic-order...>`; run audio generation first if card audio should be embedded.

## Reviews

- After each completed 10-topic block, create `courses/<course-id>/reviews/<start>-<end>/` with `test.yaml` from `prompts/review.prompt.md` and `answers.md` with a `## Gabarito do teste` table.
- Review tests must mix the block with fresh sentences and must not copy topic exercise/test items.
