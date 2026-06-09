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
- Use instructions only in `{{LANGUAGE_OF_EXPLANATION}}`; do not use English instructions when the explanation language is Brazilian Portuguese.
- Write for `{{TARGET_STUDENT}}`.
- Keep exercises appropriate for `{{LEVEL}}`.
- Before writing, consider the topic difficulty and importance for the target student. For critical or difficult topics, generate 6-8 varied exercise groups. For medium topics, generate 4-6 groups. For simple topics, generate 3-4 groups.
- Vary exercise item wording and examples; do not repeat the same prompt with only a small name/place change.
- For `multiple_choice` items, use exactly 3 options unless the exercise is explicitly true/false.
- For `multiple_choice` items, distribute correct answers across option positions 1, 2, and 3 within the file. Do not make the correct option mostly position 1 or 2.
- Make distractors plausible, unique, and clearly wrong for one focused reason.

Required YAML shape:

topic: {{TOPIC}}
level: {{LEVEL}}
exercises:
  - type: fill_blank
    instruction: Complete com o artigo correto.
    items:
      - question: Ich sehe ___ Mann.
        answer: den
      - question: Sie kauft ___ Apfel.
        answer: einen

  - type: multiple_choice
    instruction: Escolha a opção correta.
    items:
      - question: Ich sehe ___ Hund.
        options:
          - der
          - den
          - dem
        answer: den
