#!/usr/bin/env python3
"""Build compact context for a cumulative review.json generation call."""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_course_config, resolve_course_root


def target_words(course_root: Path, order: int, field: str) -> list[str]:
    matches = list((course_root / "topics").glob(f"*/{order:03d}-*/vocabulary.yaml"))
    if not matches:
        return []
    data = yaml.safe_load(matches[0].read_text(encoding="utf-8")) or {}
    return [
        str(item[field])
        for item in data.get("words", [])
        if isinstance(item, dict) and item.get(field)
    ][:12]


def main() -> int:
    parser = argparse.ArgumentParser(description="Monta contexto compacto para uma revisão.")
    parser.add_argument("range", help="Faixa no formato 001-010")
    parser.add_argument("--course", default=None, help="ID ou pasta do curso")
    args = parser.parse_args()

    match = re.fullmatch(r"(\d{3})-(\d{3})", args.range)
    if not match:
        raise SystemExit("Erro: use uma faixa como 001-010")
    start, end = map(int, match.groups())
    if start > end:
        raise SystemExit("Erro: início da faixa maior que o fim")

    course_root = resolve_course_root(args.course)
    config = load_course_config(course_root)
    rows = []
    with (course_root / "roadmap.tsv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            try:
                order = int(row["Ordem"])
            except (KeyError, ValueError):
                continue
            if start <= order <= end:
                rows.append(
                    {
                        "order": order,
                        "level": row["Nível"],
                        "topic": row["Tópico Principal"],
                        "subtopics": row["Subtópicos / Conteúdo"],
                        "priority": row.get("Prioridade", ""),
                        "vocabulary": target_words(course_root, order, config["target_word_field"]),
                    }
                )
    if len(rows) != end - start + 1:
        raise SystemExit("Erro: a faixa não corresponde a linhas contínuas do roadmap")

    context = {
        "course": config["id"],
        "target_language": config.get("target_language", config["target_language_pt"]),
        "source_language": "português brasileiro",
        "range": args.range,
        "topics": rows,
    }
    print("# Contexto da revisão")
    print()
    print(yaml.safe_dump(context, allow_unicode=True, sort_keys=False).strip())
    print()
    print("# Contrato")
    print()
    print(
        """Retorne somente JSON válido para `review.json`, sem Markdown ou code
fence, com `topic`, `level` e
`questions` (20-30 itens). Cada item contém `type`, `question`, `answer`,
`explanation`, `points` opcional e, para múltipla escolha, exatamente dois
`distractors`. O compilador cria IDs, distribui a resposta nas três posições e
gera test.yaml e answers.md.

Use `schemas/review-content.schema.json` como JSON Schema da resposta quando a
API oferecer structured outputs.
JSON compacto é aceito; espaços e indentação não são necessários.

Misture todos os tópicos e intercale-os. Reaproveite habilidades e vocabulário,
mas crie frases, contextos e pares pergunta/resposta novos. Use português
brasileiro nas instruções e explicações e a língua-alvo apenas no que o aluno
deve ler ou produzir. Priorize contrastes, formas fáceis de esquecer e itens de
alta prioridade."""
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
