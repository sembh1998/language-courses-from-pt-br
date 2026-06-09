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
- Use Portuguese section headings and table headers when `{{LANGUAGE_OF_EXPLANATION}}` is Brazilian Portuguese.
- Do not leave navigation labels such as Goal, Explanation, Examples, Common mistakes, Summary, Level, Translation, or Note in English.
- Write for `{{TARGET_STUDENT}}`.
- Keep content appropriate for `{{LEVEL}}`.
- Before writing, consider the topic difficulty and importance for the target student. For critical or difficult topics, make the lesson fuller with more examples, contrasts, and common mistakes. For simple topics, keep it shorter.
- Use the roadmap level, topic title, and subtópicos to decide how much explanation the lesson needs. Do not assume every topic is A1.
- Use page space well. If the topic is foundational, important, or error-prone, add a compact extra section such as `## Prática guiada`, `## Contraste rápido`, or `## Mini-checagem explicada` before the summary. Use this section for level-appropriate examples, guided patterns, short comparisons, or self-check items with answers/explanations.
- Avoid leaving most of the final lesson page empty when the topic can support more useful explanation or guided practice. Prefer useful examples and contrasts over filler text.

Required structure:

# {{TOPIC}}

Nível: {{LEVEL}}

## Objetivo

Um objetivo curto para a lição.

## Explicação

Uma explicação simples em `{{LANGUAGE_OF_EXPLANATION}}`.

## Exemplos

| Alemão | Tradução | Observação |
|---|---|---|
| Exemplo em alemão | Tradução | Observação curta |

## Erros comuns

- Erro comum 1
- Erro comum 2
- Erro comum 3

Optional, when useful for the topic importance/difficulty:

## Prática guiada

Exemplos guiados, contraste rápido, ou mini-checagem explicada em `{{LANGUAGE_OF_EXPLANATION}}`.

## Resumo

Um mini-resumo curto em `{{LANGUAGE_OF_EXPLANATION}}`.
