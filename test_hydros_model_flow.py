"""
Teste do fluxo completo do modelo Hydros.

Este teste executa o fluxo conceitual:

H(Ui) -> C(t)
Aclim -> Eclim
Ahid  -> Ehid
Afen  -> Efen
Ageo  -> Egeo
Aprod -> Eprod
Ahist -> Ehist
AIEC  -> Ehc
ARG   -> Earg
APS   -> Eaps
AMDH  -> D(Ui)
"""

import pandas as pd

from src.services.hydros_engine import HydrosEngine


def main():
    """
    Executa o teste do fluxo completo.
    """

    df = pd.read_csv(
        "data/historico_contexto_exemplo.csv"
    )

    engine = HydrosEngine()

    resultados = engine.executar(
        df
    )

    print("\n=== FLUXO DO MODELO HYDROS ===\n")

    print("H(Ui): histórico de contexto carregado")
    print("Quantidade de contextos:", len(df))

    print("\nC(t): contexto atual")
    print(resultados["C(t)"])

    print("\nEclim:", resultados["aclim"]["Eclim"])
    print("Ehid :", resultados["ahid"]["Ehid"])
    print("Efen :", resultados["afen"]["Efen"])
    print("Egeo :", resultados["ageo"]["Egeo"])
    print("Eprod:", resultados["aprod"]["Eprod"])
    print("Ehist:", resultados["ahist"]["Ehist"])

    print("\nEhc:", resultados["aiec"]["Ehc"])
    print("Earg:", resultados["arg"]["Earg"])
    print("Eaps:", resultados["aps"]["Eaps"])

    print("\nD(Ui):", resultados["amdh"]["D(Ui)"])
    print("Score híbrido:", resultados["amdh"]["score_hibrido"])
    print("Confiança:", resultados["amdh"]["confianca"])

    print("\nExplicação:")
    print(resultados["amdh"]["explicacao"])


if __name__ == "__main__":
    main()
