# Language Learning Content Generator

A local content-generation system for language-learning materials for Brazilian Portuguese speakers.

The repository is now multi-course: course-specific roadmaps, prompts, topics, reviews, and outputs live under `courses/<course-id>/`; shared scripts, schemas, and Typst templates stay at the repository root.

## Courses

```txt
courses/
├── de-from-pt-br/   # German from Brazilian Portuguese
├── it-from-pt-br/   # Italian from Brazilian Portuguese
├── en-from-pt-br/   # English from Brazilian Portuguese
└── fr-from-pt-br/   # French from Brazilian Portuguese
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
│   └── fr-from-pt-br/
├── schemas/
├── scripts/
├── templates/
├── requirements.txt
└── README.md
```

## Topic Files

Each generated topic folder should contain exactly these source files:

```txt
lesson.md
vocabulary.yaml
flashcards.yaml
exercises.yaml
test.yaml
story.md
answers.md
```

Example topic folder:

```txt
courses/de-from-pt-br/topics/a1/001-alfabeto-alemao-e-sons-basicos/
```

## Add A Topic

Choose a topic from the selected course roadmap, then scaffold the topic folder:

```sh
scripts/generate-topic.sh courses/de-from-pt-br/topics/a1/001-alfabeto-alemao-e-sons-basicos
```

Use the prompt files in the selected course:

```txt
courses/de-from-pt-br/prompts/
courses/it-from-pt-br/prompts/
courses/en-from-pt-br/prompts/
courses/fr-from-pt-br/prompts/
```

Italian, English, and French currently have starter prompt folders and roadmaps ready to be filled.

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
```

PDF outputs go under the selected course:

```txt
courses/<course-id>/output/pdf/
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
