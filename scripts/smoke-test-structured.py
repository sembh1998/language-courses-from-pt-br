#!/usr/bin/env python3
"""End-to-end smoke test for structured topic and review compilers."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], cwd=REPO_ROOT, check=True)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="language-content-smoke-") as temp:
        course = Path(temp) / "course"
        topic = course / "topics" / "a1" / "001-artigos-definidos"
        review = course / "reviews" / "001-010"
        topic.mkdir(parents=True)
        review.mkdir(parents=True)

        shutil.copy(REPO_ROOT / "courses" / "de-from-pt-br" / "course.yaml", course / "course.yaml")
        shutil.copy(REPO_ROOT / "templates" / "content.example.json", topic / "content.json")

        header = (
            "Nível\tOrdem\tBloco\tTópico Principal\tSubtópicos / Conteúdo\tStatus\t"
            "Prioridade\tMaterial Gerado\tFlashcards\tExercícios\tTeste\tRevisado"
        )
        rows = [
            f"A1\t{order}\tBloco\tTópico {order}\tConteúdo {order}\tConcluído\tAlta\tSim\tSim\tSim\tSim\t"
            for order in range(1, 11)
        ]
        (course / "roadmap.tsv").write_text("\n".join([header, *rows]) + "\n", encoding="utf-8")

        review_questions = []
        for index in range(1, 21):
            if index % 3 == 1:
                review_questions.append(
                    {
                        "type": "multiple_choice",
                        "question": f"Qual opção é a resposta correta do item {index}?",
                        "answer": f"correta {index}",
                        "distractors": [f"distrator A {index}", f"distrator B {index}"],
                        "explanation": f"A resposta correta do item {index} foi definida no conteúdo.",
                    }
                )
            else:
                review_questions.append(
                    {
                        "type": "short_answer",
                        "question": f"Responda ao item {index}.",
                        "answer": f"resposta {index}",
                        "explanation": f"Explicação pedagógica do item {index}.",
                    }
                )
        (review / "review.json").write_text(
            json.dumps(
                {"topic": "Revisão 001-010", "level": "A1", "questions": review_questions},
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        run("scripts/compile-content.py", "--course", str(course), str(topic))
        run("scripts/compile-content.py", "--check", "--course", str(course), str(topic))
        run("scripts/validate-content.py", str(topic))
        run("scripts/compile-review-content.py", "--course", str(course), str(review))
        run("scripts/compile-review-content.py", "--check", "--course", str(course), str(review))
        run("scripts/validate-reviews.py", str(course))

    print("Structured content smoke test OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
