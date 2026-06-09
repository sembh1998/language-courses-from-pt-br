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
- Use Portuguese section headings and table headers when `{{LANGUAGE_OF_EXPLANATION}}` is Brazilian Portuguese.
- Do not leave navigation labels such as Answers, Exercises answer key, Test answer key, Story questions, Level, Answer, Note, Points, or Question in English.
- Every exercise and test answer row must include a short explanation in `{{LANGUAGE_OF_EXPLANATION}}`; do not leave explanation/note cells blank.
- For test answers, include both the explanation and the points.

Required structure:

# Respostas: {{TOPIC}}

Nível: {{LEVEL}}

## Gabarito dos exercícios

| ID | Resposta | Explicação |
|---|---|---|
| número do exercício ou item | resposta | explicação curta |

## Gabarito do teste

| ID | Resposta | Explicação | Pontos |
|---|---|---|---|
| número da questão | resposta | explicação curta | pontos, se houver |

## Perguntas da história

| Pergunta | Resposta |
|---|---|
| pergunta | resposta |
