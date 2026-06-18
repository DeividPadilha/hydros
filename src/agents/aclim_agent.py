"""
Aclim Agent do Hydros.

Aclim significa Agente Climático.

Responsabilidade no modelo Hydros:
analisar as variáveis climáticas do histórico de contexto
e produzir a evidência climática Eclim.

Variáveis analisadas:
p    = precipitação
temp = temperatura média
gd   = soma térmica
et   = evapotranspiração

Saída:
Eclim em {baixo, moderado, alto, critico}
"""


class AclimAgent:
    """
    Agente climático do modelo Hydros.
    """

    def __init__(self):
        """
        Inicializa o agente climático.
        """

        self.tamanho_janela = 5
        self.nome_evidencia = "Eclim"

        self.variaveis_modelo = [
            "p",
            "temp",
            "gd",
            "et"
        ]

        self.colunas_csv = [
            "precipitacao",
            "temperatura",
            "graus_dia",
            "evapotranspiracao"
        ]

    def analisar(self, df):
        """
        Analisa o histórico de contexto e gera a evidência climática Eclim.
        """

        janela = df.tail(self.tamanho_janela)
        contexto_atual = janela.iloc[-1]

        precipitacao_atual = contexto_atual["precipitacao"]
        temperatura_atual = contexto_atual["temperatura"]
        graus_dia_atual = contexto_atual["graus_dia"]
        evapotranspiracao_atual = contexto_atual["evapotranspiracao"]

        precipitacao_acumulada = janela["precipitacao"].sum()
        evapotranspiracao_acumulada = janela["evapotranspiracao"].sum()
        temperatura_media = janela["temperatura"].mean()
        graus_dia_medio = janela["graus_dia"].mean()

        primeira_et = janela["evapotranspiracao"].iloc[0]
        ultima_et = janela["evapotranspiracao"].iloc[-1]

        if ultima_et > primeira_et:
            tendencia_evapotranspiracao = "aumento"
        elif ultima_et < primeira_et:
            tendencia_evapotranspiracao = "queda"
        else:
            tendencia_evapotranspiracao = "estavel"

        score = 0
        regras_acionadas = []

        if precipitacao_acumulada < 5:
            score += 2
            regras_acionadas.append(
                "baixa precipitação acumulada na janela recente"
            )

        elif precipitacao_acumulada < 15:
            score += 1
            regras_acionadas.append(
                "precipitação acumulada moderada na janela recente"
            )

        if evapotranspiracao_atual >= 6.5:
            score += 2
            regras_acionadas.append(
                "evapotranspiração atual elevada"
            )

        elif evapotranspiracao_atual >= 5.5:
            score += 1
            regras_acionadas.append(
                "evapotranspiração atual moderadamente elevada"
            )

        if temperatura_atual >= 36:
            score += 1
            regras_acionadas.append(
                "temperatura atual elevada"
            )

        if graus_dia_atual >= 27:
            score += 1
            regras_acionadas.append(
                "soma térmica atual elevada"
            )

        if tendencia_evapotranspiracao == "aumento":
            score += 1
            regras_acionadas.append(
                "tendência de aumento da evapotranspiração"
            )

        if precipitacao_acumulada >= 25:
            score -= 2
            regras_acionadas.append(
                "precipitação acumulada suficiente na janela recente"
            )

        if score < 0:
            score = 0

        evidencia = self.converter_score_para_evidencia(score)
        confianca = self.calcular_confianca(score)

        return {
            "agente": "Aclim",
            "nome_agente": "Agente Climático",
            "evidencia_nome": self.nome_evidencia,
            "Eclim": evidencia,
            "evidencia": evidencia,
            "criticidade": evidencia,
            "score": score,
            "confianca": confianca,
            "variaveis_modelo": self.variaveis_modelo,
            "colunas_csv": self.colunas_csv,
            "indicadores": {
                "precipitacao_atual": precipitacao_atual,
                "precipitacao_acumulada": round(precipitacao_acumulada, 2),
                "temperatura_atual": temperatura_atual,
                "temperatura_media": round(temperatura_media, 2),
                "graus_dia_atual": graus_dia_atual,
                "graus_dia_medio": round(graus_dia_medio, 2),
                "evapotranspiracao_atual": evapotranspiracao_atual,
                "evapotranspiracao_acumulada": round(evapotranspiracao_acumulada, 2),
                "tendencia_evapotranspiracao": tendencia_evapotranspiracao
            },
            "regras_acionadas": regras_acionadas,
            "motivo": "análise climática baseada em precipitação, temperatura, soma térmica e evapotranspiração"
        }

    def converter_score_para_evidencia(self, score):
        """
        Converte o score climático em evidência Eclim.
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
        Calcula uma confiança simples para a evidência climática.
        """

        confianca = score / 6

        if confianca > 1:
            confianca = 1

        return round(confianca, 2)
