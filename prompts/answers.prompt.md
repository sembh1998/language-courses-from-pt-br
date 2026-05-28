# Answers Prompt

Generate the complete contents of `answers.md` for a German learning topic.

Variables:
- Level: `{{LEVEL}}`
- Topic: `{{TOPIC}}`
- Language of explanation: `{{LANGUAGE_OF_EXPLANATION}}`
- Target student: `{{TARGET_STUDENT}}`

Inputs you may receive:
- `exercises.yaml`
- `test.yaml`
- `story.md`

Strict output rules:
- Output only the Markdown file content.
- Do not wrap the answer in code fences.
- Do not add comments, explanations, notes, or metadata outside the answer key.
- Keep the Markdown simple, clean, and AI-friendly.
- Include answer keys for exercises and tests.
- Include story question answers if `story.md` is provided.
- Use `{{LANGUAGE_OF_EXPLANATION}}` for brief notes.

Required structure:

# Answers: {{TOPIC}}

Level: {{LEVEL}}

## Exercises answer key

| ID | Answer | Note |
|---|---|---|
| exercise number or item | answer | short note |

## Test answer key

| ID | Answer | Points |
|---|---|---|
| question number | answer | points if available |

## Story questions

| Question | Answer |
|---|---|
| question | answer |
