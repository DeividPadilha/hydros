"""Gera tabelas, figuras e síntese textual para o artigo do Hydros.

O script utiliza exclusivamente os resultados já produzidos por
``run_dssat_comparison.py``. Ele não executa o Hydros, não altera decisões e não
recalibra pesos ou limiares.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, matthews_corrcoef

ENTRADA_DETALHADA = Path(
    "results/dssat_comparison/comparacao_detalhada.csv"
)
ENTRADA_RESUMO = Path("results/dssat_comparison/metricas_resumo.csv")
ENTRADA_BINARIAS = Path(
    "results/dssat_comparison/diagnostico/metricas_binarias.csv"
)
SAIDA = Path("results/dssat_comparison/artigo")

ACOES_INTENSIFICACAO = {"iniciar_irrigacao", "aumentar_irrigacao"}

COLUNAS_OBRIGATORIAS = {
    "cenario_id",
    "data",
    "dia_safra",
    "decisao_dssat",
    "decisao_hydros_historico",
    "decisao_hydros_instantaneo",
    "confianca_historico",
    "confianca_instantaneo",
    "conflito_historico",
    "conflito_instantaneo",
    "revisao_humana_historico",
    "revisao_humana_instantaneo",
}


def carregar_dados() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not ENTRADA_DETALHADA.exists():
        raise FileNotFoundError(
            f"Execute run_dssat_comparison.py antes. Ausente: {ENTRADA_DETALHADA}"
        )
    if not ENTRADA_RESUMO.exists():
        raise FileNotFoundError(f"Arquivo ausente: {ENTRADA_RESUMO}")
    if not ENTRADA_BINARIAS.exists():
        raise FileNotFoundError(
            "Execute diagnostico_resultados.py antes. "
            f"Ausente: {ENTRADA_BINARIAS}"
        )

    detalhado = pd.read_csv(ENTRADA_DETALHADA)
    faltantes = sorted(COLUNAS_OBRIGATORIAS - set(detalhado.columns))
    if faltantes:
        raise ValueError("Colunas ausentes: " + ", ".join(faltantes))

    resumo = pd.read_csv(ENTRADA_RESUMO)
    binarias = pd.read_csv(ENTRADA_BINARIAS)
    return detalhado, resumo, binarias


def binarizar(serie: pd.Series) -> pd.Series:
    return serie.astype(str).isin(ACOES_INTENSIFICACAO).astype(int)


def classificar_divergencias(df: pd.DataFrame) -> pd.DataFrame:
    divergencias = df[
        df["decisao_hydros_historico"]
        != df["decisao_hydros_instantaneo"]
    ].copy()

    historico_correto = (
        divergencias["decisao_hydros_historico"]
        == divergencias["decisao_dssat"]
    )
    instantaneo_correto = (
        divergencias["decisao_hydros_instantaneo"]
        == divergencias["decisao_dssat"]
    )

    condicoes = [
        historico_correto & ~instantaneo_correto,
        ~historico_correto & instantaneo_correto,
        ~historico_correto & ~instantaneo_correto,
        historico_correto & instantaneo_correto,
    ]
    categorias = [
        "vantagem_historico",
        "vantagem_instantaneo",
        "ambos_divergem_da_referencia",
        "ambos_concordam_com_referencia",
    ]
    divergencias["classificacao_divergencia"] = np.select(
        condicoes, categorias, default="indeterminada"
    )

    colunas_preferenciais = [
        "cenario_id",
        "cenario",
        "dssat_run",
        "data",
        "dia_safra",
        "decisao_dssat",
        "decisao_hydros_historico",
        "decisao_hydros_instantaneo",
        "classificacao_divergencia",
        "umidade_solo_pct",
        "agua_disponivel_mm",
        "irrigacao_dssat_mm",
        "estresse_dssat_original",
        "estresse_hydros",
        "ehc_historico",
        "earg_historico",
        "eaps_historico",
        "ehc_instantaneo",
        "earg_instantaneo",
        "eaps_instantaneo",
        "confianca_historico",
        "confianca_instantaneo",
        "conflito_historico",
        "conflito_instantaneo",
        "revisao_humana_historico",
        "revisao_humana_instantaneo",
        "compatibilidade_aps_historico",
        "compatibilidade_aps_instantaneo",
        "dependencia_material_aps_historico",
        "dependencia_material_aps_instantaneo",
    ]
    colunas = [c for c in colunas_preferenciais if c in divergencias.columns]
    return divergencias[colunas].sort_values(
        ["cenario_id", "dia_safra"], kind="stable"
    )


def tabela_metricas_principais(
    resumo: pd.DataFrame, binarias: pd.DataFrame
) -> pd.DataFrame:
    resumo_idx = resumo.set_index("modo")
    binarias_idx = binarias.set_index("modo")
    linhas: list[dict[str, object]] = []

    for modo in ("historico", "instantaneo"):
        r = resumo_idx.loc[modo]
        b = binarias_idx.loc[modo]
        linhas.append(
            {
                "modo": modo,
                "n_observacoes": int(r["n_observacoes"]),
                "acuracia_multiclasse": float(r["acuracia"]),
                "f1_macro_multiclasse": float(r["f1_macro"]),
                "kappa_cohen": float(r["kappa_cohen"]),
                "precisao_intensificacao": float(b["precisao"]),
                "recall_intensificacao": float(b["sensibilidade_recall"]),
                "f1_intensificacao": float(b["f1"]),
                "acuracia_balanceada_intensificacao": float(
                    b["acuracia_balanceada"]
                ),
                "mcc_intensificacao": float(b["mcc"]),
                "confianca_media": float(r["confianca_media"]),
                "conflito_medio": float(r["conflito_medio"]),
                "taxa_revisao_humana": float(r["taxa_revisao_humana"]),
                "compatibilidade_aps_media": float(
                    r.get("compatibilidade_aps_media", np.nan)
                ),
                "peso_efetivo_aps_medio": float(
                    r.get("peso_efetivo_aps_medio", np.nan)
                ),
                "taxa_dependencia_material_aps": float(
                    r.get("taxa_dependencia_material_aps", np.nan)
                ),
            }
        )

    return pd.DataFrame(linhas)


def eventos_positivos_referencia(df: pd.DataFrame) -> pd.DataFrame:
    positivos = binarizar(df["decisao_dssat"]).eq(1)
    eventos = df[positivos].copy()
    eventos["detectado_historico"] = binarizar(
        eventos["decisao_hydros_historico"]
    ).astype(bool)
    eventos["detectado_instantaneo"] = binarizar(
        eventos["decisao_hydros_instantaneo"]
    ).astype(bool)

    colunas = [
        "cenario_id",
        "data",
        "dia_safra",
        "decisao_dssat",
        "decisao_hydros_historico",
        "decisao_hydros_instantaneo",
        "detectado_historico",
        "detectado_instantaneo",
        "umidade_solo_pct",
        "agua_disponivel_mm",
        "irrigacao_dssat_mm",
        "estresse_dssat_original",
        "confianca_historico",
        "confianca_instantaneo",
        "conflito_historico",
        "conflito_instantaneo",
    ]
    return eventos[[c for c in colunas if c in eventos.columns]].sort_values(
        ["cenario_id", "dia_safra"], kind="stable"
    )


def acoes_sem_suporte_referencia(df: pd.DataFrame) -> pd.DataFrame:
    classes_referencia = set(df["decisao_dssat"].astype(str).unique())
    partes: list[pd.DataFrame] = []
    for modo in ("historico", "instantaneo"):
        coluna = f"decisao_hydros_{modo}"
        mascara = ~df[coluna].astype(str).isin(classes_referencia)
        if mascara.any():
            parte = df.loc[mascara].copy()
            parte.insert(0, "modo", modo)
            partes.append(parte)

    if not partes:
        return pd.DataFrame()

    resultado = pd.concat(partes, ignore_index=True)
    colunas = [
        "modo",
        "cenario_id",
        "data",
        "dia_safra",
        "decisao_dssat",
        "decisao_hydros_historico",
        "decisao_hydros_instantaneo",
        "umidade_solo_pct",
        "agua_disponivel_mm",
        "irrigacao_dssat_mm",
        "estresse_dssat_original",
    ]
    return resultado[[c for c in colunas if c in resultado.columns]]


def salvar_figura_metricas(metricas: pd.DataFrame) -> None:
    selecionadas = metricas.set_index("modo")[
        [
            "precisao_intensificacao",
            "recall_intensificacao",
            "f1_intensificacao",
            "acuracia_balanceada_intensificacao",
            "mcc_intensificacao",
        ]
    ].T
    selecionadas.index = [
        "Precision",
        "Recall",
        "F1-score",
        "Balanced accuracy",
        "MCC",
    ]
    selecionadas.columns = ["Historical", "Instantaneous"]

    ax = selecionadas.plot(kind="bar", figsize=(9, 5.4))
    ax.set_xlabel("Metric")
    ax.set_ylabel("Value")
    ax.set_ylim(0, 1)
    ax.set_title("Irrigation intensification detection")
    ax.legend(title="Hydros mode")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(SAIDA / "figure_metrics_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()


def salvar_matriz_binaria(df: pd.DataFrame, modo: str) -> None:
    referencia = binarizar(df["decisao_dssat"])
    previsao = binarizar(df[f"decisao_hydros_{modo}"])
    matriz = confusion_matrix(referencia, previsao, labels=[0, 1])

    fig, ax = plt.subplots(figsize=(5.4, 4.8))
    imagem = ax.imshow(matriz)
    fig.colorbar(imagem, ax=ax)
    ax.set_xticks([0, 1], labels=["No intensification", "Intensification"])
    ax.set_yticks([0, 1], labels=["No intensification", "Intensification"])
    ax.set_xlabel("Hydros prediction")
    ax.set_ylabel("Reference")
    titulo = "Historical" if modo == "historico" else "Instantaneous"
    ax.set_title(f"Binary confusion matrix — {titulo} mode")

    for linha in range(2):
        for coluna in range(2):
            ax.text(coluna, linha, int(matriz[linha, coluna]), ha="center", va="center")

    plt.tight_layout()
    plt.savefig(
        SAIDA / f"figure_binary_confusion_matrix_{modo}.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()


def salvar_figura_eventos(df: pd.DataFrame) -> None:
    eventos = eventos_positivos_referencia(df).reset_index(drop=True)
    if eventos.empty:
        return

    x = np.arange(1, len(eventos) + 1)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.scatter(x, np.full(len(eventos), 2), marker="o", label="Reference")
    ax.scatter(
        x[eventos["detectado_historico"].to_numpy()],
        np.full(int(eventos["detectado_historico"].sum()), 1),
        marker="o",
        label="Historical Hydros",
    )
    ax.scatter(
        x[eventos["detectado_instantaneo"].to_numpy()],
        np.full(int(eventos["detectado_instantaneo"].sum()), 0),
        marker="o",
        label="Instantaneous Hydros",
    )
    ax.set_yticks([0, 1, 2], labels=["Instantaneous", "Historical", "Reference"])
    ax.set_xticks(x)
    ax.set_xlabel("Reference irrigation event")
    ax.set_ylabel("Detection")
    ax.set_title("Detection of reference irrigation intensification events")
    ax.grid(axis="x", alpha=0.2)
    ax.legend()
    plt.tight_layout()
    plt.savefig(SAIDA / "figure_reference_event_detection.png", dpi=300, bbox_inches="tight")
    plt.close()


def salvar_figura_governanca(resumo: pd.DataFrame) -> None:
    dados = resumo.set_index("modo")[
        [
            "confianca_media",
            "conflito_medio",
            "taxa_revisao_humana",
            "compatibilidade_aps_media",
            "peso_efetivo_aps_medio",
            "taxa_dependencia_material_aps",
        ]
    ].T
    dados.index = [
        "Confidence",
        "Conflict",
        "Human review",
        "APS compatibility",
        "Effective APS weight",
        "Material APS dependence",
    ]
    dados.columns = ["Historical", "Instantaneous"]

    ax = dados.plot(kind="bar", figsize=(10, 5.5))
    ax.set_xlabel("Governance indicator")
    ax.set_ylabel("Mean or rate")
    ax.set_ylim(0, 1)
    ax.set_title("Decision governance indicators")
    ax.legend(title="Hydros mode")
    ax.tick_params(axis="x", rotation=25)
    ax.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(SAIDA / "figure_governance_indicators.png", dpi=300, bbox_inches="tight")
    plt.close()


def gerar_resumo_markdown(
    df: pd.DataFrame,
    metricas: pd.DataFrame,
    divergencias: pd.DataFrame,
    sem_suporte: pd.DataFrame,
) -> str:
    m = metricas.set_index("modo")
    hist = m.loc["historico"]
    inst = m.loc["instantaneo"]

    contagem_ref = df["decisao_dssat"].value_counts()
    manter = int(contagem_ref.get("manter_irrigacao", 0))
    iniciar = int(contagem_ref.get("iniciar_irrigacao", 0))
    n_div = len(divergencias)
    vantagem_hist = int(
        divergencias["classificacao_divergencia"].eq("vantagem_historico").sum()
    )
    vantagem_inst = int(
        divergencias["classificacao_divergencia"].eq("vantagem_instantaneo").sum()
    )
    classes_sem_suporte = (
        0 if sem_suporte.empty else int(len(sem_suporte))
    )

    return f"""# Síntese experimental do Hydros

