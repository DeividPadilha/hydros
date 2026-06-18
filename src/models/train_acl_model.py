"""
Treinamento do modelo Random Forest do APS.

APS significa Agente Preditivo Supervisionado.

No código atual, o arquivo ainda salva o modelo como ACL
para manter compatibilidade com o restante do projeto.

Este script treina o modelo usando o novo padrão de variáveis
do Hydros.
"""

import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report


# Carrega a base sintética de treinamento
df = pd.read_csv(
    "data/historico_treinamento_acl.csv"
)


# Encoder da cultura
# Converte soja em valor numérico
encoder_cultura = LabelEncoder()
df["cultura"] = encoder_cultura.fit_transform(
    df["cultura"]
)


# Encoder da localização
# Converte Brasil_MT_Jaciara em valor numérico
encoder_loc = LabelEncoder()
df["loc"] = encoder_loc.fit_transform(
    df["loc"]
)


# Encoder do tipo de solo
# Converte argiloso, arenoso ou outro tipo em valor numérico
encoder_solo = LabelEncoder()
df["solo"] = encoder_solo.fit_transform(
    df["solo"]
)


# Encoder do estágio fenológico
# Converte V3, R1, R5 etc em valores numéricos
encoder_fenologico = LabelEncoder()
df["estagio_fenologico"] = encoder_fenologico.fit_transform(
    df["estagio_fenologico"]
)


# Features oficiais do APS no novo padrão Hydros
# Essas variáveis representam o contexto agrícola ampliado
features = [
    "cultura",
    "loc",
    "solo",
    "precipitacao",
    "temperatura",
    "graus_dia",
    "evapotranspiracao",
    "coeficiente_cultura",
    "umidade_solo",
    "agua_disponivel",
    "irrigacao_aplicada",
    "estagio_fenologico",
    "produtividade"
]


# Variáveis de entrada do modelo
X = df[features]


# Variável alvo
# O modelo irá prever o nível de estresse hídrico
y = df["estresse_hidrico"]


# Encoder do alvo
# Converte baixo, moderado, alto e critico em números
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)


# Divide os dados
# 80% para treinamento
# 20% para teste
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.2,
    random_state=42
)


# Cria o modelo Random Forest
modelo = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)


# Treina o modelo
modelo.fit(
    X_train,
    y_train
)


# Realiza predição no conjunto de teste
y_pred = modelo.predict(
    X_test
)


# Calcula a acurácia
acuracia = accuracy_score(
    y_test,
    y_pred
)


print("\nAcurácia do modelo:")
print(acuracia)


print("\nRelatório de classificação:")
print(
    classification_report(
        y_test,
        y_pred
    )
)


# Salva o modelo Random Forest treinado
joblib.dump(
    modelo,
    "src/models/hydros_acl_model.pkl"
)


# Salva encoder do alvo
joblib.dump(
    label_encoder,
    "src/models/label_encoder.pkl"
)


# Salva encoder da cultura
joblib.dump(
    encoder_cultura,
    "src/models/cultura_encoder.pkl"
)


# Salva encoder da localização
joblib.dump(
    encoder_loc,
    "src/models/loc_encoder.pkl"
)


# Salva encoder do solo
joblib.dump(
    encoder_solo,
    "src/models/solo_encoder.pkl"
)


# Salva encoder fenológico
joblib.dump(
    encoder_fenologico,
    "src/models/fenologico_encoder.pkl"
)


print("\nModelo APS treinado com sucesso.")
print("Arquivos salvos em: src/models/")