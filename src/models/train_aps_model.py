"""Treinamento cientificamente rastreável do APS do Hydros.

Este script evita a divisão aleatória de registros consecutivos da mesma
trajetória. A separação ocorre por grupo de cenário quando há grupos
independentes suficientes. Quando a base contém somente uma trajetória, a
divisão é cronológica em treino, validação e teste.

O script também salva metadados do domínio de treinamento, distribuição das
classes, faixas numéricas, versões e hashes dos modelos. Esses artefatos são
consumidos pelo ``APSAgent`` para detectar inferências fora do domínio.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    f1_score,
    matthews_corrcoef,
)
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier

from src.services.feature_extractor import FeatureExtractor


ROOT = Path(__file__).resolve().parents[2]
CAMINHO_BASE = ROOT / "data" / "historico_treinamento_aps.csv"
CAMINHO_MODELOS = ROOT / "src" / "models"
RANDOM_STATE = 42
JANELA_MINIMA = 5

COLUNAS_CATEGORICAS = [
    "cultura",
    "loc",
    "solo",
    "estagio_fenologico",
]
ARQUIVOS_ENCODERS = {
    "cultura": "aps_cultura_encoder.pkl",
    "loc": "aps_loc_encoder.pkl",
    "solo": "aps_solo_encoder.pkl",
    "estagio_fenologico": "aps_fenologico_encoder.pkl",
}
ARQUIVOS_MODELOS = {
    "random_forest": "aps_random_forest_model.pkl",
    "gradient_boosting": "aps_gradient_boosting_model.pkl",
    "decision_tree": "aps_decision_tree_model.pkl",
}


def preparar_base() -> Tuple[pd.DataFrame, pd.Series, pd.Series, Dict[str, Any]]:
    """Constrói Xt sem misturar registros futuros no histórico de cada linha."""

    df = pd.read_csv(CAMINHO_BASE)
    if df.empty:
        raise ValueError("A base de treinamento do APS está vazia.")

    if "estresse_hidrico" not in df.columns:
        raise ValueError("A base deve possuir a coluna estresse_hidrico.")

    group_columns = identificar_colunas_grupo(df)
    if group_columns:
        groups = df[group_columns].astype(str).agg("|".join, axis=1)
    else:
        groups = pd.Series("trajetoria_unica", index=df.index)

    order_column = "data" if "data" in df.columns else None
    working = df.copy()
    working["__grupo_aps"] = groups
    working["__ordem_original"] = np.arange(len(working))

    if order_column:
        working["__data_aps"] = pd.to_datetime(
            working[order_column], errors="coerce"
        )
        working = working.sort_values(
            ["__grupo_aps", "__data_aps", "__ordem_original"],
            kind="stable",
        )
    else:
        working = working.sort_values(
            ["__grupo_aps", "__ordem_original"], kind="stable"
        )

    extrator = FeatureExtractor()
    registros_x: List[Dict[str, Any]] = []
    rotulos_y: List[str] = []
    grupos_saida: List[str] = []
    ordens_saida: List[int] = []

    for group_id, group_df in working.groupby("__grupo_aps", sort=False):
        group_df = group_df.reset_index(drop=True)
        if len(group_df) < JANELA_MINIMA:
            continue

        for indice in range(JANELA_MINIMA - 1, len(group_df)):
            historico = group_df.iloc[: indice + 1].copy()
            xt = extrator.extrair(historico)
            registros_x.append(xt.iloc[0].to_dict())
            rotulos_y.append(str(group_df.iloc[indice]["estresse_hidrico"]))
            grupos_saida.append(str(group_id))
            ordens_saida.append(int(indice))

    if not registros_x:
        raise ValueError(
            "Não foi possível formar janelas de treinamento. "
            f"Cada grupo deve possuir pelo menos {JANELA_MINIMA} registros."
        )

    metadata = {
        "source_contexts": int(len(df)),
        "generated_samples": int(len(registros_x)),
        "group_columns": group_columns,
        "number_of_groups": int(len(set(grupos_saida))),
        "window_size": int(extrator.tamanho_janela),
    }

    x = pd.DataFrame(registros_x)
    y = pd.Series(rotulos_y, name="estresse_hidrico")
    sample_groups = pd.Series(grupos_saida, name="grupo")
    x["__ordem_aps"] = ordens_saida

    return x, y, sample_groups, metadata


def identificar_colunas_grupo(df: pd.DataFrame) -> List[str]:
    """Seleciona identificadores capazes de separar trajetórias independentes."""

    candidates = [
        "cenario_id",
        "execucao_id",
        "safra",
        "unidade_manejo",
        "talhao",
    ]
    available = [column for column in candidates if column in df.columns]

    # Uma coluna constante não cria grupos independentes e não deve ser usada
    # para simular uma validação por cenário inexistente.
    informative = [column for column in available if df[column].nunique() > 1]
    return informative


def separar_indices(
    x: pd.DataFrame,
    groups: pd.Series,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, str]:
    """Separa treino/validação/teste sem vazamento temporal."""

    unique_groups = list(dict.fromkeys(groups.astype(str).tolist()))

    if len(unique_groups) >= 3:
        rng = np.random.default_rng(RANDOM_STATE)
        shuffled = np.array(unique_groups, dtype=object)
        rng.shuffle(shuffled)

        n_groups = len(shuffled)
        n_train = max(1, int(round(n_groups * 0.60)))
        n_validation = max(1, int(round(n_groups * 0.20)))
        if n_train + n_validation >= n_groups:
            n_train = max(1, n_groups - 2)
            n_validation = 1

        train_groups = set(shuffled[:n_train].tolist())
        validation_groups = set(
            shuffled[n_train : n_train + n_validation].tolist()
        )
        test_groups = set(shuffled[n_train + n_validation :].tolist())

        train_idx = np.flatnonzero(groups.astype(str).isin(train_groups))
        validation_idx = np.flatnonzero(
            groups.astype(str).isin(validation_groups)
        )
        test_idx = np.flatnonzero(groups.astype(str).isin(test_groups))
        strategy = "divisao_por_grupos_independentes_60_20_20"
        return train_idx, validation_idx, test_idx, strategy

    # Com uma ou duas trajetórias, cada grupo é dividido cronologicamente.
    # Isso preserva o futuro no teste e evita que janelas consecutivas sejam
    # aleatoriamente distribuídas entre treino e teste.
    train_indices: List[int] = []
    validation_indices: List[int] = []
    test_indices: List[int] = []

    order_values = x["__ordem_aps"].to_numpy()
    for group_id in unique_groups:
        group_idx = np.flatnonzero(groups.astype(str).to_numpy() == group_id)
        group_idx = group_idx[np.argsort(order_values[group_idx], kind="stable")]
        n = len(group_idx)
        cut_train = max(1, int(np.floor(n * 0.60)))
        cut_validation = max(cut_train + 1, int(np.floor(n * 0.80)))
        cut_validation = min(cut_validation, n - 1) if n > 2 else cut_train

        train_indices.extend(group_idx[:cut_train].tolist())
        validation_indices.extend(group_idx[cut_train:cut_validation].tolist())
        test_indices.extend(group_idx[cut_validation:].tolist())

    if not validation_indices or not test_indices:
        raise ValueError(
            "A base é pequena demais para divisão cronológica em três conjuntos."
        )

    strategy = "divisao_cronologica_por_trajetoria_60_20_20"
    return (
        np.asarray(train_indices, dtype=int),
        np.asarray(validation_indices, dtype=int),
        np.asarray(test_indices, dtype=int),
        strategy,
    )


def ajustar_encoders(
    x_train: pd.DataFrame,
    y_train: pd.Series,
) -> Tuple[Dict[str, LabelEncoder], LabelEncoder]:
    CAMINHO_MODELOS.mkdir(parents=True, exist_ok=True)

    encoders: Dict[str, LabelEncoder] = {}
    for column in COLUNAS_CATEGORICAS:
        encoder = LabelEncoder()
        encoder.fit(x_train[column].astype(str))
        encoders[column] = encoder
        joblib.dump(encoder, CAMINHO_MODELOS / ARQUIVOS_ENCODERS[column])

    target_encoder = LabelEncoder()
    target_encoder.fit(y_train.astype(str))
    joblib.dump(target_encoder, CAMINHO_MODELOS / "aps_label_encoder.pkl")
    return encoders, target_encoder


def transformar_categorias(
    x: pd.DataFrame,
    encoders: Dict[str, LabelEncoder],
) -> Tuple[pd.DataFrame, Dict[str, List[str]]]:
    transformed = x.copy()
    unknown: Dict[str, List[str]] = {}

    for column, encoder in encoders.items():
        known = set(str(item) for item in encoder.classes_)
        values = transformed[column].astype(str)
        unknown_values = sorted(set(values) - known)
        if unknown_values:
            unknown[column] = unknown_values
        mapping = {str(value): index for index, value in enumerate(encoder.classes_)}
        transformed[column] = values.map(mapping).fillna(-1).astype(int)

    return transformed, unknown


def transformar_alvo(
    y: pd.Series,
    encoder: LabelEncoder,
    split_name: str,
) -> np.ndarray:
    known = set(str(item) for item in encoder.classes_)
    unknown = sorted(set(y.astype(str)) - known)
    if unknown:
        raise ValueError(
            f"O conjunto {split_name} contém classes ausentes no treino: {unknown}. "
            "Gere mais cenários ou ajuste a separação sem usar o teste no treino."
        )
    return encoder.transform(y.astype(str))


def obter_modelos() -> Dict[str, Any]:
    return {
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            random_state=RANDOM_STATE,
            class_weight="balanced",
            n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingClassifier(
            random_state=RANDOM_STATE,
        ),
        "decision_tree": DecisionTreeClassifier(
            random_state=RANDOM_STATE,
            class_weight="balanced",
            max_depth=6,
        ),
    }


def avaliar(
    model: Any,
    x: pd.DataFrame,
    y: np.ndarray,
    label_encoder: LabelEncoder,
    split_name: str,
) -> Dict[str, Any]:
    predictions = model.predict(x)
    metrics = {
        "accuracy": float(accuracy_score(y, predictions)),
        "balanced_accuracy": float(balanced_accuracy_score(y, predictions)),
        "f1_macro": float(f1_score(y, predictions, average="macro", zero_division=0)),
        "mcc": float(matthews_corrcoef(y, predictions)),
    }

    print(f"\n{split_name}")
    for name, value in metrics.items():
        print(f"  {name}: {value:.4f}")
    print(
        classification_report(
            y,
            predictions,
            labels=range(len(label_encoder.classes_)),
            target_names=label_encoder.classes_,
            zero_division=0,
        )
    )
    return metrics


def hash_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def serializable_number(value: Any) -> float:
    number = float(value)
    return number if np.isfinite(number) else 0.0


def construir_metadata(
    *,
    x_raw: pd.DataFrame,
    y_raw: pd.Series,
    train_idx: np.ndarray,
    validation_idx: np.ndarray,
    test_idx: np.ndarray,
    split_strategy: str,
    base_metadata: Dict[str, Any],
    encoders: Dict[str, LabelEncoder],
    model_metrics: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    feature_columns = [column for column in x_raw.columns if column != "__ordem_aps"]
    numeric_columns = [
        column for column in feature_columns if column not in COLUNAS_CATEGORICAS
    ]
    x_train_raw = x_raw.iloc[train_idx]

    numeric_ranges = {
        column: {
            "min": serializable_number(pd.to_numeric(x_train_raw[column], errors="coerce").min()),
            "max": serializable_number(pd.to_numeric(x_train_raw[column], errors="coerce").max()),
        }
        for column in numeric_columns
    }
    feature_defaults = {
        column: serializable_number(
            pd.to_numeric(x_train_raw[column], errors="coerce").median()
        )
        for column in numeric_columns
    }
    feature_defaults.update({column: -1 for column in COLUNAS_CATEGORICAS})

    model_hashes = {}
    for algorithm, filename in ARQUIVOS_MODELOS.items():
        path = CAMINHO_MODELOS / filename
        if path.exists():
            model_hashes[algorithm] = hash_file(path)

    return {
        "schema_version": "1.0",
        "model_version": datetime.now(timezone.utc).strftime(
            "aps-%Y%m%dT%H%M%SZ"
        ),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "training_source": str(CAMINHO_BASE.relative_to(ROOT)),
        "training_split": split_strategy,
        "scientific_status": "modelo_treinado_sem_vazamento_temporal",
        "confidence_calibration": "probabilidades_nao_calibradas",
        "source_contexts": base_metadata["source_contexts"],
        "generated_samples": base_metadata["generated_samples"],
        "window_size": base_metadata["window_size"],
        "group_columns": base_metadata["group_columns"],
        "number_of_groups": base_metadata["number_of_groups"],
        "split_sizes": {
            "train": int(len(train_idx)),
            "validation": int(len(validation_idx)),
            "test": int(len(test_idx)),
        },
        "target_distribution": dict(Counter(y_raw.astype(str))),
        "training_target_distribution": dict(
            Counter(y_raw.iloc[train_idx].astype(str))
        ),
        "categorical_domains": {
            column: [str(item) for item in encoder.classes_]
            for column, encoder in encoders.items()
        },
        "numeric_ranges": numeric_ranges,
        "feature_defaults": feature_defaults,
        "model_metrics": model_metrics,
        "model_hashes": model_hashes,
        "known_limitations": [
            "As probabilidades dos classificadores ainda não foram calibradas.",
            "Classes raras exigem geração adicional de cenários independentes.",
            "Resultados simulados não substituem validação com dados agrícolas reais.",
        ],
    }


def main() -> None:
    print("Preparando base do APS sem vazamento temporal...")
    x_raw, y_raw, groups, base_metadata = preparar_base()
    train_idx, validation_idx, test_idx, split_strategy = separar_indices(
        x_raw, groups
    )

    x_features = x_raw.drop(columns=["__ordem_aps"])
    x_train_raw = x_features.iloc[train_idx].copy()
    y_train_raw = y_raw.iloc[train_idx].copy()

    encoders, target_encoder = ajustar_encoders(x_train_raw, y_train_raw)

    x_train, unknown_train = transformar_categorias(x_train_raw, encoders)
    x_validation, unknown_validation = transformar_categorias(
        x_features.iloc[validation_idx].copy(), encoders
    )
    x_test, unknown_test = transformar_categorias(
        x_features.iloc[test_idx].copy(), encoders
    )

    if unknown_train:
        raise RuntimeError("Categorias desconhecidas foram encontradas no treino.")
    if unknown_validation:
        print("Aviso: categorias desconhecidas na validação:", unknown_validation)
    if unknown_test:
        print("Aviso: categorias desconhecidas no teste:", unknown_test)

    y_train = transformar_alvo(y_train_raw, target_encoder, "treino")
    y_validation = transformar_alvo(
        y_raw.iloc[validation_idx], target_encoder, "validação"
    )
    y_test = transformar_alvo(y_raw.iloc[test_idx], target_encoder, "teste")

    features = list(x_train.columns)
    joblib.dump(features, CAMINHO_MODELOS / "aps_features.pkl")

    print(f"Estratégia de divisão: {split_strategy}")
    print(
        "Amostras: "
        f"treino={len(train_idx)}, validação={len(validation_idx)}, "
        f"teste={len(test_idx)}"
    )
    print("Classes no treino:", dict(Counter(y_train_raw.astype(str))))

    all_metrics: Dict[str, Dict[str, Any]] = {}
    for algorithm, model in obter_modelos().items():
        print("\n========================================")
        print(f"Treinando APS com algoritmo: {algorithm}")
        model.fit(x_train, y_train)

        validation_metrics = avaliar(
            model, x_validation, y_validation, target_encoder, "VALIDAÇÃO"
        )
        test_metrics = avaliar(
            model, x_test, y_test, target_encoder, "TESTE FINAL"
        )
        all_metrics[algorithm] = {
            "validation": validation_metrics,
            "test": test_metrics,
        }

        model_path = CAMINHO_MODELOS / ARQUIVOS_MODELOS[algorithm]
        joblib.dump(model, model_path)
        print(f"Modelo salvo em: {model_path}")

        if algorithm == "random_forest":
            joblib.dump(model, CAMINHO_MODELOS / "hydros_aps_model.pkl")

    metadata = construir_metadata(
        x_raw=x_features,
        y_raw=y_raw,
        train_idx=train_idx,
        validation_idx=validation_idx,
        test_idx=test_idx,
        split_strategy=split_strategy,
        base_metadata=base_metadata,
        encoders=encoders,
        model_metrics=all_metrics,
    )
    metadata_path = CAMINHO_MODELOS / "aps_model_metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Metadados salvos em: {metadata_path}")
    print("\nTreinamento APS concluído sem divisão aleatória de linhas consecutivas.")


if __name__ == "__main__":
    main()
