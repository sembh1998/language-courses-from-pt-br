# Language Learning Content Generator

A local content-generation system for language-learning materials for Brazilian Portuguese speakers.

The repository is now multi-course: course-specific roadmaps, prompts, topics, reviews, and outputs live under `courses/<course-id>/`; shared scripts, schemas, and Typst templates stay at the repository root.

New model generation uses schema-validated JSON; deterministic compilers produce
the learner-facing Markdown and YAML files.

For fast task routing, read `QUICKSTART.md` first. It contains short command recipes for topic lookup, topic PDFs, concat PDFs, supplements, audio, numbered PDFs, and booklet PDFs.

## Courses

```txt
courses/
├── de-from-pt-br/   # German from Brazilian Portuguese
├── it-from-pt-br/   # Italian from Brazilian Portuguese
├── en-from-pt-br/   # English from Brazilian Portuguese
├── fr-from-pt-br/   # French from Brazilian Portuguese
└── es-from-pt-br/   # Spanish from Brazilian Portuguese
```

Each course contains:

```txt
course.yaml
roadmap.tsv
qa-baseline.txt
prompts/
topics/
reviews/
output/
```

`courses/de-from-pt-br` is the default course for scripts when no course is specified.

## Shared Structure

```txt
learning-languages-from-pt-br/
├── courses/
│   ├── de-from-pt-br/
│   ├── it-from-pt-br/
│   ├── en-from-pt-br/
│   ├── fr-from-pt-br/
│   └── es-from-pt-br/
├── schemas/
├── scripts/
├── templates/
├── requirements.txt
└── README.md
```

## Topic Files

Each compiled topic folder contains these learner-facing source files:

```txt
lesson.md
vocabulary.yaml
flashcards.yaml
exercises.yaml
test.yaml
story.md
answers.md
```

New topics also use:

```txt
content.json
```

`content.json` is the semantic source of truth. A deterministic compiler creates
the seven files above, so answers, explanations, story translations, IDs,
points, flashcards, and multiple-choice positions are not regenerated in
separate model calls. JSON prevents YAML coercions such as `on` becoming a
boolean or `null` becoming an empty value. Legacy `content.yaml` remains
supported.

Example topic folder:

```txt
courses/de-from-pt-br/topics/a1/001-alfabeto-alemao-e-sons-basicos/
```

## Add A Topic

Choose a topic from the selected course roadmap, then scaffold the topic folder:

```sh
scripts/generate-topic.sh courses/de-from-pt-br/topics/a1/001-alfabeto-alemao-e-sons-basicos
```

Build a compact context containing only the course profile, exact roadmap row,
selected CEFR guidance, and structured contract:

```sh
python3 scripts/build-context.py --course courses/de-from-pt-br 105
```

Ask the model for only `content.json`, preferably with
`schemas/content.schema.json` as the API response schema. Save it in the topic
folder, then compile:

```sh
python3 scripts/compile-content.py --course courses/de-from-pt-br 105
python3 scripts/validate-content.py courses/de-from-pt-br/topics/b2/105-topic-slug
```

The JSON may be compact rather than pretty-printed. This limits formatting-token
overhead while retaining strict parsing and schema validation.

Verify that compiled files are current without modifying them:

```sh
python3 scripts/compile-content.py --check --course courses/de-from-pt-br 105
```

The older per-file prompt contracts remain available for legacy topics:

```txt
courses/de-from-pt-br/prompts/
courses/it-from-pt-br/prompts/
courses/en-from-pt-br/prompts/
courses/fr-from-pt-br/prompts/
courses/es-from-pt-br/prompts/
```

Italian, English, French, and Spanish currently have starter prompt folders and roadmaps ready to be filled.

## Structured Reviews

Build compact context for a completed ten-topic block:

```sh
python3 scripts/build-review-context.py --course courses/en-from-pt-br 041-050
```

Save the model output as `reviews/041-050/review.json`, preferably using
`schemas/review-content.schema.json`, then compile and validate:

```sh
python3 scripts/compile-review-content.py --course courses/en-from-pt-br 041-050
python3 scripts/validate-reviews.py courses/en-from-pt-br
```

Legacy missing review blocks can be recorded explicitly in
`review-baseline.txt`; newly completed blocks must receive a real review rather
than a new baseline entry.

## Validate Content

Validate one topic:

```sh
python3 scripts/validate-content.py courses/de-from-pt-br/topics/a1/001-alfabeto-alemao-e-sons-basicos
```

Validate the default German topics:

```sh
python3 scripts/validate-content.py
```

## Sync Roadmap

Never edit roadmap status columns by hand. Sync them from topic folders:

