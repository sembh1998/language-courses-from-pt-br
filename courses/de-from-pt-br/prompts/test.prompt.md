# Test Prompt

Generate the complete contents of `test.yaml` for a German learning topic.

Variables:
- Level: `{{LEVEL}}`
- Topic: `{{TOPIC}}`
- Language of explanation: `{{LANGUAGE_OF_EXPLANATION}}`
- Target student: `{{TARGET_STUDENT}}`

Inputs you may receive:
- `exercises.yaml`

Strict output rules:
- Output only valid YAML.
- Do not wrap the answer in code fences.
- Do not add comments, explanations, notes, or metadata outside the YAML.
- Use exactly the field names shown below.
- Use `options` only for multiple-choice questions.
- Keep answers exact and easy to grade.
- Use questions and instructions in `{{LANGUAGE_OF_EXPLANATION}}` unless the actual item text is German.
- Write for `{{TARGET_STUDENT}}`.
- Keep questions appropriate for `{{LEVEL}}`.
- Before writing, consider the topic difficulty and importance for the target student. For critical or difficult topics, generate 14-20 questions. For medium topics, generate 10-14 questions. For simple topics, generate 8-10 questions.
- If `exercises.yaml` is provided, do not copy any exercise question, sentence, item, or exact answer pair into the test.
- The test may assess the same skill as the exercises, but it must use fresh contexts, vocabulary, names, sentence frames, and examples.
- Do not reuse the sample questions shown in this prompt.
- For `multiple_choice` questions, use exactly 3 options unless the question is explicitly true/false.
- For `multiple_choice` questions, distribute correct answers across option positions 1, 2, and 3 within the file. Do not make the correct option mostly position 1 or 2.
- Make distractors plausible, unique, and clearly wrong for one focused reason.

Required YAML shape:

topic: {{TOPIC}}
level: {{LEVEL}}
questions:
  - type: multiple_choice
    question: Qual frase está correta?
    options:
      - Ich sehe der Mann.
      - Ich sehe den Mann.
      - Ich sehe dem Mann.
    answer: Ich sehe den Mann.