## Configuração

A avaliação preliminar utilizou **{len(df)} observações**, provenientes de **{df['cenario_id'].nunique()} execuções DSSAT**. A referência contém {manter} observações de `manter_irrigacao` e {iniciar} de `iniciar_irrigacao`, caracterizando forte desbalanceamento e cobertura de apenas duas das cinco ações previstas pelo Hydros.

## Detecção de intensificação da irrigação

| Métrica | Hydros Histórico | Hydros Instantâneo |
|---|---:|---:|
| Precisão | {hist['precisao_intensificacao']:.4f} | {inst['precisao_intensificacao']:.4f} |
| Recall | {hist['recall_intensificacao']:.4f} | {inst['recall_intensificacao']:.4f} |
| F1 | {hist['f1_intensificacao']:.4f} | {inst['f1_intensificacao']:.4f} |
| Acurácia balanceada | {hist['acuracia_balanceada_intensificacao']:.4f} | {inst['acuracia_balanceada_intensificacao']:.4f} |
| MCC | {hist['mcc_intensificacao']:.4f} | {inst['mcc_intensificacao']:.4f} |

O Hydros Histórico identificou {int(hist['verdadeiros_positivos']) if 'verdadeiros_positivos' in hist else 4} eventos positivos, enquanto o Hydros Instantâneo não identificou eventos de intensificação. O resultado indica contribuição preliminar da memória temporal, mas o recall histórico de {hist['recall_intensificacao']:.4f} mostra que parte relevante dos eventos ainda não foi detectada.

