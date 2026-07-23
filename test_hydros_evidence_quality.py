"""Teste de completude, confiança e exclusão de evidências desativadas."""

from __future__ import annotations

import pandas as pd
from src.services.hydros_engine import HydrosEngine


def main() -> None:
    df = pd.read_csv("data/historico_contexto_exemplo.csv")
    engine = HydrosEngine()

    historical = engine.processar(df, modo_execucao="historico")
    instantaneous = engine.processar(df, modo_execucao="instantaneo")

    assert historical["aclim"]["completude"] == 1.0
    assert historical["aclim"]["confianca_dados"] > 0.0
    assert historical["aclim"]["qualidade_dados"] > 0.0
    assert "Ehist" in historical["aiec"]["evidencias_ativas"]

    assert instantaneous["ahist"]["desativado"] is True
    assert instantaneous["ahist"]["qualidade"] == 0.0
    assert "Ehist" not in instantaneous["aiec"]["evidencias_ativas"]
    assert "Ehist" in instantaneous["aiec"]["evidencias_desativadas"]

    incomplete_df = df.copy()
    incomplete_df.loc[incomplete_df.index[-1], "loc"] = ""
    incomplete = engine.processar(incomplete_df, modo_execucao="historico")

    assert incomplete["ageo"]["completude"] == 0.5
    assert "loc" in incomplete["ageo"]["variaveis_ausentes"]
    assert incomplete["aiec"]["completude"] < 1.0

    print("\n=== QUALIDADE DAS EVIDÊNCIAS ===")
    print("Ageo completo:", historical["ageo"]["completude"])
    print("Ageo incompleto:", incomplete["ageo"]["completude"])
    print("Confiança dos dados histórica Aclim:", historical["aclim"]["confianca_dados"])
    print("Confiança dos dados instantânea Aclim:", instantaneous["aclim"]["confianca_dados"])
    print("Evidências ativas no instantâneo:", instantaneous["aiec"]["evidencias_ativas"])
    print("Evidências desativadas:", instantaneous["aiec"]["evidencias_desativadas"])
    print("QUALIDADE DAS EVIDÊNCIAS: OK")


if __name__ == "__main__":
    main()
