# Exercises Prompt

Generate the complete contents of `exercises.yaml` for a German learning topic.

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
- Use `options` only for multiple-choice items.
- Keep answers exact and easy to grade.
- Use instructions in `{{LANGUAGE_OF_EXPLANATION}}` or simple English.
- Write for `{{TARGET_STUDENT}}`.
- Keep exercises appropriate for `{{LEVEL}}`.

Required YAML shape:

topic: {{TOPIC}}
level: {{LEVEL}}
exercises:
  - type: fill_blank
    instruction: Complete with the correct article.
    items:
      - question: Ich sehe ___ Mann.
        answer: den
      - question: Sie kauft ___ Apfel.
        answer: einen

  - type: multiple_choice
    instruction: Choose the correct option.
    items:
      - question: Ich sehe ___ Hund.
        options:
          - der
          - den
          - dem
        answer: den
