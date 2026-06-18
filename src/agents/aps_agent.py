"""
APS Agent do Hydros.

APS significa Agente Preditivo Supervisionado.

Responsabilidade no modelo Hydros:
usar um modelo supervisionado de classificação para produzir
a evidência preditiva Eaps a partir de Xt.

No modelo:
Xt = F(H(Ui))
Eaps = APS(Xt)

Modelo atual:
Random Forest
"""

import joblib

from src.services.feature_extractor import FeatureExtractor


class APSAgent:
    """
    Agente Preditivo Supervisionado do modelo Hydros.
    """

    def __init__(self):
        """
        Inicializa o APS carregando modelo, encoders e features.
        """

        self.nome_evidencia = "Eaps"

        # Extrator F(H(Ui))
        self.extrator = FeatureExtractor()

        # Modelo Random Forest treinado
        self.modelo = joblib.load(
            "src/models/hydros_aps_model.pkl"
        )

        # Encoder do alvo
        self.label_encoder = joblib.load(
            "src/models/aps_label_encoder.pkl"
        )

        # Lista de features usadas no treinamento
        self.features = joblib.load(
            "src/models/aps_features.pkl"
        )

        # Encoders das variáveis categóricas
        self.encoder_cultura = joblib.load(
            "src/models/aps_cultura_encoder.pkl"
        )

        self.encoder_loc = joblib.load(
            "src/models/aps_loc_encoder.pkl"
        )

        self.encoder_solo = joblib.load(
            "src/models/aps_solo_encoder.pkl"
        )

        self.encoder_fenologico = joblib.load(
            "src/models/aps_fenologico_encoder.pkl"
        )

    def classificar(self, df):
        """
        Classifica a condição hídrica usando Xt = F(H(Ui)).
        """

        # Extrai Xt a partir do histórico de contexto
        xt = self.extrator.extrair(
            df
        )

        # Codifica variáveis categóricas
        xt["cultura"] = self.transformar_categoria_segura(
            self.encoder_cultura,
            xt["cultura"].iloc[0]
        )

        xt["loc"] = self.transformar_categoria_segura(
            self.encoder_loc,
            xt["loc"].iloc[0]
        )

        xt["solo"] = self.transformar_categoria_segura(
            self.encoder_solo,
            xt["solo"].iloc[0]
        )

        xt["estagio_fenologico"] = self.transformar_categoria_segura(
            self.encoder_fenologico,
            xt["estagio_fenologico"].iloc[0]
        )

        # Garante a mesma ordem de features usada no treinamento
        xt_modelo = xt[self.features]

        # Executa predição
        predicao = self.modelo.predict(
            xt_modelo
        )[0]

        # Probabilidades das classes
        probabilidades = self.modelo.predict_proba(
            xt_modelo
        )[0]

        # Converte predição numérica para texto
        eaps = self.label_encoder.inverse_transform(
            [predicao]
        )[0]

        # Confiança baseada na maior probabilidade
        confianca = round(
            float(max(probabilidades)),
            2
        )

        # Monta distribuição de probabilidades por classe
        distribuicao_probabilidades = {}

        for indice, classe in enumerate(self.label_encoder.classes_):
            distribuicao_probabilidades[classe] = round(
                float(probabilidades[indice]),
                2
            )

        # Recupera principais atributos usados
        atributos_xt = xt_modelo.iloc[0].to_dict()

        return {
            "agente": "APS",
            "nome_agente": "Agente Preditivo Supervisionado",
            "modelo": "Random Forest",
            "evidencia_nome": self.nome_evidencia,
            "Eaps": eaps,
            "evidencia": eaps,
            "criticidade": eaps,
            "risco_previsto": eaps,
            "confianca": confianca,
            "features_usadas": self.features,
            "probabilidades": distribuicao_probabilidades,
            "Xt": atributos_xt,
            "motivo": "classificação supervisionada baseada no vetor Xt extraído do histórico de contexto H(Ui)"
        }

    def transformar_categoria_segura(self, encoder, valor):
        """
        Transforma uma categoria textual em número.

        Se aparecer uma categoria não vista no treinamento,
        usa a primeira categoria conhecida como fallback.
        """

        valor = str(
            valor
        )

        if valor not in encoder.classes_:
            valor = encoder.classes_[0]

        valor_transformado = encoder.transform(
            [valor]
        )[0]

        return valor_transformado
