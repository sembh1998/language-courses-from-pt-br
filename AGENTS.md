# Agent Instructions

## Repo Shape

- This repo generates language-learning source content for Brazilian Portuguese speakers; structured JSON plus compiled Markdown/YAML under `courses/<course-id>/` are the source of truth, not PDFs/audio/Anki exports.
- Default course is `courses/de-from-pt-br`; scripts also support `it-from-pt-br`, `en-from-pt-br`, `fr-from-pt-br`, and `es-from-pt-br` via `--course` or a course path.
- Course-local truth lives in `course.yaml`, `roadmap.tsv`, `prompts/`, `topics/`, `reviews/`, `qa-baseline.txt`, and `output/`; shared scripts/templates/schemas are at repo root.
- For new topics, generate one `content.json` semantic source and compile the seven learner-facing files. When `content.json` exists, it is the source of truth; do not hand-edit its compiled files. Legacy `content.yaml` remains readable.
- Before creating content, run `python3 scripts/build-context.py --course courses/<course-id> <order>` or read the exact roadmap row and contract yourself; do not invent topics outside the roadmap unless explicitly asked.

## Roadmap Lookup

- For a topic number, search the tab-delimited `Ordem` column directly instead of reading the whole roadmap: `^([^\t]*\t)<N>\t`; use `^([^\t]*\t)0?<N>\t` when leading zeroes are ambiguous.
- Important roadmap columns: `Nível`, `Ordem`, `Bloco`, `Tópico Principal`, `Subtópicos / Conteúdo`, `Status`, `Material Gerado`, `Flashcards`, `Exercícios`, `Teste`, `Revisado`.
- Topic folders are `courses/<course-id>/topics/<level>/<three-digit-order>-<slug>/`; keep slugs unique inside the selected course.
- Never edit roadmap status columns by hand; after source files exist, run `python3 scripts/sync-roadmap.py courses/<course-id>` or `python3 scripts/sync-roadmap.py --check courses/<course-id>`.

## Required Topic Sources

- Every compiled topic folder must contain `lesson.md`, `vocabulary.yaml`, `flashcards.yaml`, `exercises.yaml`, `test.yaml`, `story.md`, and `answers.md`. New structured topics also contain `content.json`.
- In `content.json`, keep each answer and explanation beside its question, and keep story target/translation sentence pairs together. Let `compile-content.py` generate IDs, answer tables, story duplication, points, flashcards, and multiple-choice ordering.
- Use Brazilian Portuguese for explanations, headings, labels, instructions, and answer explanations; use the target language only where the learner should read or produce it.
- Prefer the compact context builder and `schemas/content.schema.json`; use that schema with structured model outputs when available. `courses/<course-id>/prompts/*.prompt.md` remain the legacy seven-call contracts.
- JSON may be compact rather than pretty-printed to reduce output tokens; semantic completeness matters, whitespace does not.
- `story.md` must contain the heading configured by `course.yaml` `story_heading` so `scripts/generate-audio.py` can extract the target-language story.
- `answers.md` must include `## Gabarito dos exercícios` and `## Gabarito do teste` tables with an `Explicação` or `Observação` column; empty explanations fail validation.

## Content QA Rules

- Do not copy exercise items into `test.yaml`; `scripts/validate-content.py` checks for reused questions/answers.
- Multiple-choice items should have three options; distribute correct answers across positions 1, 2, and 3.
- In structured sources, provide the correct `answer` plus exactly two `distractors`; the compiler distributes the answer positions.
- Avoid English UI labels/headings in generated Markdown such as `Story`, `German Story`, `Line-by-line translation`, `Vocabulary notes`, or `Comprehension questions`.
- If flashcards are not useful, still create `flashcards.yaml` with `cards: []` and a short `note` explaining the intentional skip; `sync-roadmap.py` records this as `Pulado`.
- Scale lesson/story/exercises/test volume to roadmap level plus topic difficulty/importance; prefer varied practice over long prose for foundational or error-prone topics.

## Commands

- Scaffold a topic: `scripts/generate-topic.sh courses/<course-id>/topics/<level>/<order-slug>`.
- Build compact model context: `python3 scripts/build-context.py --course courses/<course-id> <order>`.
- Compile `content.json`: `python3 scripts/compile-content.py --course courses/<course-id> <topic-order-or-folder>`.
- Check compiled files without writing: `python3 scripts/compile-content.py --check --course courses/<course-id> <topic-order-or-folder>`.
- Validate one topic: `python3 scripts/validate-content.py courses/<course-id>/topics/<level>/<order-slug>`.
- Validate default German topics: `python3 scripts/validate-content.py`; legacy issues can be filtered with `--baseline courses/<course-id>/qa-baseline.txt`, but new topics should pass with zero unbaselined issues.
- Compile one topic PDF set: `scripts/compile-topic.sh --course courses/<course-id> <topic-order-or-folder>`; this needs Typst and Ghostscript (`gs`) and writes to `courses/<course-id>/output/pdf/<topic-folder>/`.
- Compile a course: `scripts/compile-all.sh courses/<course-id>`.
- Compile a review: `scripts/compile-review.sh --course courses/<course-id> 001-010`.
- Concatenate topics: `scripts/concat-topics.sh --course courses/<course-id> 1 10` for a range, or pass explicit topic numbers/folders.
- Install Python deps for audio/Anki: `uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt`.
- Generate audio: `.venv/bin/python scripts/generate-audio.py --course courses/<course-id> <topic-order-or-folder>`; it downloads Piper voices under `.cache/piper-voices/` and converts WAV to MP3 when `ffmpeg` exists.
- Export Anki: `.venv/bin/python scripts/export-anki.py --course courses/<course-id> <topic-order...>`; run audio generation first if card audio should be embedded. With topic args, the default output is separated under `output/exports/topics/` for one topic or `output/exports/selected/` for multiple topics. With no topic args, it writes the course-wide package from `course.yaml`.

## Reviews

- After each completed 10-topic block, create `courses/<course-id>/reviews/<start>-<end>/` with `test.yaml` from `prompts/review.prompt.md` and `answers.md` with a `## Gabarito do teste` table.
- For new reviews, generate `review.json` from `scripts/build-review-context.py`, then run `scripts/compile-review-content.py`; `review.json` is the semantic source.
- Review tests must mix the block with fresh sentences and must not copy topic exercise/test items.
- Validate review coverage with `python3 scripts/validate-reviews.py courses/<course-id>`.
- `review-baseline.txt` may list legacy missing blocks only; never add a newly completed block instead of generating its review.
