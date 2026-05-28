# Lesson Prompt

Generate the complete contents of `lesson.md` for a German learning topic.

Variables:
- Level: `{{LEVEL}}`
- Topic: `{{TOPIC}}`
- Language of explanation: `{{LANGUAGE_OF_EXPLANATION}}`
- Target student: `{{TARGET_STUDENT}}`

Strict output rules:
- Output only the Markdown file content.
- Do not wrap the answer in code fences.
- Do not add comments, explanations, notes, or metadata outside the lesson.
- Keep the Markdown simple, clean, and AI-friendly.
- Use German only for German examples.
- Use `{{LANGUAGE_OF_EXPLANATION}}` for explanations, translations, mistakes, and summary.
- Write for `{{TARGET_STUDENT}}`.
- Keep content appropriate for `{{LEVEL}}`.

Required structure:

# {{TOPIC}}

Level: {{LEVEL}}

## Goal

One short objective for the lesson.

## Explanation

A simple explanation in `{{LANGUAGE_OF_EXPLANATION}}`.

## Examples

| German | Translation | Note |
|---|---|---|
| German example | Translation | Short note |

## Common mistakes

- Common mistake 1
- Common mistake 2
- Common mistake 3

## Summary

A short mini summary in `{{LANGUAGE_OF_EXPLANATION}}`.
