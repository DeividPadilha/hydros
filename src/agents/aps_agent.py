"""
APS Agent do Hydros.

APS significa Agente Preditivo Supervisionado.

Responsabilidade no modelo Hydros:
usar um modelo supervisionado de classificação para produzir
a evidência preditiva Eaps a partir de Xt.

No modelo:

Xt = F(H(Ui))
Eaps = APS(Xt)

Nesta versão, o APS pode usar diferentes algoritmos supervisionados:

- Random Forest
- Gradient Boosting
- Decision Tree

O algoritmo padrão é Random Forest.
"""

from pathlib import Path

import joblib

from src.config.hydros_terms import ALGORITMO_APS_PADRAO
from src.config.hydros_terms import ALGORITMOS_APS
from src.services.feature_extractor import FeatureExtractor


class APSAgent:
    """
    Agente Preditivo Supervisionado do modelo Hydros.
    """

    def __init__(self, algoritmo=ALGORITMO_APS_PADRAO):
        """
        Inicializa o APS carregando modelo, encoders e features.

        Parameters
        ----------
        algoritmo : str
            Algoritmo supervisionado utilizado pelo APS.
        """

        self.nome_evidencia = "Eaps"

        if algoritmo not in ALGORITMOS_APS:
            algoritmo = ALGORITMO_APS_PADRAO

        self.algoritmo = algoritmo
        self.nome_modelo = ALGORITMOS_APS[algoritmo]

        # Extrator F(H(Ui))
        self.extrator = FeatureExtractor()

        # Caminhos dos modelos disponíveis
        self.caminhos_modelos = {
            "random_forest": Path("src/models/aps_random_forest_model.pkl"),
            "gradient_boosting": Path("src/models/aps_gradient_boosting_model.pkl"),
            "decision_tree": Path("src/models/aps_decision_tree_model.pkl")
        }

        caminho_modelo = self.caminhos_modelos[self.algoritmo]

        if not caminho_modelo.exists():
            raise FileNotFoundError(
                f"Modelo APS não encontrado: {caminho_modelo}. "
                "Execute: python -m src.models.train_aps_model"
            )

        # Modelo supervisionado escolhido
        self.modelo = joblib.load(
            caminho_modelo
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

        for classe in self.label_encoder.classes_:
            distribuicao_probabilidades[classe] = 0.0

        for indice, classe_codificada in enumerate(self.modelo.classes_):
            classe_nome = self.label_encoder.inverse_transform(
                [classe_codificada]
            )[0]

            distribuicao_probabilidades[classe_nome] = round(
                float(probabilidades[indice]),
                2
            )

        # Recupera principais atributos usados
        atributos_xt = xt_modelo.iloc[0].to_dict()

        return {
            "agente": "APS",
            "nome_agente": "Agente Preditivo Supervisionado",
            "algoritmo": self.algoritmo,
            "modelo": self.nome_modelo,
            "evidencia_nome": self.nome_evidencia,
            "Eaps": eaps,
            "evidencia": eaps,
            "criticidade": eaps,
            "risco_previsto": eaps,
            "confianca": confianca,
            "features_usadas": self.features,
            "probabilidades": distribuicao_probabilidades,
            "Xt": atributos_xt,
            "motivo": (
                "classificação supervisionada baseada no vetor Xt "
                "extraído do histórico de contexto H(Ui)"
            )
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
