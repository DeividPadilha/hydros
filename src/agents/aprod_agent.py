"""
Aprod Agent do Hydros.

Aprod significa Agente Produtivo.

Responsabilidade no modelo Hydros:
analisar a produtividade estimada da unidade de manejo
e produzir a evidência produtiva Eprod.

Variável analisada:
prod = produtividade estimada

Saída:
Eprod em {baixo, moderado, alto, critico}
"""


class AprodAgent:
    """
    Agente produtivo do modelo Hydros.
    """

    def __init__(self):
        """
        Inicializa o agente produtivo.
        """

        self.tamanho_janela = 5
        self.nome_evidencia = "Eprod"

        self.variaveis_modelo = [
            "prod"
        ]

        self.colunas_csv = [
            "produtividade"
        ]

    def analisar(self, df):
        """
        Analisa a produtividade estimada e gera a evidência produtiva Eprod.
        """

        janela = df.tail(self.tamanho_janela)
        contexto_atual = janela.iloc[-1]

        produtividade_atual = contexto_atual["produtividade"]
        produtividade_media = janela["produtividade"].mean()

        produtividade_inicial = janela["produtividade"].iloc[0]
        produtividade_final = janela["produtividade"].iloc[-1]

        variacao_produtividade = produtividade_final - produtividade_inicial

        if variacao_produtividade < 0:
            tendencia_produtividade = "queda"
        elif variacao_produtividade > 0:
            tendencia_produtividade = "aumento"
        else:
            tendencia_produtividade = "estavel"

        score = 0
        regras_acionadas = []

        # Regra produtiva 1:
        # queda leve de produtividade estimada indica atenção
        if variacao_produtividade < -200:
            score += 1
            regras_acionadas.append(
                "queda moderada da produtividade estimada"
            )

        # Regra produtiva 2:
        # queda forte de produtividade estimada indica alta criticidade
        if variacao_produtividade < -400:
            score += 2
            regras_acionadas.append(
                "queda forte da produtividade estimada"
            )

        # Regra produtiva 3:
        # produtividade atual abaixo da média recente indica possível impacto
        if produtividade_atual < produtividade_media:
            score += 1
            regras_acionadas.append(
                "produtividade atual abaixo da média recente"
            )

        # Regra produtiva 4:
        # tendência de aumento reduz a criticidade produtiva
        if tendencia_produtividade == "aumento":
            score -= 1
            regras_acionadas.append(
                "tendência de aumento da produtividade estimada"
            )

        if score < 0:
            score = 0

        evidencia = self.converter_score_para_evidencia(
            score
        )

        confianca = self.calcular_confianca(
            score
        )

        return {
            "agente": "Aprod",
            "nome_agente": "Agente Produtivo",
            "evidencia_nome": self.nome_evidencia,
            "Eprod": evidencia,
            "evidencia": evidencia,
            "criticidade": evidencia,
            "score": score,
            "confianca": confianca,
            "variaveis_modelo": self.variaveis_modelo,
            "colunas_csv": self.colunas_csv,
            "indicadores": {
                "produtividade_atual": produtividade_atual,
                "produtividade_media": round(produtividade_media, 2),
                "produtividade_inicial": produtividade_inicial,
                "produtividade_final": produtividade_final,
                "variacao_produtividade": variacao_produtividade,
                "tendencia_produtividade": tendencia_produtividade
            },
            "regras_acionadas": regras_acionadas,
            "motivo": "análise produtiva baseada na produtividade estimada e sua tendência recente"
        }

    def converter_score_para_evidencia(self, score):
        """
        Converte o score produtivo em evidência Eprod.
        """

        if score <= 0:
            return "baixo"

        if score == 1:
            return "moderado"

        if score <= 3:
            return "alto"

        return "critico"

    def calcular_confianca(self, score):
        """
        Calcula uma confiança simples para a evidência produtiva.
        """

        confianca = score / 4

        if confianca > 1:
            confianca = 1

        return round(confianca, 2)
