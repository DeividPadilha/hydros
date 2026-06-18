"""
Ahid Agent do Hydros.

Ahid significa Agente Hídrico.

Responsabilidade no modelo Hydros:
analisar as variáveis hídricas do histórico de contexto
e produzir a evidência hídrica Ehid.

Variáveis analisadas:
solo = tipo de solo
us   = umidade do solo
ad   = água disponível no solo
irr  = irrigação aplicada
eh   = estresse hídrico

Saída:
Ehid em {baixo, moderado, alto, critico}
"""


class AhidAgent:
    """
    Agente hídrico do modelo Hydros.
    """

    def __init__(self):
        """
        Inicializa o agente hídrico.
        """

        self.tamanho_janela = 5
        self.nome_evidencia = "Ehid"

        self.variaveis_modelo = [
            "solo",
            "us",
            "ad",
            "irr",
            "eh"
        ]

        self.colunas_csv = [
            "solo",
            "umidade_solo",
            "agua_disponivel",
            "irrigacao_aplicada",
            "estresse_hidrico"
        ]

    def analisar(self, df):
        """
        Analisa o histórico de contexto e gera a evidência hídrica Ehid.
        """

        janela = df.tail(self.tamanho_janela)
        contexto_atual = janela.iloc[-1]

        solo = str(contexto_atual["solo"]).lower()
        umidade_solo = contexto_atual["umidade_solo"]
        agua_disponivel = contexto_atual["agua_disponivel"]
        irrigacao_aplicada = contexto_atual["irrigacao_aplicada"]
        estresse_hidrico = str(contexto_atual["estresse_hidrico"]).lower()

        umidade_media = janela["umidade_solo"].mean()
        agua_disponivel_media = janela["agua_disponivel"].mean()
        irrigacao_acumulada = janela["irrigacao_aplicada"].sum()

        primeira_umidade = janela["umidade_solo"].iloc[0]
        ultima_umidade = janela["umidade_solo"].iloc[-1]

        primeira_agua = janela["agua_disponivel"].iloc[0]
        ultima_agua = janela["agua_disponivel"].iloc[-1]

        if ultima_umidade < primeira_umidade:
            tendencia_umidade = "queda"
        elif ultima_umidade > primeira_umidade:
            tendencia_umidade = "aumento"
        else:
            tendencia_umidade = "estavel"

        if ultima_agua < primeira_agua:
            tendencia_agua = "queda"
        elif ultima_agua > primeira_agua:
            tendencia_agua = "aumento"
        else:
            tendencia_agua = "estavel"

        score = 0
        regras_acionadas = []

        # Regra hídrica 1:
        # umidade do solo baixa indica risco hídrico
        if umidade_solo < 30:
            score += 2
            regras_acionadas.append(
                "umidade do solo muito baixa"
            )

        elif umidade_solo < 45:
            score += 1
            regras_acionadas.append(
                "umidade do solo baixa"
            )

        # Regra hídrica 2:
        # água disponível baixa indica limitação hídrica
        if agua_disponivel < 45:
            score += 2
            regras_acionadas.append(
                "água disponível muito baixa"
            )

        elif agua_disponivel < 70:
            score += 1
            regras_acionadas.append(
                "água disponível baixa"
            )

        # Regra hídrica 3:
        # estresse hídrico informado no contexto
        if estresse_hidrico == "critico":
            score += 2
            regras_acionadas.append(
                "estresse hídrico crítico informado no contexto"
            )

        elif estresse_hidrico == "alto":
            score += 1
            regras_acionadas.append(
                "estresse hídrico alto informado no contexto"
            )

        elif estresse_hidrico == "moderado":
            score += 1
            regras_acionadas.append(
                "estresse hídrico moderado informado no contexto"
            )

        # Regra hídrica 4:
        # solo arenoso aumenta atenção quando a água está baixa
        if "arenoso" in solo and agua_disponivel < 70:
            score += 1
            regras_acionadas.append(
                "solo arenoso com baixa água disponível"
            )

        # Regra hídrica 5:
        # tendência de queda da umidade indica piora hídrica
        if tendencia_umidade == "queda":
            score += 1
            regras_acionadas.append(
                "tendência de queda da umidade do solo"
            )

        # Regra hídrica 6:
        # tendência de queda da água disponível indica perda hídrica acumulada
        if tendencia_agua == "queda":
            score += 1
            regras_acionadas.append(
                "tendência de queda da água disponível"
            )

        # Regra hídrica 7:
        # ausência de irrigação recente com baixa água disponível
        if irrigacao_acumulada == 0 and agua_disponivel < 70:
            score += 1
            regras_acionadas.append(
                "ausência de irrigação recente com baixa água disponível"
            )

        # Regra hídrica 8:
        # se houve irrigação, mas a condição segue ruim, há indício de insuficiência
        if irrigacao_acumulada > 20 and agua_disponivel < 60:
            score += 1
            regras_acionadas.append(
                "irrigação recente insuficiente para recuperar a água disponível"
            )

        # Regra de redução:
        # boa umidade, boa água disponível e baixo estresse reduzem criticidade
        if umidade_solo > 65 and agua_disponivel > 90 and estresse_hidrico == "baixo":
            score -= 2
            regras_acionadas.append(
                "boa condição hídrica atual"
            )

        if score < 0:
            score = 0

        evidencia = self.converter_score_para_evidencia(score)
        confianca = self.calcular_confianca(score)

        return {
            "agente": "Ahid",
            "nome_agente": "Agente Hídrico",
            "evidencia_nome": self.nome_evidencia,
            "Ehid": evidencia,
            "evidencia": evidencia,
            "criticidade": evidencia,
            "score": score,
            "confianca": confianca,
            "variaveis_modelo": self.variaveis_modelo,
            "colunas_csv": self.colunas_csv,
            "indicadores": {
                "solo": solo,
                "umidade_solo_atual": umidade_solo,
                "umidade_solo_media": round(umidade_media, 2),
                "agua_disponivel_atual": agua_disponivel,
                "agua_disponivel_media": round(agua_disponivel_media, 2),
                "irrigacao_aplicada_atual": irrigacao_aplicada,
                "irrigacao_acumulada": round(irrigacao_acumulada, 2),
                "estresse_hidrico": estresse_hidrico,
                "tendencia_umidade": tendencia_umidade,
                "tendencia_agua": tendencia_agua
            },
            "regras_acionadas": regras_acionadas,
            "motivo": "análise hídrica baseada em solo, umidade, água disponível, irrigação aplicada e estresse hídrico"
        }

    def converter_score_para_evidencia(self, score):
        """
        Converte o score hídrico em evidência Ehid.
        """

        if score <= 1:
            return "baixo"

        if score <= 3:
            return "moderado"

        if score <= 5:
            return "alto"

        return "critico"

    def calcular_confianca(self, score):
        """
        Calcula uma confiança simples para a evidência hídrica.
        """

        confianca = score / 7

        if confianca > 1:
            confianca = 1

        return round(confianca, 2)