```sh
python3 scripts/sync-roadmap.py courses/de-from-pt-br
python3 scripts/sync-roadmap.py courses/it-from-pt-br
python3 scripts/sync-roadmap.py courses/en-from-pt-br
python3 scripts/sync-roadmap.py courses/fr-from-pt-br
python3 scripts/sync-roadmap.py courses/es-from-pt-br
```

Check without writing:

```sh
python3 scripts/sync-roadmap.py --check courses/de-from-pt-br
python3 scripts/sync-roadmap.py --check courses/fr-from-pt-br
```

## Compile PDFs

Compile one topic:

```sh
scripts/compile-topic.sh --course courses/de-from-pt-br 1
scripts/compile-topic.sh --course courses/de-from-pt-br courses/de-from-pt-br/topics/a1/001-alfabeto-alemao-e-sons-basicos
```

Compile all topics in a course:

```sh
scripts/compile-all.sh courses/de-from-pt-br
```

Compile a review:

```sh
scripts/compile-review.sh --course courses/de-from-pt-br 001-010
```

Concatenate topic PDFs:

```sh
scripts/concat-topics.sh --course courses/de-from-pt-br 1 10
scripts/concat-topics.sh --course courses/en-from-pt-br 6 10
```

PDF outputs go under the selected course:

```txt
courses/<course-id>/output/pdf/
```

Prepare a compiled or concatenated PDF for printing. This keeps the original PDF and writes a numbered copy plus a booklet-imposed copy beside it:

```sh
scripts/prepare-print-pdf.sh courses/en-from-pt-br/output/pdf/concat/006-007-008-009-010-combined.pdf
```

Print booklet PDFs with duplex `flip on short side`.

## Supplements

Use supplements when a topic needs extra practice without changing the normal topic files.

Create supplement source under the topic:

```txt
courses/<course-id>/topics/<level>/<topic-folder>/supplements/<name>.json
```

Compile supplement source files:

```sh
python3 scripts/compile-supplement.py --course courses/de-from-pt-br 34 mastery-001
```

Compile supplement PDFs:

```sh
scripts/compile-supplement-pdf.sh --course courses/de-from-pt-br 34 mastery-001
```

Prepare supplement combined PDF for printing:

```sh
scripts/prepare-print-pdf.sh courses/de-from-pt-br/output/pdf/034-preposicoes-com-acusativo/supplements/mastery-001/combined.pdf
```

Generate supplement story audio:

```sh
.venv/bin/python scripts/generate-supplement-audio.py --course courses/de-from-pt-br 34 mastery-001
```

## Audio

The project uses Piper TTS. Voices are configured in each course `course.yaml`:

```yaml
target_voice: de_DE-karlsson-low
source_voice: pt_BR-cadu-medium
```

Install dependencies once:

```sh
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

Generate audio:

```sh
.venv/bin/python scripts/generate-audio.py --course courses/de-from-pt-br 104
```

Audio outputs go under:

```txt
courses/<course-id>/output/audio/<topic-folder>/
```

## Anki Export

Export all flashcards for a course into the course-wide package:

```sh
.venv/bin/python scripts/export-anki.py --course courses/de-from-pt-br
```

Output:

```txt
courses/<course-id>/output/exports/<course-output>.apkg
```

Export one topic into its own package. This is the safest command for independent topic-generation agents because it does not overwrite the course-wide package:

```sh
.venv/bin/python scripts/export-anki.py --course courses/de-from-pt-br 104
```

Output:

```txt
courses/<course-id>/output/exports/topics/<topic-folder>.apkg
```

Export selected topics together into a separate package:

```sh
.venv/bin/python scripts/export-anki.py --course courses/de-from-pt-br 99 100
```

Output:

```txt
courses/<course-id>/output/exports/selected/<course-output-stem>-099-100.apkg
```

Use `--output` only when you intentionally want a custom file path.

Deck metadata and course-wide output names come from `course.yaml`. Exports go under:

```txt
courses/<course-id>/output/exports/
```

## Course Configuration

Each course has a `course.yaml` like:

```yaml
id: de-from-pt-br
target_language: German
target_language_pt: alemão
target_locale: de_DE
source_language: Brazilian Portuguese
source_language_pt: português brasileiro
source_locale: pt_BR
target_voice: de_DE-karlsson-low
source_voice: pt_BR-cadu-medium
anki_deck_name: Alemão
anki_model_name: Alemão PT-BR (com áudio)
anki_output: alemao.apkg
story_heading: "## História em alemão"
target_word_field: german
```

## Content Rules

- Use Brazilian Portuguese for explanations, headings, labels, and instructions.
- Use the target language only where the learner should read or produce it.
- Markdown and YAML are the source of truth.
- Typst is only for local PDF rendering.
- Do not generate PDFs directly with AI.
- Do not copy exercise items into `test.yaml`; tests must use fresh contexts and sentences.
- New topics should pass `scripts/validate-content.py` with zero issues.
