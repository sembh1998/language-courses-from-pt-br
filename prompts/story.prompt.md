# Story Prompt

Generate the complete contents of `story.md` for a German learning topic.

Variables:
- Level: `{{LEVEL}}`
- Topic: `{{TOPIC}}`
- Language of explanation: `{{LANGUAGE_OF_EXPLANATION}}`
- Target student: `{{TARGET_STUDENT}}`

Strict output rules:
- Output only the Markdown file content.
- Do not wrap the answer in code fences.
- Do not add comments, explanations, notes, or metadata outside the story file.
- Keep the Markdown simple, clean, and AI-friendly.
- The story itself must be in German.
- Use `{{LANGUAGE_OF_EXPLANATION}}` for translations, vocabulary notes, and instructions.
- Use Portuguese section headings and table headers when `{{LANGUAGE_OF_EXPLANATION}}` is Brazilian Portuguese.
- Do not leave navigation labels such as Story, German Story, Line-by-line translation, Vocabulary notes, Comprehension questions, Level, or Translation in English.
- Write for `{{TARGET_STUDENT}}`.
- Keep vocabulary and sentence length appropriate for `{{LEVEL}}`.
- Before writing, read `{{LEVEL}}` as the CEFR level from `roadmap.tsv` and evaluate the topic's learning load from its level, title, block, and subtópicos.
- Match the German story, questions, and guided practice to `{{LEVEL}}`; do not generate all stories as if they were A1.
- CEFR calibration:
  - A1: use very short transparent sentences, present tense, high-frequency words, simple connectors like und/aber, and mostly recognition or completion questions.
  - A2: use short connected paragraphs, daily-life contexts, Perfekt/modal/dative patterns when relevant, and simple why/when/how questions.
  - B1: use richer everyday narratives, opinions, reasons, subordinate clauses when relevant, and questions that require sentence-level answers.
  - B2: use more natural texts with nuance, contrast, cause/effect, abstract but accessible topics, and questions that require explanation or reformulation.
  - C1: use dense authentic-style prose, idiomatic phrasing when useful, argumentation, register awareness, and analytical questions.
  - C2: use sophisticated, near-authentic prose with nuance, implicit meaning, style/register analysis, and open-ended interpretation tasks.
- Scale the story by both `Difficulty` and `Importance`, not by difficulty alone. Important foundational topics should get more reading practice even if the grammar pattern is simple.
- Use the story page space well. Avoid a story section that leaves most of the page empty unless the topic is genuinely very small.
- For low difficulty and low/medium importance, write 1 short story section with about 6-8 German sentences, 4-6 translated lines, 4-6 vocabulary notes, and 3-4 comprehension questions.
- For medium difficulty or medium/high importance, write 2 connected story sections or scenes with about 10-14 German sentences total, 8-12 translated lines, 6-8 vocabulary notes, and 5-7 comprehension questions.
- For high difficulty or high importance, write 3 connected story sections or guided contexts with about 14-20 German sentences total, 10-16 translated lines, 8-10 vocabulary notes, and 6-8 comprehension questions.
- If the story is likely to spill onto a second PDF page, make the second page pedagogically useful: add more comprehension questions, short answer prompts, or guided production questions that reuse the target forms.
- For important topics, prefer 8-12 total questions split between comprehension and short production if that prevents a mostly empty story page.
- For important topics where there is still useful space, add an extra section `## Prática com a história` after comprehension questions. Use 4-8 short guided items that reuse the story language and the target pattern.
- Prefer meaningful repetition of the target pattern over longer prose. Recycle the key grammar/vocabulary naturally in different sentences and contexts.
- For A1, keep sentences short and transparent. A longer story should mean more simple sentences, not harder syntax.

Required structure:

# História: {{TOPIC}}

Nível: {{LEVEL}}

## História em alemão

Uma história em alemão dimensionada conforme `{{LEVEL}}`, dificuldade e importância do tópico.

## Tradução linha por linha

| Alemão | Tradução |
|---|---|
| Frase em alemão | Tradução |

## Notas de vocabulário

- Palavra ou expressão em alemão = explicação ou tradução

## Perguntas de compreensão

1. Pergunta em alemão ou em `{{LANGUAGE_OF_EXPLANATION}}`
2. Pergunta em alemão ou em `{{LANGUAGE_OF_EXPLANATION}}`
3. Pergunta em alemão ou em `{{LANGUAGE_OF_EXPLANATION}}`

Para tópicos importantes, adicione mais perguntas numeradas aqui. Inclua algumas perguntas de produção curta guiada quando for útil, como completar ou reescrever frases simples com o padrão-alvo.

## Prática com a história

Somente para tópicos importantes: adicione itens curtos de prática guiada em `{{LANGUAGE_OF_EXPLANATION}}` ou alemão adequado ao nível. Pule esta seção em tópicos pequenos/simples.
