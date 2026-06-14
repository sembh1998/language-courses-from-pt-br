# Vocabulary Prompt

Generate the complete contents of `vocabulary.yaml` for a German learning topic.

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
- Use `null` for `gender` and `plural` when they do not apply.
- Use high-frequency German words and phrases for `{{LEVEL}}`.
- Use `{{LANGUAGE_OF_EXPLANATION}}` for translations.
- Write for `{{TARGET_STUDENT}}`.

Required YAML shape:

topic: {{TOPIC}}
level: {{LEVEL}}
words:
  - german: der Mann
    translation: o homem
    type: noun
    gender: masculine
    plural: die Männer
    example: Ich sehe den Mann.
    example_translation: Eu vejo o homem.
