# German Learning Content Generator

A local content-generation system for German learning materials.

The goal is to generate editable German lessons from reusable Markdown and YAML
source files, then render printable PDFs locally with Typst. AI models should
generate the source content only, not the final PDFs.

```txt
topic folder
↓
AI-generated Markdown/YAML
↓
Typst templates
↓
local PDF output
```

## Project Goal

This project helps create German learning materials consistently and cheaply.
Each topic can contain lessons, vocabulary, flashcards, exercises, tests,
stories, and answer keys.

The content is designed for manual editing and repeated reuse. Markdown files
are human-readable. YAML files hold structured data. Typst templates render the
printable PDFs.

## Folder Structure

```txt
german-learning-content/
├── README.md
├── topics/
│   ├── a1/
│   │   └── 001-alfabeto-alemao-e-sons-basicos/
│   │       ├── lesson.md
│   │       ├── vocabulary.yaml
│   │       ├── flashcards.yaml
│   │       ├── exercises.yaml
│   │       ├── test.yaml
│   │       ├── story.md
│   │       └── answers.md
│   ├── a2/
│   ├── b1/
│   ├── b2/
│   ├── c1/
│   └── c2/
├── templates/
│   ├── lesson.typ
│   ├── flashcards.typ
│   ├── exercises.typ
│   ├── test.typ
│   └── story.typ
├── prompts/
│   ├── lesson.prompt.md
│   ├── vocabulary.prompt.md
│   ├── flashcards.prompt.md
│   ├── exercises.prompt.md
│   ├── test.prompt.md
│   ├── story.prompt.md
│   └── answers.prompt.md
├── scripts/
│   ├── generate-topic.sh
│   ├── compile-topic.sh
│   └── compile-all.sh
└── output/
    ├── pdf/
    └── exports/
```

## Source Files

Each real topic folder should contain exactly these source files:

```txt
lesson.md
vocabulary.yaml
flashcards.yaml
exercises.yaml
test.yaml
story.md
answers.md
```

Markdown files are for prose content:

- `lesson.md`: lesson explanation, examples, mistakes, summary
- `story.md`: short German story, translation, vocabulary notes, questions
- `answers.md`: answer keys for exercises, tests, and story questions

YAML files are for structured reusable data:

- `vocabulary.yaml`: words and examples
- `flashcards.yaml`: card fronts, backs, examples
- `exercises.yaml`: practice exercises
- `test.yaml`: test questions

## How To Add A New Topic

Choose the topic from `roadmap.tsv`, then create a topic folder with the helper script:

```sh
scripts/generate-topic.sh topics/a1/001-alfabeto-alemao-e-sons-basicos
```

Or create the folder manually:

```sh
mkdir -p topics/a1/001-alfabeto-alemao-e-sons-basicos
touch topics/a1/001-alfabeto-alemao-e-sons-basicos/lesson.md
touch topics/a1/001-alfabeto-alemao-e-sons-basicos/vocabulary.yaml
touch topics/a1/001-alfabeto-alemao-e-sons-basicos/flashcards.yaml
touch topics/a1/001-alfabeto-alemao-e-sons-basicos/exercises.yaml
touch topics/a1/001-alfabeto-alemao-e-sons-basicos/test.yaml
touch topics/a1/001-alfabeto-alemao-e-sons-basicos/story.md
touch topics/a1/001-alfabeto-alemao-e-sons-basicos/answers.md
```

Use lower-case folder names with a three-digit roadmap order prefix, such as
`001-alfabeto-alemao-e-sons-basicos` or `022-acusativo-objeto-direto`.

## How To Generate Content With AI

Use the prompt files in `prompts/`. Each prompt is designed for one output file.

Replace these variables before sending the prompt to an AI model:

```txt
{{LEVEL}}
{{TOPIC}}
{{LANGUAGE_OF_EXPLANATION}}
{{TARGET_STUDENT}}
```

Example values:

```txt
{{LEVEL}} = A1
{{TOPIC}} = Greetings and Introductions
{{LANGUAGE_OF_EXPLANATION}} = Brazilian Portuguese
{{TARGET_STUDENT}} = adult Brazilian Portuguese speaker learning German
```

Example workflow for one topic:

1. Use `prompts/lesson.prompt.md` and save the AI output to `lesson.md`.
2. Use `prompts/vocabulary.prompt.md` and save the AI output to `vocabulary.yaml`.
3. Use `prompts/flashcards.prompt.md` and save the AI output to `flashcards.yaml`.
4. Use `prompts/exercises.prompt.md` and save the AI output to `exercises.yaml`.
5. Use `prompts/test.prompt.md` and save the AI output to `test.yaml`.
6. Use `prompts/story.prompt.md` and save the AI output to `story.md`.
7. Use `prompts/answers.prompt.md` and save the AI output to `answers.md`.

The prompts instruct the AI to output only the requested Markdown or YAML file
content. Do not ask the AI to produce PDFs.

## How To Compile PDFs With Typst

Install the Typst CLI, then compile one topic:

```sh
scripts/compile-topic.sh topics/a1/001-alfabeto-alemao-e-sons-basicos
```

Compile all topic folders:

```sh
scripts/compile-all.sh
```

The generated PDFs are written to:

```txt
output/pdf/<topic-folder>/
```

Example output:

```txt
output/pdf/001-alfabeto-alemao-e-sons-basicos/lesson.pdf
output/pdf/001-alfabeto-alemao-e-sons-basicos/flashcards.pdf
output/pdf/001-alfabeto-alemao-e-sons-basicos/exercises.pdf
output/pdf/001-alfabeto-alemao-e-sons-basicos/test.pdf
output/pdf/001-alfabeto-alemao-e-sons-basicos/story.pdf
```

The scripts run simple Typst commands like:

```sh
typst compile --root . templates/lesson.typ output/pdf/001-alfabeto-alemao-e-sons-basicos/lesson.pdf --input topic=../topics/a1/001-alfabeto-alemao-e-sons-basicos
```

## Recommended Workflow

1. Choose a topic from `roadmap.tsv`.
2. Create a topic folder under `topics/<level>/` using the roadmap order and title.
3. Generate Markdown and YAML using the prompt templates.
4. Save the generated content into the topic folder.
5. Manually review and edit the content.
6. Validate that YAML files are parseable.
7. Compile PDFs locally with Typst.
8. Keep editing the source Markdown/YAML, then recompile PDFs as needed.

## Examples

Create a new topic:

```sh
scripts/generate-topic.sh topics/a1/001-alfabeto-alemao-e-sons-basicos
```

Compile one topic:

```sh
scripts/compile-topic.sh topics/a1/001-alfabeto-alemao-e-sons-basicos
```

Compile everything:

```sh
scripts/compile-all.sh
```

Validate YAML with Ruby if available:

```sh
ruby -e 'require "yaml"; ARGV.each { |f| YAML.load_file(f); puts "ok #{f}" }' topics/a1/001-alfabeto-alemao-e-sons-basicos/*.yaml
```

## Important Design Rules

- Do not generate PDFs directly with the AI.
- Do not use `.docx` as the source format.
- Markdown and YAML are the source of truth.
- Typst is only for rendering printable PDFs.
- Keep files small and reusable.
- The content should be easy to edit manually.
- The system should work locally.
- Prefer simple scripts over complex frameworks.
- Avoid unnecessary dependencies.
