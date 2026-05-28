# Flashcards Prompt

Generate the complete contents of `flashcards.yaml` for a German learning topic.

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
- Use `{{LANGUAGE_OF_EXPLANATION}}` for card backs and example translations.
- Write for `{{TARGET_STUDENT}}`.
- Keep cards short and appropriate for `{{LEVEL}}`.

Required YAML shape:

topic: {{TOPIC}}
level: {{LEVEL}}
cards:
  - front: der Mann
    back: o homem
    example: Ich sehe den Mann.
    example_translation: Eu vejo o homem.
