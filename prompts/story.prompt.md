# Story Prompt

Generate the complete contents of `story.md` for a German learning topic.

Variables:
- Level: `{{LEVEL}}`
- Topic: `{{TOPIC}}`
- Language of explanation: `{{LANGUAGE_OF_EXPLANATION}}`
- Target student: `{{TARGET_STUDENT}}`

Strict output rules:
- Output only the Markdown file content.
- Do not wrap the answer in code fences.
- Do not add comments, explanations, notes, or metadata outside the story file.
- Keep the Markdown simple, clean, and AI-friendly.
- The story itself must be in German.
- Use `{{LANGUAGE_OF_EXPLANATION}}` for translations, vocabulary notes, and instructions.
- Write for `{{TARGET_STUDENT}}`.
- Keep vocabulary and sentence length appropriate for `{{LEVEL}}`.

Required structure:

# Story: {{TOPIC}}

Level: {{LEVEL}}

## German Story

A short German story.

## Line-by-line translation

| German | Translation |
|---|---|
| German sentence | Translation |

## Vocabulary notes

- German word or phrase = explanation or translation

## Comprehension questions

1. Question in German or `{{LANGUAGE_OF_EXPLANATION}}`
2. Question in German or `{{LANGUAGE_OF_EXPLANATION}}`
3. Question in German or `{{LANGUAGE_OF_EXPLANATION}}`
