"""
Agente ACL do Hydros.

No código atual, mantemos o nome ACL para não quebrar o projeto.
Conceitualmente, este agente representa o APS,
Agente Preditivo Supervisionado descrito na proposta.

Responsabilidade:
carregar o modelo Random Forest treinado,
preparar o contexto agrícola atual
e prever a criticidade hídrica.
"""

import joblib


class ACLAgent:
    """
    Agente classificador baseado em Random Forest.
    """

    def __init__(self):
        """
        Inicializa o agente carregando:
        modelo treinado,
        encoder do alvo,
        encoder da cultura,
        encoder da localização,
        encoder do solo,
        encoder fenológico.
        """

        # Carrega o modelo Random Forest treinado
        self.model = joblib.load(
            "src/models/hydros_acl_model.pkl"
        )

        # Carrega o encoder do alvo
        # Converte o número previsto em texto
        # Exemplo: baixo, moderado, alto ou critico
        self.label_encoder = joblib.load(
            "src/models/label_encoder.pkl"
        )

        # Carrega o encoder da cultura
        self.encoder_cultura = joblib.load(
            "src/models/cultura_encoder.pkl"
        )

        # Carrega o encoder da localização
        self.encoder_loc = joblib.load(
            "src/models/loc_encoder.pkl"
        )

        # Carrega o encoder do solo
        self.encoder_solo = joblib.load(
            "src/models/solo_encoder.pkl"
        )

        # Carrega o encoder do estágio fenológico
        self.encoder_fenologico = joblib.load(
            "src/models/fenologico_encoder.pkl"
        )

        # Features oficiais usadas pelo modelo APS
        # A ordem precisa ser a mesma usada no treinamento
        self.features = [
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

    def classificar(self, df):
        """
        Classifica a criticidade hídrica do contexto mais recente.
        """

        # Copia apenas a última linha do histórico
        # Essa linha representa o contexto agrícola atual
        contexto_atual = df.iloc[[-1]].copy()

        # Converte cultura para número
        contexto_atual["cultura"] = self.encoder_cultura.transform(
            contexto_atual["cultura"]
        )

        # Converte localização para número
        contexto_atual["loc"] = self.encoder_loc.transform(
            contexto_atual["loc"]
        )

        # Converte tipo de solo para número
        contexto_atual["solo"] = self.encoder_solo.transform(
            contexto_atual["solo"]
        )

        # Converte estágio fenológico para número
        contexto_atual["estagio_fenologico"] = self.encoder_fenologico.transform(
            contexto_atual["estagio_fenologico"]
        )

        # Seleciona somente as features usadas no treinamento
        contexto_features = contexto_atual[self.features]

        # Executa a predição do Random Forest
        predicao = self.model.predict(
            contexto_features
        )[0]

        # Obtém as probabilidades das classes
        probabilidades = self.model.predict_proba(
            contexto_features
        )[0]

        # Converte a classe numérica para texto
        classe = self.label_encoder.inverse_transform(
            [predicao]
        )[0]

        # Calcula a confiança usando a maior probabilidade
        confianca = round(
            float(max(probabilidades)),
            2
        )

        # Retorna a evidência preditiva
        return {
            "agente": "APS",
            "nome_arquivo": "acl_agent.py",
            "modelo": "Random Forest",
            "risco_previsto": classe,
            "criticidade": classe,
            "evidencia": classe,
            "confianca": confianca,
            "features_usadas": self.features,
            "motivo": "classificação supervisionada baseada no contexto agrícola mais recente"
        }