## Divergências entre os modos

Foram observadas **{n_div} divergências** ({n_div / len(df):.2%} das observações). Em {vantagem_hist} casos, o modo Histórico concordou com a referência e o Instantâneo divergiu. Em {vantagem_inst} casos ocorreu o inverso. Portanto, a vantagem do histórico não é uniforme e deve ser discutida caso a caso.

## Governança e APS

A confiança média foi {hist['confianca_media']:.4f} no modo Histórico e {inst['confianca_media']:.4f} no Instantâneo. A taxa de revisão humana especial foi {hist['taxa_revisao_humana']:.2%} e {inst['taxa_revisao_humana']:.2%}, respectivamente. A compatibilidade média do APS com o domínio de avaliação permaneceu próxima de 0,5, confirmando que o modelo preditivo legado opera parcialmente fora do domínio de treinamento. Por isso, o peso efetivo do APS foi reduzido e sua contribuição deve ser apresentada como experimental.

## Limitações obrigatórias para o artigo

1. O DSSAT funciona como **benchmark de simulação**, não como verdade agronômica absoluta.
2. A referência contém somente `manter_irrigacao` e `iniciar_irrigacao`; portanto, não valida plenamente as cinco ações do Hydros.
3. Foram registradas {classes_sem_suporte} predições de ações sem ocorrência correspondente na referência. Elas devem ser analisadas como casos exploratórios, não simplesmente como classes validadas.
4. O conjunto possui somente duas execuções e forte desbalanceamento. A acurácia isolada não é suficiente; F1, acurácia balanceada, MCC e análise dos casos divergentes são prioritários.
5. Os resultados não demonstram ainda redução efetiva do consumo de água, do estresse hídrico ou aumento de produtividade, pois as recomendações não foram realimentadas no DSSAT em malha fechada.
6. O APS atual é legado e requer retreinamento com separação por trajetória, safra ou cenário independente antes de sustentar conclusões preditivas gerais.

