"""Teste da integração mínima e rastreável da HydrosOnto."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.services.hydros_engine import HydrosEngine
from src.ontology.hydros_onto import HydrosOnto


def validate_result(result: dict, mode: str) -> None:
    inference = result["hydros_onto"]
    trace = result["registro_execucao"]
    arg = result["arg"]

    assert inference["ontology"] == "HydrosOnto"
    assert inference["mode"] == mode
    assert inference["semantic_condition"] in {
        "adequada",
        "atencao",
        "critica",
    }
    assert inference["ontology_class"] in {
        "CondicaoAdequada",
        "CondicaoAtencao",
        "CondicaoCritica",
    }
    assert 0.0 <= inference["confidence"] <= 1.0
    assert inference["rules_triggered"]
    assert trace["semantic_inferences"]
    assert trace["metadata"]["ontology_integrated"] is True
    assert arg["inferencia_semantica"]["inference_id"] == inference["inference_id"]
    assert arg["consistencia_semantica"] in {
        "concordante",
        "divergente",
    }
    json.dumps(trace, ensure_ascii=False)


def main() -> None:
    ontology_file = Path("ontology/hydros_onto.ttl")
    assert ontology_file.exists()

    ontology = HydrosOnto()
    assert ontology.validation["minimum_vocabulary_valid"] is True

    dataframe = pd.read_csv("data/historico_contexto_exemplo.csv")
    engine = HydrosEngine()

    historical = engine.processar(dataframe, modo_execucao="historico")
    instantaneous = engine.processar(dataframe, modo_execucao="instantaneo")

    validate_result(historical, "historico")
    validate_result(instantaneous, "instantaneo")

    print("\n=== HYDROSONTO ===")
    print("Arquivo:", ontology.validation["path"])
    print("Backend:", ontology.validation["backend"])
    print(
        "Sintaxe Turtle validada por parser:",
        ontology.validation["turtle_syntax_validated"],
    )
    print(
        "Condição histórica:",
        historical["hydros_onto"]["semantic_condition"],
    )
    print(
        "Classe histórica:",
        historical["hydros_onto"]["ontology_class"],
    )
    print(
        "Regras históricas:",
        historical["hydros_onto"]["rules_triggered"],
    )
    print(
        "Consistência ARG x HydrosOnto:",
        historical["arg"]["consistencia_semantica"],
    )
    print(
        "Condição instantânea:",
        instantaneous["hydros_onto"]["semantic_condition"],
    )
    print("Inferências rastreadas:", len(historical["registro_execucao"]["semantic_inferences"]))
    print("HYDROSONTO: OK")


if __name__ == "__main__":
    main()
