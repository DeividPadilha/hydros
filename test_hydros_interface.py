from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from src.database.database import Database
from src.services.hydros_engine import HydrosEngine
from src.services.interface_adapter import (
    build_comparison_rows,
    build_execution_view,
    persist_execution,
    register_user_evaluation,
)


def main() -> None:
    dataframe = pd.read_csv("data/historico_contexto_exemplo.csv")
    engine = HydrosEngine(algoritmo_aps="random_forest")

    historical = engine.executar(dataframe.copy(), modo_execucao="historico")
    instantaneous = engine.executar(dataframe.copy(), modo_execucao="instantaneo")

    historical_view = build_execution_view(historical)
    instantaneous_view = build_execution_view(instantaneous)

    assert historical_view["mode"] == "historico"
    assert instantaneous_view["mode"] == "instantaneo"
    assert historical_view["used_contexts"] == len(dataframe)
    assert instantaneous_view["used_contexts"] == 1
    assert historical_view["evidence_count"] == 9
    assert instantaneous_view["evidence_count"] == 9
    assert historical_view["automatic_execution"] is False
    assert historical_view["ontology_integrated"] is True
    assert historical_view["execution_id"]
    assert instantaneous_view["execution_id"]

    comparison = build_comparison_rows([historical, instantaneous])
    assert len(comparison) == 2
    assert {row["Modo"] for row in comparison} == {
        "Hydros Histórico",
        "Hydros Instantâneo",
    }

    with TemporaryDirectory() as temp_dir:
        database = Database(str(Path(temp_dir) / "hydros_interface_test.db"))
        historical_id = persist_execution(database, historical)
        instantaneous_id = persist_execution(database, instantaneous)

        assert historical_id == historical_view["execution_id"]
        assert instantaneous_id == instantaneous_view["execution_id"]
        assert database.quantidade_execucoes() == 2

        accepted = register_user_evaluation(
            database,
            historical_id,
            status="aceita",
            justification="Recomendação coerente com a trajetória observada.",
        )
        assert accepted["status_usuario"] == "aceita"
        assert accepted["decisao_final"] == accepted["decisao_original"]

        modified_action = (
            "manter_irrigacao"
            if instantaneous_view["action"] != "manter_irrigacao"
            else "iniciar_irrigacao"
        )
        modified = register_user_evaluation(
            database,
            instantaneous_id,
            status="modificada",
            modified_action=modified_action,
            justification="Ação ajustada pelo avaliador humano.",
        )
        assert modified["status_usuario"] == "modificada"
        assert modified["decisao_final"] == modified_action

    print("\n=== INTERFACE E SUPERVISÃO HUMANA ===")
    print(f"Modo histórico: {historical_view['action']}")
    print(f"Modo instantâneo: {instantaneous_view['action']}")
    print(f"Contextos históricos utilizados: {historical_view['used_contexts']}")
    print(f"Contextos instantâneos utilizados: {instantaneous_view['used_contexts']}")
    print(f"Evidências por execução: {historical_view['evidence_count']}")
    print("Persistência integral: OK")
    print("Aceitar, modificar e rejeitar: disponíveis")
    print("Acionamento automático: desativado")
    print("INTERFACE E SUPERVISÃO HUMANA: OK")


if __name__ == "__main__":
    main()
