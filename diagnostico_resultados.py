"""Diagnóstico científico da comparação DSSAT x Hydros.

Lê ``results/dssat_comparison/comparacao_detalhada.csv`` e produz:
- distribuição das classes;
- acurácia balanceada e MCC;
- avaliação binária de intensificação da irrigação;
- diferenças entre os modos Histórico e Instantâneo;
- identificação de ações previstas pelo Hydros sem ocorrência na referência;
- arquivos CSV de diagnóstico.

O script não altera o Hydros, não recalibra parâmetros e não modifica as decisões.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    matthews_corrcoef,
    precision_recall_fscore_support,
)

ARQUIVO = Path("results/dssat_comparison/comparacao_detalhada.csv")
SAIDA = Path("results/dssat_comparison/diagnostico")

COLUNAS_DECISAO = {
    "dssat": "decisao_dssat",
    "historico": "decisao_hydros_historico",
    "instantaneo": "decisao_hydros_instantaneo",
}

ACOES_INTENSIFICACAO = {
    "iniciar_irrigacao",
    "aumentar_irrigacao",
}


def validar_colunas(df: pd.DataFrame) -> None:
    faltantes = [c for c in COLUNAS_DECISAO.values() if c not in df.columns]
    if faltantes:
        raise ValueError("Colunas ausentes: " + ", ".join(faltantes))


def distribuicao_classes(df: pd.DataFrame) -> pd.DataFrame:
    linhas: list[dict[str, object]] = []
    total = len(df)

    for sistema, coluna in COLUNAS_DECISAO.items():
        contagens = df[coluna].value_counts(dropna=False)
        for classe, quantidade in contagens.items():
            linhas.append(
                {
                    "sistema": sistema,
                    "classe": str(classe),
                    "quantidade": int(quantidade),
                    "percentual": round(100.0 * quantidade / total, 2),
                }
            )

    return pd.DataFrame(linhas)


def binarizar(serie: pd.Series) -> pd.Series:
    return serie.astype(str).isin(ACOES_INTENSIFICACAO).astype(int)


def acuracia_balanceada_referencia(
    referencia: Iterable[object], previsao: Iterable[object]
) -> float:
    """Calcula a média do recall das classes presentes na referência.

    A implementação explícita evita o aviso do scikit-learn quando a previsão contém
    uma ação que não ocorre em ``y_true``. Essas ações continuam sendo contabilizadas
    como erros nas linhas das classes de referência.
    """

    y_true = pd.Series(referencia, dtype="object")
    y_pred = pd.Series(previsao, dtype="object")
    classes_referencia = list(pd.unique(y_true.dropna()))
    if not classes_referencia:
        return 0.0

    recalls: list[float] = []
    for classe in classes_referencia:
        mascara = y_true.eq(classe)
        total_classe = int(mascara.sum())
        if total_classe:
            recalls.append(float(y_pred[mascara].eq(classe).mean()))

    return float(np.mean(recalls)) if recalls else 0.0


def metricas_multiclasse(df: pd.DataFrame) -> pd.DataFrame:
    referencia = df[COLUNAS_DECISAO["dssat"]].astype(str)
    linhas: list[dict[str, object]] = []

    for modo in ("historico", "instantaneo"):
        previsao = df[COLUNAS_DECISAO[modo]].astype(str)
        linhas.append(
            {
                "modo": modo,
                "acuracia": round(accuracy_score(referencia, previsao), 4),
                "acuracia_balanceada": round(
                    acuracia_balanceada_referencia(referencia, previsao), 4
                ),
                "mcc": round(matthews_corrcoef(referencia, previsao), 4),
            }
        )

    return pd.DataFrame(linhas)


def metricas_binarias(df: pd.DataFrame) -> pd.DataFrame:
    referencia = binarizar(df[COLUNAS_DECISAO["dssat"]])
    linhas: list[dict[str, object]] = []

    for modo in ("historico", "instantaneo"):
        previsao = binarizar(df[COLUNAS_DECISAO[modo]])
        precisao, recall, f1, _ = precision_recall_fscore_support(
            referencia,
            previsao,
            average="binary",
            zero_division=0,
        )
        matriz = confusion_matrix(referencia, previsao, labels=[0, 1])
        tn, fp, fn, tp = matriz.ravel()

        linhas.append(
            {
                "modo": modo,
                "n": int(len(df)),
                "positivos_dssat": int(referencia.sum()),
                "positivos_hydros": int(previsao.sum()),
                "verdadeiros_positivos": int(tp),
                "falsos_positivos": int(fp),
                "falsos_negativos": int(fn),
                "verdadeiros_negativos": int(tn),
                "precisao": round(float(precisao), 4),
                "sensibilidade_recall": round(float(recall), 4),
                "f1": round(float(f1), 4),
                "acuracia_balanceada": round(
                    acuracia_balanceada_referencia(referencia, previsao), 4
                ),
                "mcc": round(matthews_corrcoef(referencia, previsao), 4),
            }
        )

    return pd.DataFrame(linhas)


def comparar_modos(df: pd.DataFrame) -> pd.DataFrame:
    divergiram = (
        df[COLUNAS_DECISAO["historico"]]
        != df[COLUNAS_DECISAO["instantaneo"]]
    )

    resultado: dict[str, object] = {
        "n_observacoes": len(df),
        "n_divergencias": int(divergiram.sum()),
        "taxa_divergencia": round(float(divergiram.mean()), 4),
    }

    for coluna in (
        "confianca_historico",
        "confianca_instantaneo",
        "conflito_historico",
        "conflito_instantaneo",
        "revisao_humana_historico",
        "revisao_humana_instantaneo",
        "compatibilidade_aps_historico",
        "compatibilidade_aps_instantaneo",
        "peso_efetivo_aps_historico",
        "peso_efetivo_aps_instantaneo",
        "dependencia_material_aps_historico",
        "dependencia_material_aps_instantaneo",
    ):
        if coluna in df.columns:
            resultado[f"media_{coluna}"] = round(
                float(pd.to_numeric(df[coluna], errors="coerce").mean()), 4
            )

    return pd.DataFrame([resultado])


def acoes_sem_classe_na_referencia(df: pd.DataFrame) -> pd.DataFrame:
    classes_referencia = set(df[COLUNAS_DECISAO["dssat"]].dropna().astype(str))
    linhas: list[dict[str, object]] = []

    for modo in ("historico", "instantaneo"):
        coluna = COLUNAS_DECISAO[modo]
        previsoes = df[coluna].astype(str)
        fora = ~previsoes.isin(classes_referencia)
        for classe, quantidade in previsoes[fora].value_counts().items():
            linhas.append(
                {
                    "modo": modo,
                    "classe_sem_ocorrencia_na_referencia": classe,
                    "quantidade": int(quantidade),
                    "percentual": round(100.0 * quantidade / len(df), 4),
                }
            )

    return pd.DataFrame(
        linhas,
        columns=[
            "modo",
            "classe_sem_ocorrencia_na_referencia",
            "quantidade",
            "percentual",
        ],
    )


def main() -> None:
    if not ARQUIVO.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {ARQUIVO}")

    df = pd.read_csv(ARQUIVO)
    validar_colunas(df)
    SAIDA.mkdir(parents=True, exist_ok=True)

    distribuicao = distribuicao_classes(df)
    multiclasses = metricas_multiclasse(df)
    binarias = metricas_binarias(df)
    modos = comparar_modos(df)
    classes_ausentes = acoes_sem_classe_na_referencia(df)

    distribuicao.to_csv(SAIDA / "distribuicao_classes.csv", index=False)
    multiclasses.to_csv(SAIDA / "metricas_multiclasse.csv", index=False)
    binarias.to_csv(SAIDA / "metricas_binarias.csv", index=False)
    modos.to_csv(SAIDA / "comparacao_modos.csv", index=False)
    classes_ausentes.to_csv(
        SAIDA / "acoes_sem_classe_na_referencia.csv", index=False
    )

    print("\n=== DISTRIBUIÇÃO DAS CLASSES ===")
    print(distribuicao.to_string(index=False))

    print("\n=== MÉTRICAS MULTICLASSE ===")
    print(multiclasses.to_string(index=False))

    print("\n=== DETECÇÃO DE INTENSIFICAÇÃO DA IRRIGAÇÃO ===")
    print(binarias.to_string(index=False))

    print("\n=== HISTÓRICO x INSTANTÂNEO ===")
    print(modos.to_string(index=False))

    print("\n=== AÇÕES SEM OCORRÊNCIA NA REFERÊNCIA ===")
    if classes_ausentes.empty:
        print("Nenhuma.")
    else:
        print(classes_ausentes.to_string(index=False))

    print(f"\nArquivos salvos em: {SAIDA.resolve()}")
    print("DIAGNÓSTICO: OK")


if __name__ == "__main__":
    main()
