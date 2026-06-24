# Supplement Prompt

Generate one structured supplement JSON for an existing German learning topic.

Variables:
- Course root: `{{COURSE_ROOT}}`
- Topic order: `{{TOPIC_ORDER}}`
- Topic folder: `{{TOPIC_FOLDER}}`
- Supplement name: `{{SUPPLEMENT_NAME}}`
- Mode: `{{MODE}}` (`extra_story`, `extra_exercises`, `extra_test`, or `mastery`)
- Language of explanation: `{{LANGUAGE_OF_EXPLANATION}}`
- Target student: `{{TARGET_STUDENT}}`

Strict output rules:
- Output only JSON that follows `schemas/supplement.schema.json`.
- Do not wrap the answer in code fences.
- Do not add comments, explanations, notes, or metadata outside the JSON.
- Do not edit `content.json`, `lesson.md`, `exercises.yaml`, `test.yaml`, `story.md`, or `answers.md`.
- Save the source as `{{TOPIC_FOLDER}}/supplements/{{SUPPLEMENT_NAME}}.json`.
- After saving, run `python3 scripts/compile-supplement.py --course {{COURSE_ROOT}} {{TOPIC_ORDER}} {{SUPPLEMENT_NAME}}`.
- Read the existing topic first. Reuse its learning goals, level, vocabulary, examples, story patterns, exercises, and test scope as context, but do not copy existing exercise or test items.
- Use Brazilian Portuguese for explanations, instructions, headings, answers, and answer explanations.
- Use German only where the learner should read or produce German.
- Keep the German calibrated to the topic CEFR level.

Mode requirements:
- `extra_story`: generate `stories` only. Make the story much larger than the normal topic story, with meaningful repetition of the target pattern, line-by-line translations, vocabulary notes, comprehension questions, and guided story practice.
- `extra_exercises`: generate `exercises` only. Prefer 8-14 varied groups and 60-120 total items depending on topic importance and difficulty.
- `extra_test`: generate `test` only. Prefer 30-60 questions with varied formats and answer explanations.
- `mastery`: generate `exercises`, `test`, and `stories`. Prefer 10-16 exercise groups, 80-160 exercise items, 35-70 test questions, and one or more long stories.

Quality rules:
- Multiple-choice items must include `answer` and exactly two `distractors`; the compiler will distribute option positions.
- Every exercise and test item must include a useful `explanation` in Brazilian Portuguese.
- Exercise items and test items must not duplicate each other.
- Avoid making all items simple translations. Mix recognition, controlled production, correction, transformation, contrast, classification, ordering, and short-answer items where appropriate.
- For A1, larger means more simple repetitions and contexts, not harder syntax.
- For B2-C2, include nuance, register, reformulation, and error analysis when useful.

Required JSON shape:

```json
{
  "topic": "Nome do tópico",
  "level": "A1",
  "source_topic_order": 1,
  "mode": "mastery",
  "description": "Suplemento grande para dominar o tópico.",
  "exercises": [
    {
      "type": "fill_blank",
      "title": "Artigos em contexto",
      "instruction": "Complete as frases com a forma correta.",
      "items": [
        {
          "type": "fill_blank",
          "question": "Ich sehe ___ Mann.",
          "answer": "den",
          "explanation": "Depois de sehen, o objeto direto fica no acusativo."
        }
      ]
    }
  ],
  "test": [
    {
      "type": "multiple_choice",
      "question": "Ich sehe ___ Hund.",
      "answer": "den",
      "distractors": ["der", "dem"],
      "explanation": "Hund é objeto direto masculino no acusativo.",
      "points": 1
    }
  ],
  "stories": [
    {
      "title": "Um dia com muitos exemplos",
      "sections": [
        {
          "heading": "Cena 1",
          "sentences": [
            {
              "target": "Ich sehe den Hund.",
              "translation": "Eu vejo o cachorro."
            }
          ]
        }
      ],
      "vocabulary_notes": [
        {
          "target": "sehen",
          "note": "ver; costuma aparecer com objeto direto."
        }
      ],
      "questions": [
        {
          "question": "O que a pessoa vê?",
          "answer": "Ela vê o cachorro.",
          "explanation": "A informação aparece na frase Ich sehe den Hund."
        }
      ],
      "practice": [
        {
          "question": "Reescreva com Katze: Ich sehe den Hund.",
          "answer": "Ich sehe die Katze.",
          "explanation": "Katze é feminino; no acusativo fica die."
        }
      ]
    }
  ]
}
```
