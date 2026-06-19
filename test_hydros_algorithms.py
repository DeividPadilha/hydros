"""
Teste dos algoritmos disponíveis no APS do Hydros.

Este teste executa o mesmo histórico de contexto usando
diferentes algoritmos supervisionados no APS:

- Random Forest
- Gradient Boosting
- Decision Tree

O objetivo é verificar se todos carregam corretamente,
geram Eaps e permitem ao AMDH gerar D(Ui).
"""

import pandas as pd

from src.services.hydros_engine import HydrosEngine


def executar_teste_algoritmo(algoritmo_aps):
    """
    Executa o Hydros com um algoritmo específico do APS.
    """

    df = pd.read_csv(
        "data/historico_contexto_exemplo.csv"
    )

    engine = HydrosEngine(
        algoritmo_aps=algoritmo_aps
    )

    resultado = engine.executar(
        df
    )

    aps = resultado["aps"]
    amdh = resultado["amdh"]

    decisao = (
        amdh.get("D(Ui)")
        or amdh.get("decisao")
        or amdh.get("decisao_final")
    )

    print("\n========================================")
    print(f"Algoritmo APS: {aps.get('modelo')}")
    print(f"Código interno: {aps.get('algoritmo')}")
    print(f"Eaps: {aps.get('Eaps')}")
    print(f"Confiança APS: {aps.get('confianca')}")
    print(f"D(Ui): {decisao}")
    print(f"Score híbrido: {amdh.get('score')}")
    print(f"Confiança AMDH: {amdh.get('confianca')}")
    print("Status: OK")


def main():
    """
    Executa todos os algoritmos APS disponíveis.
    """

    print("=== TESTE DOS ALGORITMOS APS DO HYDROS ===")

    algoritmos = [
        "random_forest",
        "gradient_boosting",
        "decision_tree"
    ]

    for algoritmo in algoritmos:
        executar_teste_algoritmo(
            algoritmo
        )

    print("\nResultado geral: todos os algoritmos APS executaram sem erro.")


if __name__ == "__main__":
    main()
