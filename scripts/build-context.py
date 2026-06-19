#!/usr/bin/env python3
"""Build a compact, topic-specific generation context for content.json."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_course_config, resolve_course_root


CEFR_GUIDANCE = {
    "A1": "Frases curtas e transparentes; alta frequência; presente; reconhecimento e produção guiada.",
    "A2": "Parágrafos curtos conectados; situações cotidianas; perguntas simples de causa, tempo e modo.",
    "B1": "Narrativas e opiniões com razões; conectores e subordinadas relevantes; respostas em frases completas.",
    "B2": "Texto natural com nuance, contraste e causa/efeito; explicação e reformulação; atenção a registro.",
    "C1": "Prosa densa e autêntica; expressões idiomáticas úteis; argumentação, precisão e consciência de registro.",
    "C2": "Linguagem sofisticada e quase autêntica; implícitos, estilo, nuance e interpretação aberta.",
}

CONTENT_CONTRACT = """\
Retorne somente JSON válido para `content.json`, sem Markdown ou code fence.
Use `schemas/content.schema.json` como JSON Schema da resposta quando a API
oferecer structured outputs.
JSON compacto é aceito; espaços e indentação não são necessários.

O compilador gera lesson.md, vocabulary.yaml, flashcards.yaml, exercises.yaml,
test.yaml, story.md e answers.md. Não repita tabelas de gabarito nem a história
em dois formatos.

Campos:
- topic, level
- lesson: objective, explanation (Markdown), examples[{target, translation, note?}],
  common_mistakes[], guided_practice? (Markdown), summary
- vocabulary[]: id?, target, translation, type?, gender?, plural?, example,
  example_translation, note?, flashcard?; use flashcard: false quando inadequado
- flashcards[] opcional para cartões que não derivam do vocabulário
- exercises[]: type, title?, instruction, items[]
- test[]: itens
- cada item: type, question, answer, explanation, distractors? e points?
- múltipla escolha: answer correto + exatamente dois distractors; o compilador
  decide a posição da resposta
- story.sections[]: heading? e sentences[{target, translation}]
- story.vocabulary_notes[{target, note}]
- story.questions[{question, answer, explanation?}]
- story.practice[] opcional no mesmo formato

Tipos canônicos: multiple_choice, fill_blank, translation, matching,
short_answer, ordering, transformation, correction, classification,
production, contrast, identification, dictation.

Regras de qualidade:
- Explicações, instruções e observações em português brasileiro.
- Língua-alvo somente no que o aluno lê ou produz.
- Exercícios e teste usam contextos diferentes.
- Distratores plausíveis e errados por uma razão clara.
- Toda resposta de exercício e teste tem explicação pedagógica não vazia.
- Cada frase da história tem tradução alinhada; preserve naturalidade.
- Escale volume pela dificuldade e importância do tópico, sem texto de enchimento.
- Preserve literalmente strings como "null", "on", "off", "yes" e "no".
"""


def roadmap_row(course_root: Path, order: int) -> dict[str, str]:
    with (course_root / "roadmap.tsv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            try:
                if int(row["Ordem"]) == order:
                    return row
            except (KeyError, ValueError):
                continue
    raise SystemExit(f"Erro: ordem {order} não encontrada em {course_root / 'roadmap.tsv'}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Monta contexto compacto para gerar content.json.")
    parser.add_argument("topic", type=int, help="Ordem do tópico no roadmap")
    parser.add_argument("--course", default=None, help="ID ou pasta do curso")
    parser.add_argument("--json", action="store_true", help="Emite contexto estruturado em JSON")
    args = parser.parse_args()

    course_root = resolve_course_root(args.course)
    config = load_course_config(course_root)
    row = roadmap_row(course_root, args.topic)
    level = row["Nível"].upper()
    context = {
        "course": {
            "id": config["id"],
            "target_language": config.get("target_language", config["target_language_pt"]),
            "target_language_pt": config["target_language_pt"],
            "source_language": config.get("source_language", "Brazilian Portuguese"),
            "target_student": "falante de português brasileiro",
        },
        "roadmap": {
            "level": level,
            "order": int(row["Ordem"]),
            "block": row["Bloco"],
            "topic": row["Tópico Principal"],
            "subtopics": row["Subtópicos / Conteúdo"],
            "priority": row.get("Prioridade", ""),
        },
        "cefr": CEFR_GUIDANCE[level],
    }
    if args.json:
        print(json.dumps({**context, "contract": CONTENT_CONTRACT}, ensure_ascii=False, indent=2))
        return 0

    print("# Contexto de geração")
    print()
    print(yaml.safe_dump(context, allow_unicode=True, sort_keys=False).strip())
    print()
    print("# Contrato")
    print()
    print(CONTENT_CONTRACT.rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
