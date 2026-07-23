"""Compara Hydros Histórico e Hydros Instantâneo."""

import pandas as pd

from src.services.hydros_engine import HydrosEngine


def resumir(nome, resultado):
    amdh = resultado["amdh"]
    print(f"\n=== {nome.upper()} ===")
    print("Contextos utilizados:", resultado["quantidade_contextos_utilizados"])
    print("Ehist:", resultado["ahist"]["Ehist"])
    print("Ehc:", resultado["aiec"]["Ehc"])
    print("Earg:", resultado["arg"]["Earg"])
    print("Eaps:", resultado["aps"]["Eaps"])
    print("D(Ui):", amdh["D(Ui)"])
    print("Score:", amdh["score_hibrido"])
    print("Confiança:", amdh["confianca"])
    print("Conflito:", amdh["indice_conflito"])
    print("Revisão humana:", amdh["revisao_humana_requerida"])


def main():
    df = pd.read_csv("data/historico_contexto_exemplo.csv")
    engine = HydrosEngine()

    historico = engine.executar(df, modo_execucao="historico")
    instantaneo = engine.executar(df, modo_execucao="instantaneo")

    resumir("Hydros Histórico", historico)
    resumir("Hydros Instantâneo", instantaneo)

    print("\n=== COMPARAÇÃO ===")
    print(
        "Mesma decisão:",
        historico["amdh"]["D(Ui)"] == instantaneo["amdh"]["D(Ui)"],
    )
    print(
        "Diferença de confiança:",
        round(
            historico["amdh"]["confianca"]
            - instantaneo["amdh"]["confianca"],
            4,
        ),
    )


if __name__ == "__main__":
    main()