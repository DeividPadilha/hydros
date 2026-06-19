"""
Treinamento do APS do Hydros.

APS significa Agente Preditivo Supervisionado.

Este script treina diferentes algoritmos supervisionados
para gerar a evidência preditiva Eaps a partir de Xt.

No modelo Hydros:

Xt = F(H(Ui))
Eaps = M(Xt)

Algoritmos treinados:

- Random Forest
- Gradient Boosting
- Decision Tree
"""

from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier

from src.services.feature_extractor import FeatureExtractor


CAMINHO_BASE = "data/historico_treinamento_aps.csv"
CAMINHO_MODELOS = Path("src/models")


def preparar_base():
    """
    Prepara a base de treinamento do APS.

    Para cada linha do histórico, o script monta Xt = F(H(Ui)),
    usando todos os contextos disponíveis até aquele instante.
    """

    df = pd.read_csv(
        CAMINHO_BASE
    )

    extrator = FeatureExtractor()

    registros_x = []
    rotulos_y = []

    # Começa após alguns registros para formar histórico mínimo
    for indice in range(4, len(df)):
        historico = df.iloc[: indice + 1].copy()

        xt = extrator.extrair(
            historico
        )

        registros_x.append(
            xt.iloc[0].to_dict()
        )

        rotulos_y.append(
            df.iloc[indice]["estresse_hidrico"]
        )

    x = pd.DataFrame(
        registros_x
    )

    y = pd.Series(
        rotulos_y
    )

    return x, y


def codificar_categorias(x, y):
    """
    Codifica variáveis categóricas e o alvo.
    """

    CAMINHO_MODELOS.mkdir(
        parents=True,
        exist_ok=True
    )

    colunas_categoricas = [
        "cultura",
        "loc",
        "solo",
        "estagio_fenologico"
    ]

    nomes_arquivos_encoders = {
        "cultura": "aps_cultura_encoder.pkl",
        "loc": "aps_loc_encoder.pkl",
        "solo": "aps_solo_encoder.pkl",
        "estagio_fenologico": "aps_fenologico_encoder.pkl"
    }

    for coluna in colunas_categoricas:
        encoder = LabelEncoder()

        x[coluna] = encoder.fit_transform(
            x[coluna].astype(str)
        )

        joblib.dump(
            encoder,
            CAMINHO_MODELOS / nomes_arquivos_encoders[coluna]
        )

    label_encoder = LabelEncoder()

    y_codificado = label_encoder.fit_transform(
        y.astype(str)
    )

    joblib.dump(
        label_encoder,
        CAMINHO_MODELOS / "aps_label_encoder.pkl"
    )

    features = list(
        x.columns
    )

    joblib.dump(
        features,
        CAMINHO_MODELOS / "aps_features.pkl"
    )

    return x, y_codificado, label_encoder, features


def obter_modelos():
    """
    Retorna os algoritmos supervisionados disponíveis para o APS.
    """

    modelos = {
        "random_forest": RandomForestClassifier(
            n_estimators=150,
            random_state=42,
            class_weight="balanced"
        ),
        "gradient_boosting": GradientBoostingClassifier(
            random_state=42
        ),
        "decision_tree": DecisionTreeClassifier(
            random_state=42,
            class_weight="balanced",
            max_depth=6
        )
    }

    return modelos


def treinar_modelos(x, y, label_encoder):
    """
    Treina todos os modelos do APS.
    """

    x_treino, x_teste, y_treino, y_teste = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42
    )

    modelos = obter_modelos()

    nomes_arquivos_modelos = {
        "random_forest": "aps_random_forest_model.pkl",
        "gradient_boosting": "aps_gradient_boosting_model.pkl",
        "decision_tree": "aps_decision_tree_model.pkl"
    }

    for nome_modelo, modelo in modelos.items():
        print("\n========================================")
        print(f"Treinando APS com algoritmo: {nome_modelo}")

        modelo.fit(
            x_treino,
            y_treino
        )

        predicoes = modelo.predict(
            x_teste
        )

        acuracia = accuracy_score(
            y_teste,
            predicoes
        )

        print(f"Acurácia: {acuracia:.2f}")

        print("\nRelatório de classificação:")

        print(
            classification_report(
                y_teste,
                predicoes,
                labels=range(len(label_encoder.classes_)),
                target_names=label_encoder.classes_,
                zero_division=0
            )
        )

        caminho_modelo = CAMINHO_MODELOS / nomes_arquivos_modelos[nome_modelo]

        joblib.dump(
            modelo,
            caminho_modelo
        )

        print(f"Modelo salvo em: {caminho_modelo}")

        # Mantém compatibilidade com versões anteriores
        if nome_modelo == "random_forest":
            joblib.dump(
                modelo,
                CAMINHO_MODELOS / "hydros_aps_model.pkl"
            )


def main():
    """
    Executa o treinamento completo do APS.
    """

    print("Preparando base do APS...")

    x, y = preparar_base()

    x, y_codificado, label_encoder, features = codificar_categorias(
        x,
        y
    )

    print(f"Total de registros usados no treinamento: {len(x)}")
    print(f"Total de features: {len(features)}")
    print(f"Classes do alvo: {list(label_encoder.classes_)}")

    treinar_modelos(
        x,
        y_codificado,
        label_encoder
    )

    print("\nTreinamento dos modelos APS concluído com sucesso.")


if __name__ == "__main__":
    main()
