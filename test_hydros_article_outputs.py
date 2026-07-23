"""Teste dos artefatos experimentais destinados ao artigo."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from gerar_resultados_artigo import SAIDA, main

ARQUIVOS_ESPERADOS = [
    "table_main_metrics.csv",
    "table_divergent_cases.csv",
    "table_reference_positive_events.csv",
    "table_actions_without_reference_support.csv",
    "figure_metrics_comparison.png",
    "figure_binary_confusion_matrix_historico.png",
    "figure_binary_confusion_matrix_instantaneo.png",
    "figure_reference_event_detection.png",
    "figure_governance_indicators.png",
    "experimental_results_summary.md",
]


def testar_arquivos() -> None:
    ausentes = [nome for nome in ARQUIVOS_ESPERADOS if not (SAIDA / nome).exists()]
    if ausentes:
        raise AssertionError("Artefatos ausentes: " + ", ".join(ausentes))

    vazios = [
        nome
        for nome in ARQUIVOS_ESPERADOS
        if (SAIDA / nome).stat().st_size == 0
    ]
    if vazios:
        raise AssertionError("Artefatos vazios: " + ", ".join(vazios))


def testar_conteudo() -> tuple[int, int, int]:
    metricas = pd.read_csv(SAIDA / "table_main_metrics.csv")
    divergencias = pd.read_csv(SAIDA / "table_divergent_cases.csv")
    positivos = pd.read_csv(SAIDA / "table_reference_positive_events.csv")

    if set(metricas["modo"]) != {"historico", "instantaneo"}:
        raise AssertionError("A tabela de métricas não contém os dois modos.")

    vantagem_hist = int(
        divergencias["classificacao_divergencia"].eq("vantagem_historico").sum()
    )
    vantagem_inst = int(
        divergencias["classificacao_divergencia"].eq("vantagem_instantaneo").sum()
    )

    if len(divergencias) != 6:
        raise AssertionError(
            f"Esperadas 6 divergências nos resultados atuais; obtidas {len(divergencias)}."
        )
    if vantagem_hist != 4 or vantagem_inst != 2:
        raise AssertionError(
            "Classificação inesperada das divergências: "
            f"Histórico={vantagem_hist}, Instantâneo={vantagem_inst}."
        )
    if len(positivos) != 11:
        raise AssertionError(
            f"Esperados 11 eventos positivos de referência; obtidos {len(positivos)}."
        )

    return len(divergencias), vantagem_hist, vantagem_inst


def main_test() -> None:
    main()
    testar_arquivos()
    n_div, vantagem_hist, vantagem_inst = testar_conteudo()

    print("\n=== VALIDAÇÃO DOS ARTEFATOS DO ARTIGO ===")
    print(f"Arquivos validados: {len(ARQUIVOS_ESPERADOS)}")
    print(f"Divergências validadas: {n_div}")
    print(f"Favoráveis ao Histórico: {vantagem_hist}")
    print(f"Favoráveis ao Instantâneo: {vantagem_inst}")
    print("Tabelas, figuras e síntese: OK")
    print("VALIDAÇÃO DOS ARTEFATOS: OK")


if __name__ == "__main__":
    main_test()
