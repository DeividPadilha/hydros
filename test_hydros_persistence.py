"""Teste da persistência completa e da avaliação humana do Hydros."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from src.database.database import Database
from src.services.hydros_engine import HydrosEngine


def main() -> None:
    data_path = Path("data/historico_contexto_exemplo.csv")
    if not data_path.exists():
        raise FileNotFoundError(data_path)

    dataframe = pd.read_csv(data_path)
    engine = HydrosEngine(modo_execucao="historico")
    result = engine.processar(dataframe)
    trace = result["registro_execucao"]

    with TemporaryDirectory() as temp_dir:
        database_path = Path(temp_dir) / "hydros_test.db"
        database = Database(str(database_path))

        execution_id = database.salvar_registro_execucao(trace)
        stored = database.buscar_execucao(execution_id)

        assert database.quantidade_execucoes() == 1
        assert stored["execution_id"] == trace["execution_id"]
        assert stored["modo_execucao"] == "historico"
        assert stored["unit_id"] == trace["unit_id"]
        assert stored["decisao_original"] == trace["decision"]["action"]
        assert stored["decisao_final"] == trace["decision"]["action"]
        assert stored["status_usuario"] == "nao_avaliada"
        assert stored["registro_execucao"]["agents_executed"][-1] == "AMDH"
        assert len(stored["registro_execucao"]["evidences"]) == 9
        assert stored["algoritmo_aps"] == trace["predictive_result"]["algorithm"]

        accepted = database.registrar_avaliacao_usuario(
            execution_id,
            status="aceitar",
            justificativa="Recomendação agronomicamente coerente.",
        )
        assert accepted["status_usuario"] == "aceita"
        assert accepted["decisao_final"] == accepted["decisao_original"]
        assert (
            accepted["registro_execucao"]["decision"]["user_status"]
            == "aceita"
        )

        modified = database.registrar_avaliacao_usuario(
            execution_id,
            status="modificar",
            acao_modificada="manter_irrigacao",
            justificativa="Alteração realizada pelo responsável técnico.",
        )
        assert modified["status_usuario"] == "modificada"
        assert modified["decisao_final"] == "manter_irrigacao"
        assert modified["acao_modificada_usuario"] == "manter_irrigacao"
        assert (
            modified["registro_execucao"]["decision"]["user_modified_action"]
            == "manter_irrigacao"
        )

        detailed = database.listar_execucoes_detalhadas(limite=10)
        legacy = database.listar_execucoes()
        assert len(detailed) == 1
        assert len(legacy) == 1
        assert len(legacy[0]) == 6

        try:
            database.registrar_avaliacao_usuario(
                execution_id,
                status="modificar",
                acao_modificada="acao_inexistente",
            )
        except ValueError:
            invalid_action_rejected = True
        else:
            invalid_action_rejected = False
        assert invalid_action_rejected

        print("\n=== PERSISTÊNCIA RASTREÁVEL ===")
        print(f"Execução: {execution_id}")
        print(f"Modo: {stored['modo_execucao']}")
        print(f"Decisão original: {stored['decisao_original']}")
        print(f"Status humano final: {modified['status_usuario']}")
        print(f"Decisão após avaliação: {modified['decisao_final']}")
        print(
            "Evidências persistidas:",
            len(stored["registro_execucao"]["evidences"]),
        )
        print("Migração e compatibilidade legada: OK")
        print("PERSISTÊNCIA E AVALIAÇÃO HUMANA: OK")


if __name__ == "__main__":
    main()
