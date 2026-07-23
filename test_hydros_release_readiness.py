"""Verifica se o projeto está pronto para auditoria e congelamento."""

from __future__ import annotations

import json
from pathlib import Path

from src.config.hydros_terms import VERSAO_ARQUITETURA

ROOT = Path(__file__).resolve().parent

REQUIRED = [
    "README.md",
    "STATUS_HYDROS.md",
    "DOCUMENTACAO_CODIGO_HYDROS.md",
    "REPRODUCIBILITY.md",
    "CHANGELOG.md",
    "requirements.txt",
    "ontology/hydros_onto.ttl",
    "src/ontology/hydros_onto.py",
    "src/core/contracts.py",
    "src/core/evidence_quality.py",
    "src/core/irrigation_state.py",
    "src/services/hydros_engine.py",
    "src/services/interface_adapter.py",
    "src/integrations/dssat_adapter.py",
    "src/models/aps_model_metadata.json",
    "run_dssat_comparison.py",
    "diagnostico_resultados.py",
    "gerar_resultados_artigo.py",
    "run_hydros_validation.py",
    "freeze_hydros_release.py",
]


def main() -> None:
    missing = [relative for relative in REQUIRED if not (ROOT / relative).exists()]
    if missing:
        raise AssertionError("Arquivos ausentes: " + ", ".join(missing))

    if VERSAO_ARQUITETURA != "0.3.0-agentic":
        raise AssertionError(
            f"Versão inesperada da arquitetura: {VERSAO_ARQUITETURA}"
        )

    metadata = json.loads(
        (ROOT / "src/models/aps_model_metadata.json").read_text(
            encoding="utf-8"
        )
    )
    if metadata.get("scientific_status") != (
        "modelo_legado_requer_retreinamento_temporal"
    ):
        raise AssertionError(
            "O status científico do APS legado não está registrado."
        )

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    required_phrases = [
        "Hydros Histórico",
        "Hydros Instantâneo",
        "benchmark de simulação",
        "não aciona equipamentos",
        "prova de conceito",
    ]
    absent_phrases = [
        phrase for phrase in required_phrases if phrase not in readme
    ]
    if absent_phrases:
        raise AssertionError(
            "Conceitos ausentes no README: " + ", ".join(absent_phrases)
        )

    print("\n=== PRONTIDÃO PARA RELEASE ===")
    print(f"Versão da arquitetura: {VERSAO_ARQUITETURA}")
    print(f"Arquivos obrigatórios: {len(REQUIRED)}")
    print("Status científico do APS: registrado")
    print("Escopo e limitações: documentados")
    print("PRONTIDÃO PARA RELEASE: OK")


if __name__ == "__main__":
    main()
