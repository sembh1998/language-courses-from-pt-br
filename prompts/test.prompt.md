# Test Prompt

Generate the complete contents of `test.yaml` for a German learning topic.

Variables:
- Level: `{{LEVEL}}`
- Topic: `{{TOPIC}}`
- Language of explanation: `{{LANGUAGE_OF_EXPLANATION}}`
- Target student: `{{TARGET_STUDENT}}`

Strict output rules:
- Output only valid YAML.
- Do not wrap the answer in code fences.
- Do not add comments, explanations, notes, or metadata outside the YAML.
- Use exactly the field names shown below.
- Use `options` only for multiple-choice questions.
- Keep answers exact and easy to grade.
- Write for `{{TARGET_STUDENT}}`.
- Keep questions appropriate for `{{LEVEL}}`.

Required YAML shape:

topic: {{TOPIC}}
level: {{LEVEL}}
questions:
  - type: multiple_choice
    question: Which sentence is correct?
    options:
      - Ich sehe der Mann.
      - Ich sehe den Mann.
      - Ich sehe dem Mann.
    answer: Ich sehe den Mann.
