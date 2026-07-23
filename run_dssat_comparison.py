"""Executa a comparação DSSAT x Hydros Histórico x Hydros Instantâneo.

Saídas geradas em results/dssat_comparison:
- comparacao_detalhada.csv
- metricas_resumo.csv
- matriz_confusao_historico.csv
- matriz_confusao_instantaneo.csv

O DSSAT é tratado como benchmark de simulação, não como verdade absoluta.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    cohen_kappa_score,
    confusion_matrix,
    precision_recall_fscore_support,
)

from src.integrations.dssat_adapter import DSSATAdapter
from src.services.hydros_engine import HydrosEngine


ARQUIVO_DSSAT = Path("data/hydros_soja_dssat_real_v2.csv")
PASTA_SAIDA = Path("results/dssat_comparison")

CLASSES_DECISAO = [
    "finalizar_irrigacao",
    "reduzir_irrigacao",
    "manter_irrigacao",
    "iniciar_irrigacao",
    "aumentar_irrigacao",
]


def calcular_metricas(
    referencia: pd.Series,
    previsao: pd.Series,
    modo: str,
) -> Dict[str, float | str | int]:
    """Calcula métricas de classificação para um modo do Hydros."""

    precisao, recall, f1, _ = precision_recall_fscore_support(
        referencia,
        previsao,
        labels=CLASSES_DECISAO,
        average="macro",
        zero_division=0,
    )

    return {
        "modo": modo,
        "n_observacoes": int(len(referencia)),
        "acuracia": round(float(accuracy_score(referencia, previsao)), 4),
        "precisao_macro": round(float(precisao), 4),
        "recall_macro": round(float(recall), 4),
        "f1_macro": round(float(f1), 4),
        "kappa_cohen": round(float(cohen_kappa_score(referencia, previsao)), 4),
    }


def salvar_matriz_confusao(
    referencia: pd.Series,
    previsao: pd.Series,
    nome_arquivo: str,
) -> None:
    """Salva a matriz de confusão em CSV."""

    matriz = confusion_matrix(
        referencia,
        previsao,
        labels=CLASSES_DECISAO,
    )

    df_matriz = pd.DataFrame(
        matriz,
        index=[f"dssat_{classe}" for classe in CLASSES_DECISAO],
        columns=[f"hydros_{classe}" for classe in CLASSES_DECISAO],
    )
    df_matriz.to_csv(PASTA_SAIDA / nome_arquivo, index=True)


def executar_comparacao() -> pd.DataFrame:
    """Executa ambos os modos do Hydros para cada data simulada."""

    adapter = DSSATAdapter()
    dados_dssat = adapter.carregar_csv(ARQUIVO_DSSAT)
    execucoes = adapter.separar_execucoes(dados_dssat)

    engine_historico = HydrosEngine(modo_execucao="historico")
    engine_instantaneo = HydrosEngine(modo_execucao="instantaneo")

    registros: List[Dict[str, object]] = []
    total = sum(len(grupo) for grupo in execucoes.values())
    processados = 0

    print("\n=== COMPARAÇÃO DSSAT x HYDROS ===")
    print(f"Arquivo: {ARQUIVO_DSSAT}")
    print(f"Execuções DSSAT: {len(execucoes)}")
    print(f"Observações: {total}")

    for cenario_id, grupo in execucoes.items():
        contexto_completo = adapter.contexto_hydros(grupo)

        print(f"\nProcessando {cenario_id}: {len(grupo)} observações")

        for indice in range(len(grupo)):
            historico_ate_data = contexto_completo.iloc[: indice + 1].copy()
            linha_dssat = grupo.iloc[indice]

            try:
                resultado_historico = engine_historico.executar(
                    historico_ate_data,
                    modo_execucao="historico",
                )
                resultado_instantaneo = engine_instantaneo.executar(
                    historico_ate_data,
                    modo_execucao="instantaneo",
                )
            except Exception as erro:
                raise RuntimeError(
                    "Falha ao processar "
                    f"cenario_id={cenario_id}, data={linha_dssat['data']}, "
                    f"indice={indice}. Erro original: {erro}"
                ) from erro

            amdh_h = resultado_historico["amdh"]
            amdh_i = resultado_instantaneo["amdh"]

            registros.append(
                {
                    "cenario_id": cenario_id,
                    "cenario": linha_dssat.get("cenario", ""),
                    "dssat_run": linha_dssat.get("dssat_run", ""),
                    "data": linha_dssat["data"],
                    "dia_safra": linha_dssat.get("dia_safra", indice + 1),
                    "decisao_dssat": linha_dssat["decisao_dssat"],
                    "decisao_hydros_historico": amdh_h["D(Ui)"],
                    "decisao_hydros_instantaneo": amdh_i["D(Ui)"],
                    "concordancia_historico": (
                        linha_dssat["decisao_dssat"] == amdh_h["D(Ui)"]
                    ),
                    "concordancia_instantaneo": (
                        linha_dssat["decisao_dssat"] == amdh_i["D(Ui)"]
                    ),
                    "mesma_decisao_hydros": (
                        amdh_h["D(Ui)"] == amdh_i["D(Ui)"]
                    ),
                    "confianca_historico": amdh_h.get("confianca", 0.0),
                    "confianca_instantaneo": amdh_i.get("confianca", 0.0),
                    "conflito_historico": amdh_h.get("indice_conflito", 0.0),
                    "conflito_instantaneo": amdh_i.get("indice_conflito", 0.0),
                    "revisao_humana_historico": amdh_h.get(
                        "revisao_humana_requerida", False
                    ),
                    "revisao_humana_instantaneo": amdh_i.get(
                        "revisao_humana_requerida", False
                    ),
                    "motivos_revisao_historico": " | ".join(
                        amdh_h.get("motivos_revisao_humana", [])
                    ),
                    "motivos_revisao_instantaneo": " | ".join(
                        amdh_i.get("motivos_revisao_humana", [])
                    ),
                    "avisos_governanca_historico": " | ".join(
                        amdh_h.get("avisos_governanca", [])
                    ),
                    "avisos_governanca_instantaneo": " | ".join(
                        amdh_i.get("avisos_governanca", [])
                    ),
                    "status_aps_historico": resultado_historico["aps"].get(
                        "status_dominio", "nao_informado"
                    ),
                    "status_aps_instantaneo": resultado_instantaneo["aps"].get(
                        "status_dominio", "nao_informado"
                    ),
                    "compatibilidade_aps_historico": resultado_historico["aps"].get(
                        "compatibilidade_dominio", 0.0
                    ),
                    "compatibilidade_aps_instantaneo": resultado_instantaneo["aps"].get(
                        "compatibilidade_dominio", 0.0
                    ),
                    "peso_efetivo_aps_historico": amdh_h.get(
                        "dependencia_aps", {}
                    ).get("peso_efetivo_aps", 0.0),
                    "peso_efetivo_aps_instantaneo": amdh_i.get(
                        "dependencia_aps", {}
                    ).get("peso_efetivo_aps", 0.0),
                    "decisao_sem_aps_historico": amdh_h.get(
                        "dependencia_aps", {}
                    ).get("decisao_sem_aps", ""),
                    "decisao_sem_aps_instantaneo": amdh_i.get(
                        "dependencia_aps", {}
                    ).get("decisao_sem_aps", ""),
                    "dependencia_material_aps_historico": bool(
                        amdh_h.get("dependencia_aps", {}).get(
                            "influencia_material", False
                        )
                    ),
                    "dependencia_material_aps_instantaneo": bool(
                        amdh_i.get("dependencia_aps", {}).get(
                            "influencia_material", False
                        )
                    ),
                    "score_historico": amdh_h.get("score_hibrido", 0.0),
                    "score_instantaneo": amdh_i.get("score_hibrido", 0.0),
                    "umidade_solo_pct": linha_dssat["umidade_solo"],
                    "agua_disponivel_mm": linha_dssat["agua_disponivel"],
                    "irrigacao_dssat_mm": linha_dssat["irrigacao_aplicada"],
                    "estresse_dssat_original": linha_dssat.get(
                        "estresse_hidrico_dssat_original",
                        linha_dssat.get("estresse_hidrico", ""),
                    ),
                    "estresse_hydros": linha_dssat["estresse_hidrico"],
                    "produtividade_kg_ha": linha_dssat["produtividade"],
                    "ehc_historico": resultado_historico["aiec"]["Ehc"],
                    "earg_historico": resultado_historico["arg"]["Earg"],
                    "eaps_historico": resultado_historico["aps"]["Eaps"],
                    "ehc_instantaneo": resultado_instantaneo["aiec"]["Ehc"],
                    "earg_instantaneo": resultado_instantaneo["arg"]["Earg"],
                    "eaps_instantaneo": resultado_instantaneo["aps"]["Eaps"],
                }
            )

            processados += 1
            if processados % 25 == 0 or processados == total:
                print(f"  Progresso: {processados}/{total}")

    return pd.DataFrame(registros)


def main() -> None:
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    resultados = executar_comparacao()
    caminho_detalhado = PASTA_SAIDA / "comparacao_detalhada.csv"
    resultados.to_csv(caminho_detalhado, index=False)

    referencia = resultados["decisao_dssat"]

    metricas = pd.DataFrame(
        [
            calcular_metricas(
                referencia,
                resultados["decisao_hydros_historico"],
                "historico",
            ),
            calcular_metricas(
                referencia,
                resultados["decisao_hydros_instantaneo"],
                "instantaneo",
            ),
        ]
    )

    metricas["confianca_media"] = [
        round(float(resultados["confianca_historico"].mean()), 4),
        round(float(resultados["confianca_instantaneo"].mean()), 4),
    ]
    metricas["conflito_medio"] = [
        round(float(resultados["conflito_historico"].mean()), 4),
        round(float(resultados["conflito_instantaneo"].mean()), 4),
    ]
    metricas["taxa_revisao_humana"] = [
        round(float(resultados["revisao_humana_historico"].mean()), 4),
        round(float(resultados["revisao_humana_instantaneo"].mean()), 4),
    ]
    metricas["compatibilidade_aps_media"] = [
        round(float(resultados["compatibilidade_aps_historico"].mean()), 4),
        round(float(resultados["compatibilidade_aps_instantaneo"].mean()), 4),
    ]
    metricas["peso_efetivo_aps_medio"] = [
        round(float(resultados["peso_efetivo_aps_historico"].mean()), 4),
        round(float(resultados["peso_efetivo_aps_instantaneo"].mean()), 4),
    ]
    metricas["taxa_dependencia_material_aps"] = [
        round(float(resultados["dependencia_material_aps_historico"].mean()), 4),
        round(float(resultados["dependencia_material_aps_instantaneo"].mean()), 4),
    ]

    metricas.to_csv(PASTA_SAIDA / "metricas_resumo.csv", index=False)

    salvar_matriz_confusao(
        referencia,
        resultados["decisao_hydros_historico"],
        "matriz_confusao_historico.csv",
    )
    salvar_matriz_confusao(
        referencia,
        resultados["decisao_hydros_instantaneo"],
        "matriz_confusao_instantaneo.csv",
    )

    print("\n=== RESULTADOS ===")
    print(metricas.to_string(index=False))

    diferencas = int((~resultados["mesma_decisao_hydros"]).sum())
    print(f"\nDatas em que os modos Hydros divergiram: {diferencas}")
    print(f"Resultados salvos em: {PASTA_SAIDA.resolve()}")
    print("\nCOMPARAÇÃO DSSAT x HYDROS: OK")


if __name__ == "__main__":
    main()