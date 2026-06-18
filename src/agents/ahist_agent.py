"""
Ahist Agent do Hydros.

Ahist significa Agente Histórico Contextual.

Responsabilidade no modelo Hydros:
analisar a evolução temporal completa do histórico de contexto H(Ui)
e produzir a evidência histórica Ehist.

Entrada:
H(Ui) = histórico de contexto da unidade de manejo

Saída:
Ehist em {baixo, moderado, alto, critico}
"""

from sklearn.neighbors import NearestNeighbors


class AhistAgent:
    """
    Agente histórico-contextual do modelo Hydros.
    """

    def __init__(self):
        """
        Inicializa o agente histórico-contextual.
        """

        self.tamanho_janela = 5
        self.nome_evidencia = "Ehist"

        self.variaveis_modelo = [
            "H(Ui)"
        ]

        # Colunas usadas para comparar contextos históricos semelhantes
        self.colunas_similaridade = [
            "precipitacao",
            "temperatura",
            "graus_dia",
            "evapotranspiracao",
            "coeficiente_cultura",
            "umidade_solo",
            "agua_disponivel",
            "irrigacao_aplicada",
            "produtividade"
        ]

    def analisar(self, df):
        """
        Analisa o histórico de contexto H(Ui) e gera Ehist.
        """

        # Se houver poucos registros, não há histórico suficiente
        if len(df) < 2:
            return {
                "agente": "Ahist",
                "nome_agente": "Agente Histórico Contextual",
                "evidencia_nome": self.nome_evidencia,
                "Ehist": "moderado",
                "evidencia": "moderado",
                "criticidade": "moderado",
                "score": 2,
                "confianca": 0.3,
                "variaveis_modelo": self.variaveis_modelo,
                "colunas_csv": self.colunas_similaridade,
                "indicadores": {
                    "quantidade_contextos": len(df)
                },
                "regras_acionadas": [
                    "histórico insuficiente para análise temporal robusta"
                ],
                "motivo": "histórico insuficiente para identificar tendências e similaridades"
            }

        janela = df.tail(self.tamanho_janela)
        contexto_atual = df.iloc[[-1]]
        historico_anterior = df.iloc[:-1]

        score = 0
        regras_acionadas = []

        # Indicadores de tendência temporal recente
        umidade_inicial = janela["umidade_solo"].iloc[0]
        umidade_final = janela["umidade_solo"].iloc[-1]

        agua_inicial = janela["agua_disponivel"].iloc[0]
        agua_final = janela["agua_disponivel"].iloc[-1]

        produtividade_inicial = janela["produtividade"].iloc[0]
        produtividade_final = janela["produtividade"].iloc[-1]

        et_inicial = janela["evapotranspiracao"].iloc[0]
        et_final = janela["evapotranspiracao"].iloc[-1]

        precipitacao_acumulada = janela["precipitacao"].sum()
        irrigacao_acumulada = janela["irrigacao_aplicada"].sum()

        tendencia_umidade = self.calcular_tendencia(
            umidade_inicial,
            umidade_final
        )

        tendencia_agua = self.calcular_tendencia(
            agua_inicial,
            agua_final
        )

        tendencia_produtividade = self.calcular_tendencia(
            produtividade_inicial,
            produtividade_final
        )

        tendencia_evapotranspiracao = self.calcular_tendencia(
            et_inicial,
            et_final
        )

        # Regra histórica 1:
        # queda persistente da umidade do solo
        if tendencia_umidade == "queda":
            score += 1
            regras_acionadas.append(
                "queda recente da umidade do solo"
            )

        # Regra histórica 2:
        # queda persistente da água disponível
        if tendencia_agua == "queda":
            score += 1
            regras_acionadas.append(
                "queda recente da água disponível"
            )

        # Regra histórica 3:
        # aumento da evapotranspiração na janela recente
        if tendencia_evapotranspiracao == "aumento":
            score += 1
            regras_acionadas.append(
                "aumento recente da evapotranspiração"
            )

        # Regra histórica 4:
        # ausência ou baixa precipitação acumulada
        if precipitacao_acumulada < 5:
            score += 1
            regras_acionadas.append(
                "baixa precipitação acumulada na trajetória recente"
            )

        # Regra histórica 5:
        # queda da produtividade estimada
        if tendencia_produtividade == "queda":
            score += 1
            regras_acionadas.append(
                "queda recente da produtividade estimada"
            )

        # Regra histórica 6:
        # baixa irrigação recente com perda de água disponível
        if irrigacao_acumulada == 0 and tendencia_agua == "queda":
            score += 1
            regras_acionadas.append(
                "ausência de irrigação recente associada à queda da água disponível"
            )

        # Busca contextos históricos semelhantes
        resultado_similaridade = self.buscar_contextos_similares(
            historico_anterior,
            contexto_atual
        )

        tendencia_contextos_similares = resultado_similaridade[
            "tendencia_contextos_similares"
        ]

        # Regra histórica 7:
        # contextos semelhantes indicam condição crítica ou alta
        if tendencia_contextos_similares == "critico":
            score += 2
            regras_acionadas.append(
                "contextos históricos semelhantes indicam criticidade crítica"
            )

        elif tendencia_contextos_similares == "alto":
            score += 1
            regras_acionadas.append(
                "contextos históricos semelhantes indicam criticidade alta"
            )

        elif tendencia_contextos_similares == "moderado":
            score += 1
            regras_acionadas.append(
                "contextos históricos semelhantes indicam atenção moderada"
            )

        # Regra de redução:
        # boa chuva recente, aumento de umidade e aumento de água disponível
        if (
            precipitacao_acumulada >= 20
            and tendencia_umidade == "aumento"
            and tendencia_agua == "aumento"
        ):
            score -= 2
            regras_acionadas.append(
                "trajetória recente indica recuperação hídrica"
            )

        if score < 0:
            score = 0

        evidencia = self.converter_score_para_evidencia(
            score
        )

        confianca = self.calcular_confianca(
            score,
            len(df)
        )

        return {
            "agente": "Ahist",
            "nome_agente": "Agente Histórico Contextual",
            "evidencia_nome": self.nome_evidencia,
            "Ehist": evidencia,
            "evidencia": evidencia,
            "criticidade": evidencia,
            "score": score,
            "confianca": confianca,
            "variaveis_modelo": self.variaveis_modelo,
            "colunas_csv": self.colunas_similaridade,
            "indicadores": {
                "quantidade_contextos": len(df),
                "precipitacao_acumulada": round(precipitacao_acumulada, 2),
                "irrigacao_acumulada": round(irrigacao_acumulada, 2),
                "tendencia_umidade": tendencia_umidade,
                "tendencia_agua": tendencia_agua,
                "tendencia_produtividade": tendencia_produtividade,
                "tendencia_evapotranspiracao": tendencia_evapotranspiracao,
                "contextos_similares": resultado_similaridade["contextos_similares"],
                "tendencia_contextos_similares": tendencia_contextos_similares
            },
            "regras_acionadas": regras_acionadas,
            "motivo": "análise histórica baseada na trajetória temporal e em contextos semelhantes de H(Ui)"
        }

    def buscar_contextos_similares(self, historico_anterior, contexto_atual):
        """
        Busca contextos históricos semelhantes ao contexto atual.
        """

        if len(historico_anterior) < 1:
            return {
                "contextos_similares": 0,
                "tendencia_contextos_similares": "moderado"
            }

        quantidade_vizinhos = min(
            3,
            len(historico_anterior)
        )

        x_historico = historico_anterior[self.colunas_similaridade]
        x_atual = contexto_atual[self.colunas_similaridade]

        modelo = NearestNeighbors(
            n_neighbors=quantidade_vizinhos
        )

        modelo.fit(x_historico)

        distancias, indices = modelo.kneighbors(x_atual)

        similares = historico_anterior.iloc[
            indices[0]
        ]

        if "estresse_hidrico" in similares.columns:
            tendencia = similares["estresse_hidrico"].mode()[0]
        else:
            tendencia = "moderado"

        return {
            "contextos_similares": quantidade_vizinhos,
            "tendencia_contextos_similares": tendencia
        }

    def calcular_tendencia(self, valor_inicial, valor_final):
        """
        Calcula tendência simples entre o início e o fim da janela.
        """

        if valor_final < valor_inicial:
            return "queda"

        if valor_final > valor_inicial:
            return "aumento"

        return "estavel"

    def converter_score_para_evidencia(self, score):
        """
        Converte o score histórico em evidência Ehist.
        """

        if score <= 1:
            return "baixo"

        if score <= 3:
            return "moderado"

        if score <= 5:
            return "alto"

        return "critico"

    def calcular_confianca(self, score, quantidade_contextos):
        """
        Calcula uma confiança simples para a evidência histórica.
        """

        confianca_score = score / 7

        if confianca_score > 1:
            confianca_score = 1

        # Quanto maior o histórico, maior a confiança temporal
        confianca_historico = quantidade_contextos / 20

        if confianca_historico > 1:
            confianca_historico = 1

        confianca = (
            confianca_score * 0.7
            + confianca_historico * 0.3
        )

        return round(
            confianca,
            2
        )