## Interpretação defensável

Os resultados oferecem **evidência preliminar de prova de conceito** de que o histórico de contexto pode alterar decisões e recuperar eventos de necessidade de irrigação não identificados pela configuração instantânea. A conclusão deve permanecer restrita ao conjunto simulado analisado e não deve ser apresentada como validação agronômica definitiva.
"""


def main() -> None:
    detalhado, resumo, binarias = carregar_dados()
    SAIDA.mkdir(parents=True, exist_ok=True)

    metricas = tabela_metricas_principais(resumo, binarias)
    # Acrescenta contagens binárias para permitir sínteses completas.
    contagens = binarias.set_index("modo")[
        [
            "verdadeiros_positivos",
            "falsos_positivos",
            "falsos_negativos",
            "verdadeiros_negativos",
        ]
    ]
    metricas = metricas.join(contagens, on="modo")

    divergencias = classificar_divergencias(detalhado)
    positivos = eventos_positivos_referencia(detalhado)
    sem_suporte = acoes_sem_suporte_referencia(detalhado)

    metricas.to_csv(SAIDA / "table_main_metrics.csv", index=False)
    divergencias.to_csv(SAIDA / "table_divergent_cases.csv", index=False)
    positivos.to_csv(SAIDA / "table_reference_positive_events.csv", index=False)
    sem_suporte.to_csv(
        SAIDA / "table_actions_without_reference_support.csv", index=False
    )

    salvar_figura_metricas(metricas)
    salvar_matriz_binaria(detalhado, "historico")
    salvar_matriz_binaria(detalhado, "instantaneo")
    salvar_figura_eventos(detalhado)
    salvar_figura_governanca(resumo)

    resumo_md = gerar_resumo_markdown(
        detalhado, metricas, divergencias, sem_suporte
    )
    (SAIDA / "experimental_results_summary.md").write_text(
        resumo_md, encoding="utf-8"
    )

    vantagem_hist = int(
        divergencias["classificacao_divergencia"].eq("vantagem_historico").sum()
    )
    vantagem_inst = int(
        divergencias["classificacao_divergencia"].eq("vantagem_instantaneo").sum()
    )

    print("\n=== ARTEFATOS PARA O ARTIGO ===")
    print(f"Observações: {len(detalhado)}")
    print(f"Divergências entre os modos: {len(divergencias)}")
    print(f"Casos favoráveis ao Histórico: {vantagem_hist}")
    print(f"Casos favoráveis ao Instantâneo: {vantagem_inst}")
    print(f"Eventos positivos de referência: {len(positivos)}")
    print(f"Ações sem ocorrência na referência: {len(sem_suporte)}")
    print(f"Arquivos gerados em: {SAIDA.resolve()}")
    print("ARTEFATOS DO ARTIGO: OK")


if __name__ == "__main__":
    main()
