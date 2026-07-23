"""Teste de segurança, domínio e rastreabilidade do APS."""

from pathlib import Path

import pandas as pd

from src.agents.aps_agent import APSAgent
from src.services.hydros_engine import HydrosEngine


ROOT = Path(__file__).resolve().parent


def main() -> None:
    aps = APSAgent(algoritmo="random_forest")

    treino = pd.read_csv(ROOT / "data" / "historico_treinamento_aps.csv")
    conhecido = aps.classificar(treino.tail(5).copy())

    dssat = pd.read_csv(ROOT / "data" / "hydros_soja_dssat_real_v2.csv")
    fora_dominio = aps.classificar(dssat.head(5).copy())

    assert conhecido["categorias_desconhecidas"] == {}
    assert conhecido["status_dominio"] == "dentro_dominio"
    assert conhecido["compatibilidade_dominio"] >= 0.85

    desconhecidas = set(fora_dominio["categorias_desconhecidas"])
    assert {"loc", "solo", "estagio_fenologico"}.issubset(desconhecidas)
    assert fora_dominio["status_dominio"] in {
        "parcialmente_fora_dominio",
        "fora_dominio",
    }
    assert fora_dominio["confianca"] <= fora_dominio["confianca_bruta_modelo"]
    assert fora_dominio["avisos"]
    assert fora_dominio["hash_modelo"]
    assert fora_dominio["versao_modelo"]
    assert fora_dominio["importancia_atributos"]
    assert fora_dominio["tipo_explicabilidade_aps"] == "importancia_global_do_modelo"

    engine = HydrosEngine(algoritmo_aps="random_forest")
    resultado = engine.processar(dssat.head(5).copy(), modo_execucao="historico")
    metadata_aps = resultado["rastreabilidade"]["evidences"]["aps"]["metadata"]

    assert metadata_aps["model_version"] == fora_dominio["versao_modelo"]
    assert metadata_aps["model_hash"] == fora_dominio["hash_modelo"]
    assert metadata_aps["domain_status"] in {
        "parcialmente_fora_dominio",
        "fora_dominio",
    }
    assert metadata_aps["unknown_categories"]

    print("\n=== SEGURANÇA E DOMÍNIO DO APS ===")
    print("Modelo:", conhecido["modelo"])
    print("Versão:", conhecido["versao_modelo"])
    print("Hash:", conhecido["hash_modelo"])
    print("Status científico:", conhecido["status_cientifico_modelo"])
    print("\nCenário conhecido")
    print("  Condição:", conhecido["Eaps"])
    print("  Compatibilidade:", conhecido["compatibilidade_dominio"])
    print("  Status:", conhecido["status_dominio"])
    print("  Confiança bruta:", conhecido["confianca_bruta_modelo"])
    print("  Confiança usada:", conhecido["confianca"])
    print("\nCenário DSSAT")
    print("  Condição:", fora_dominio["Eaps"])
    print("  Compatibilidade:", fora_dominio["compatibilidade_dominio"])
    print("  Status:", fora_dominio["status_dominio"])
    print("  Categorias desconhecidas:", sorted(desconhecidas))
    print("  Confiança bruta:", fora_dominio["confianca_bruta_modelo"])
    print("  Confiança usada:", fora_dominio["confianca"])
    print("  Avisos:", fora_dominio["avisos"])
    print("  Importâncias globais registradas:", len(fora_dominio["importancia_atributos"]))
    print("APS SEGURO E RASTREÁVEL: OK")


if __name__ == "__main__":
    main()
