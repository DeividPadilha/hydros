from sklearn.neighbors import NearestNeighbors


class AHCAgent:
    """
    AHC: Agente de Histórico de Contexto.

    Responsabilidade:
    analisar o histórico do talhão, buscar contextos semelhantes
    e gerar uma evidência histórica padronizada.
    """

    def __init__(self):
        # Variáveis usadas para comparar contextos históricos semelhantes
        self.colunas_analise = [
            "temperatura",
            "precipitacao",
            "umidade_solo",
            "evapotranspiracao",
            "agua_disponivel"
        ]

    def analisar(self, df):
        """
        Analisa o histórico de contexto do talhão.
        """

        # Se houver poucos registros, não há histórico suficiente
        if len(df) < 2:
            return {
                "agente": "AHC",
                "criticidade": "moderado",
                "evidencia": "moderado",
                "contextos_similares": 0,
                "recomendacao": "manter_irrigacao",
                "motivo": "histórico insuficiente para análise contextual"
            }

        # Separa histórico anterior e contexto atual
        historico = df.iloc[:-1]
        contexto_atual = df.iloc[-1:]

        # Seleciona variáveis usadas na comparação
        x_historico = historico[self.colunas_analise]
        x_atual = contexto_atual[self.colunas_analise]

        # Define quantidade de contextos semelhantes
        quantidade_vizinhos = min(3, len(historico))

        # Modelo de vizinhança para buscar contextos semelhantes
        modelo = NearestNeighbors(
            n_neighbors=quantidade_vizinhos
        )

        modelo.fit(x_historico)

        # Busca contextos mais próximos do contexto atual
        distancias, indices = modelo.kneighbors(x_atual)

        # Recupera os registros históricos semelhantes
        similares = historico.iloc[indices[0]]

        # Verifica o estresse hídrico mais comum nos contextos semelhantes
        if "estresse_hidrico" in similares.columns:
            tendencia = similares["estresse_hidrico"].mode()[0]
        else:
            tendencia = "moderado"

        # Analisa tendência recente da umidade e da água disponível
        janela_recente = df.tail(5)

        umidade_inicial = janela_recente["umidade_solo"].iloc[0]
        umidade_final = janela_recente["umidade_solo"].iloc[-1]

        agua_inicial = janela_recente["agua_disponivel"].iloc[0]
        agua_final = janela_recente["agua_disponivel"].iloc[-1]

        tendencia_umidade = "queda" if umidade_final < umidade_inicial else "estavel_ou_alta"
        tendencia_agua = "queda" if agua_final < agua_inicial else "estavel_ou_alta"

        # Score histórico simples
        score = 0

        if tendencia in ["alto", "critico"]:
            score += 2

        if tendencia_umidade == "queda":
            score += 1

        if tendencia_agua == "queda":
            score += 1

        # Classificação da criticidade histórica
        if score == 0:
            criticidade = "baixo"
            recomendacao = "reduzir_irrigacao"

        elif score == 1:
            criticidade = "moderado"
            recomendacao = "manter_irrigacao"

        elif score == 2:
            criticidade = "alto"
            recomendacao = "iniciar_irrigacao"

        else:
            criticidade = "critico"
            recomendacao = "aumentar_irrigacao"

        return {
            "agente": "AHC",
            "criticidade": criticidade,
            "evidencia": criticidade,
            "contextos_similares": quantidade_vizinhos,
            "tendencia_contextos": tendencia,
            "tendencia_umidade": tendencia_umidade,
            "tendencia_agua_disponivel": tendencia_agua,
            "score_historico": score,
            "recomendacao": recomendacao,
            "motivo": "análise baseada em contextos históricos semelhantes e tendência recente do talhão"
        }