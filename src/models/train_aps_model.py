"""
Treinamento do APS do Hydros.

APS significa Agente Preditivo Supervisionado.

Este script treina o modelo Random Forest usando o vetor:

Xt = F(H(Ui))

Ou seja:
o modelo não usa apenas a última linha do CSV.
Ele usa atributos extraídos do histórico de contexto da unidade de manejo.
"""

import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report

from src.services.feature_extractor import FeatureExtractor


# Caminho da base de treinamento
CAMINHO_BASE = "data/historico_treinamento_acl.csv"


# Caminhos de saída do modelo APS
CAMINHO_MODELO = "src/models/hydros_aps_model.pkl"
CAMINHO_LABEL_ENCODER = "src/models/aps_label_encoder.pkl"
CAMINHO_FEATURES = "src/models/aps_features.pkl"

CAMINHO_ENCODER_CULTURA = "src/models/aps_cultura_encoder.pkl"
CAMINHO_ENCODER_LOC = "src/models/aps_loc_encoder.pkl"
CAMINHO_ENCODER_SOLO = "src/models/aps_solo_encoder.pkl"
CAMINHO_ENCODER_FENOLOGICO = "src/models/aps_fenologico_encoder.pkl"


def montar_base_com_xt(df):
    """
    Monta uma base de treinamento usando Xt = F(H(Ui)).

    Para cada instante t, usa o histórico até aquele ponto
    e extrai os atributos históricos com o FeatureExtractor.
    """

    extrator = FeatureExtractor()

    registros_xt = []

    # Começa a partir da janela mínima
    # Isso garante que existam dados históricos para calcular tendências
    for indice in range(extrator.tamanho_janela - 1, len(df)):
        historico_parcial = df.iloc[:indice + 1].copy()

        xt = extrator.extrair(
            historico_parcial
        )

        # O alvo é o estresse hídrico do contexto atual
        xt["estresse_hidrico"] = df.iloc[indice]["estresse_hidrico"]

        registros_xt.append(
            xt
        )

    base_xt = pd.concat(
        registros_xt,
        ignore_index=True
    )

    return base_xt


def treinar_modelo():
    """
    Executa o treinamento completo do APS.
    """

    print("\nCarregando base de treinamento...")
    df = pd.read_csv(
        CAMINHO_BASE
    )

    print("Montando Xt = F(H(Ui))...")
    base_xt = montar_base_com_xt(
        df
    )

    # Encoders das variáveis categóricas
    encoder_cultura = LabelEncoder()
    encoder_loc = LabelEncoder()
    encoder_solo = LabelEncoder()
    encoder_fenologico = LabelEncoder()

    base_xt["cultura"] = encoder_cultura.fit_transform(
        base_xt["cultura"]
    )

    base_xt["loc"] = encoder_loc.fit_transform(
        base_xt["loc"]
    )

    base_xt["solo"] = encoder_solo.fit_transform(
        base_xt["solo"]
    )

    base_xt["estagio_fenologico"] = encoder_fenologico.fit_transform(
        base_xt["estagio_fenologico"]
    )

    # Variável alvo
    label_encoder = LabelEncoder()

    y = label_encoder.fit_transform(
        base_xt["estresse_hidrico"]
    )

    # Features usadas pelo APS
    features = [
        coluna
        for coluna in base_xt.columns
        if coluna != "estresse_hidrico"
    ]

    X = base_xt[features]

    # Divide treino e teste
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    # Modelo Random Forest
    modelo = RandomForestClassifier(
        n_estimators=150,
        random_state=42,
        class_weight="balanced"
    )

    print("Treinando modelo APS...")
    modelo.fit(
        X_train,
        y_train
    )

    # Avaliação simples
    y_pred = modelo.predict(
        X_test
    )

    acuracia = accuracy_score(
        y_test,
        y_pred
    )

    print("\nAcurácia do APS:")
    print(acuracia)

    print("\nRelatório de classificação:")
    print(
        classification_report(
            y_test,
            y_pred,
            labels=range(len(label_encoder.classes_)),
            target_names=label_encoder.classes_,
            zero_division=0
        )
    )

    # Salva modelo e artefatos
    joblib.dump(
        modelo,
        CAMINHO_MODELO
    )

    joblib.dump(
        label_encoder,
        CAMINHO_LABEL_ENCODER
    )

    joblib.dump(
        features,
        CAMINHO_FEATURES
    )

    joblib.dump(
        encoder_cultura,
        CAMINHO_ENCODER_CULTURA
    )

    joblib.dump(
        encoder_loc,
        CAMINHO_ENCODER_LOC
    )

    joblib.dump(
        encoder_solo,
        CAMINHO_ENCODER_SOLO
    )

    joblib.dump(
        encoder_fenologico,
        CAMINHO_ENCODER_FENOLOGICO
    )

    print("\nModelo APS treinado com sucesso.")
    print(f"Modelo salvo em: {CAMINHO_MODELO}")
    print(f"Features salvas em: {CAMINHO_FEATURES}")


if __name__ == "__main__":
    treinar_modelo()


