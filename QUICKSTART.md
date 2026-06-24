# Quick Agent Map

Use this file first when you are a fresh or weaker agent. It tells you where things live and which command to run. Do not guess paths.

## Mental Model

- Course source lives under `courses/<course-id>/`.
- Topic source lives under `courses/<course-id>/topics/<level>/<three-digit-order>-<slug>/`.
- Generated PDFs/audio/Anki live under `courses/<course-id>/output/`.
- Root `scripts/`, `schemas/`, and `templates/` are shared by all courses.
- Default course is German: `courses/de-from-pt-br`.
- Other courses: `en-from-pt-br`, `it-from-pt-br`, `fr-from-pt-br`, `es-from-pt-br`.

## Most Common User Requests

| User asks | Do this | Main output |
|---|---|---|
| `compile topic 34` | `scripts/compile-topic.sh --course courses/de-from-pt-br 34` | `courses/de-from-pt-br/output/pdf/<topic>/combined.pdf` |
| `combine topics 6 to 10 on en` | `scripts/concat-topics.sh --course courses/en-from-pt-br 6 10` | `courses/en-from-pt-br/output/pdf/concat/006-007-008-009-010-combined.pdf` |
| `make numbered/booklet` | `scripts/prepare-print-pdf.sh <path/to/combined.pdf>` | `<name>-numbered.pdf`, `<name>-booklet.pdf` |
| `generate audio for topic 34` | `.venv/bin/python scripts/generate-audio.py --course courses/de-from-pt-br 34` | `courses/de-from-pt-br/output/audio/<topic>/` |
| `expand topic 34` | Create a supplement, not normal topic edits | `topics/.../supplements/<name>*` |
| `compile supplement mastery` | `python3 scripts/compile-supplement.py --course courses/de-from-pt-br 34 mastery-001` | `topics/.../supplements/mastery-001-*.yaml/md` |
| `compile supplement PDF` | `scripts/compile-supplement-pdf.sh --course courses/de-from-pt-br 34 mastery-001` | `output/pdf/<topic>/supplements/mastery-001/combined.pdf` |
| `audio for supplement` | `.venv/bin/python scripts/generate-supplement-audio.py --course courses/de-from-pt-br 34 mastery-001` | `output/audio/<topic>/supplements/mastery-001-story.wav` |

## Topic Lookup

For topic number `N`, find folder by glob:

```txt
courses/<course-id>/topics/*/<NNN>-*
```

Examples:

```txt
courses/de-from-pt-br/topics/*/034-*
courses/en-from-pt-br/topics/*/006-*
```

If you need roadmap details, search the tab-delimited `Ordem` column:

```regex
^([^\t]*\t)0?34\t
```

## Normal Topic Workflow

Use this when creating or updating the normal lesson content.

1. Read roadmap/context:

```sh
python3 scripts/build-context.py --course courses/<course-id> <order>
```

2. Create or update only `content.json` in the topic folder.

3. Compile source files:

```sh
python3 scripts/compile-content.py --course courses/<course-id> <order>
```

4. Validate:

```sh
python3 scripts/validate-content.py courses/<course-id>/topics/<level>/<topic-folder>
```

Do not hand-edit compiled normal files when `content.json` exists: `lesson.md`, `vocabulary.yaml`, `flashcards.yaml`, `exercises.yaml`, `test.yaml`, `story.md`, `answers.md`.

## Supplement Workflow

Use this when the user says `expand`, `extra exercises`, `extra test`, `bigger story`, `mastery`, or similar.

Do not edit the normal topic files. Supplements live here:

```txt
courses/<course-id>/topics/<level>/<topic-folder>/supplements/
```

Create semantic source:

```txt
supplements/<name>.json
```

Compile learner files:

```sh
python3 scripts/compile-supplement.py --course courses/<course-id> <order> <name>
```

Compile PDFs:

```sh
scripts/compile-supplement-pdf.sh --course courses/<course-id> <order> <name>
```

Prepare numbered/booklet PDF:

```sh
scripts/prepare-print-pdf.sh courses/<course-id>/output/pdf/<topic-folder>/supplements/<name>/combined.pdf
```

Generate supplement story audio:

```sh
.venv/bin/python scripts/generate-supplement-audio.py --course courses/<course-id> <order> <name>
```

## PDF Workflow

One topic:

```sh
scripts/compile-topic.sh --course courses/<course-id> <order>
```

Range or selected topics:

```sh
scripts/concat-topics.sh --course courses/<course-id> <start> <end>
scripts/concat-topics.sh --course courses/<course-id> <topic-a> <topic-b> <topic-c>
```

Number and booklet any `combined.pdf`:

```sh
scripts/prepare-print-pdf.sh <path/to/combined.pdf>
```

Print booklet PDFs with duplex `flip on short side`.

## Output Path Patterns

Normal topic PDFs:

```txt
courses/<course-id>/output/pdf/<topic-folder>/combined.pdf
```

Concat PDFs:

```txt
courses/<course-id>/output/pdf/concat/<orders>-combined.pdf
```

Supplement PDFs:

```txt
courses/<course-id>/output/pdf/<topic-folder>/supplements/<name>/combined.pdf
```

Print-prepped PDFs:

```txt
<combined-stem>-numbered.pdf
<combined-stem>-booklet.pdf
```

Normal audio:

```txt
courses/<course-id>/output/audio/<topic-folder>/
```

Supplement audio:

```txt
courses/<course-id>/output/audio/<topic-folder>/supplements/
```

## Do Not Delete Or Edit Casually

- `courses/<course-id>/topics/`: source content.
- `courses/<course-id>/roadmap.tsv`: sync via script, do not hand-edit status columns.
- `content.json`: semantic source for structured topics.
- `schemas/`, `scripts/`, `templates/`: shared tooling.

Root `output/` is old/generated if it exists. Current generated files belong under `courses/<course-id>/output/`.
