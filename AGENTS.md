# Agent Instructions

This project follows `roadmap.tsv`. Before generating content, read the roadmap
and select the requested topic from it.

## Roadmap Source Of Truth

Use `roadmap.tsv` as the planning source for topic generation.

Important columns:

- `Nível`: CEFR level or module group.
- `Ordem`: global topic order.
- `Bloco`: learning block/category.
- `Tópico Principal`: topic title.
- `Subtópicos / Conteúdo`: required scope for the topic.
- `Status`: generation status.
- `Material Gerado`: whether core topic files exist.
- `Flashcards`: whether flashcards were generated or skipped.
- `Exercícios`: whether exercises were generated.
- `Teste`: whether test content was generated.
- `Revisado`: whether a human reviewed it.

## Topic Selection

When asked to generate a topic:

1. Read `roadmap.tsv`.
2. Find the selected topic by `Ordem`, `Nível`, or `Tópico Principal`.
3. Use the roadmap row to determine level, block, title, and required subtópicos.
4. Create the topic folder under `topics/<level>/<order-topic-slug>/`.
5. Generate only the files required by this project.

Example folder names:

- `topics/a1/001-alfabeto-alemao-e-sons-basicos/`
- `topics/a1/004-cumprimentos-e-despedidas/`
- `topics/b1/091-verbos-com-preposicoes-fixas/`

Use three digits for `Ordem` so folders sort correctly.

## Required Topic Files

Each generated topic folder must contain:

```txt
lesson.md
vocabulary.yaml
flashcards.yaml
exercises.yaml
test.yaml
story.md
answers.md
```

Exception: if flashcards are not useful for the selected topic, still create
`flashcards.yaml`, but make it explicit that flashcards were intentionally
skipped.

Use this shape when skipping flashcards:

```yaml
topic: Topic Title
level: A1
cards: []
note: Flashcards skipped because this topic is better practiced through exercises and examples.
```

## Flashcard Evaluation

Before generating `flashcards.yaml`, decide whether flashcards are useful for
the selected topic.

Flashcards are usually useful for:

- Vocabulary topics.
- Fixed phrases.
- Verb forms.
- Articles and gender patterns.
- Irregular forms.
- Idioms and expressions.
- Prepositions with required cases.

Flashcards are often not enough or may be skipped for:

- Broad review topics.
- Writing tasks.
- Debate or speaking practice.
- Complex syntax topics that require full sentence production.
- Pronunciation topics that need audio or guided reading more than memorization.

If flashcards are useful, generate concise cards with a German front, translated
back, German example, and translation.

If flashcards are weak for the topic, skip them with `cards: []` and focus the
learning value in `lesson.md`, `exercises.yaml`, `story.md`, and `test.yaml`.

## Content Generation Rules

- Do not generate PDFs directly with AI.
- Markdown and YAML are the source of truth.
- Typst is only for rendering printable PDFs.
- Keep files small, editable, and reusable.
- Use the prompt files in `prompts/` as contracts for output format.
- Keep YAML valid and simple.
- Keep Markdown clean and predictable.
- Prefer Brazilian Portuguese for explanations unless asked otherwise.
- Generate content appropriate to the roadmap level.
- Do not invent roadmap topics outside `roadmap.tsv` unless explicitly asked.

## After Generation

After generating a topic:

1. Validate YAML files parse successfully.
2. Compile PDFs with `scripts/compile-topic.sh <topic-folder>` if Typst is available.
3. Report which files were created.
4. Report whether flashcards were generated or intentionally skipped, and why.
5. Do not edit `roadmap.tsv` unless explicitly asked.
