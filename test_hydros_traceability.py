"""Teste funcional dos contratos e da rastreabilidade do Hydros."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.services.hydros_engine import HydrosEngine


def validar_resultado(resultado: dict, modo: str) -> None:
    assert "registro_execucao" in resultado
    assert "rastreabilidade" in resultado

    registro = resultado["registro_execucao"]
    assert registro["mode"] == modo
    assert registro["unit_id"]
    assert registro["analysis_timestamp"]
    assert len(registro["agents_executed"]) == 10

    evidencias_esperadas = {
        "aclim",
        "ahid",
        "afen",
        "ageo",
        "aprod",
        "ahist",
        "aiec",
        "arg",
        "aps",
    }
    assert set(registro["evidences"]) == evidencias_esperadas

    for evidence in registro["evidences"].values():
        assert evidence["semantic_condition"] in {
            "adequada",
            "atencao",
            "critica",
        }
        assert 0.0 <= evidence["confidence"] <= 1.0
        assert 0.0 <= evidence["completeness"] <= 1.0
        assert 0.0 <= evidence["quality"] <= 1.0

    decisao = registro["decision"]
    assert decisao["action"] == resultado["amdh"]["decisao_final"]
    assert decisao["automatic_execution"] is False
    assert decisao["user_status"] == "nao_avaliada"

    # O registro precisa ser exportável em JSON sem conversões externas.
    json.dumps(registro, ensure_ascii=False)

    if modo == "historico":
        assert registro["historical_window"]["history_used"] is True
        assert registro["evidences"]["ahist"]["active"] is True
    else:
        assert registro["historical_window"]["history_used"] is False
        assert registro["evidences"]["ahist"]["active"] is False
        assert registro["evidences"]["ahist"]["quality"] == 0.0


def main() -> None:
    data_path = Path("data/historico_contexto_exemplo.csv")
    if not data_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {data_path}")

    dataframe = pd.read_csv(data_path)
    engine = HydrosEngine()

    historico = engine.processar(dataframe, modo_execucao="historico")
    instantaneo = engine.processar(dataframe, modo_execucao="instantaneo")

    validar_resultado(historico, "historico")
    validar_resultado(instantaneo, "instantaneo")

    print("\n=== RASTREABILIDADE HYDROS ===")
    print("Execução histórica:", historico["registro_execucao"]["execution_id"])
    print("Execução instantânea:", instantaneo["registro_execucao"]["execution_id"])
    print("Agentes registrados: 10")
    print("Evidências registradas: 9")
    print("Decisão histórica:", historico["amdh"]["decisao_final"])
    print("Decisão instantânea:", instantaneo["amdh"]["decisao_final"])
    print("RASTREABILIDADE: OK")


if __name__ == "__main__":
    main()
