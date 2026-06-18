class AGRAgent:
    """
    AGR: Agente de Regras Agronômicas.

    Responsabilidade:
    analisar uma janela recente do histórico de contexto
    e gerar uma evidência agronômica padronizada.

    Saída:
    baixo, moderado, alto ou critico.
    """

    def __init__(self):
        # Quantidade de registros recentes usados na análise
        self.tamanho_janela = 5

    def avaliar(self, df):
        """
        Avalia o histórico recente do talhão usando regras agronômicas.
        """

        # Seleciona os últimos registros do histórico
        janela = df.tail(self.tamanho_janela)

        # Pega o contexto mais recente
        contexto_atual = janela.iloc[-1]

        # Variáveis atuais
        precipitacao = contexto_atual["precipitacao"]
        evapotranspiracao = contexto_atual["evapotranspiracao"]
        umidade_solo = contexto_atual["umidade_solo"]
        agua_disponivel = contexto_atual["agua_disponivel"]
        irrigacao_aplicada = contexto_atual["irrigacao_aplicada"]
        estagio_fenologico = contexto_atual["estagio_fenologico"]

        # Variáveis calculadas da janela recente
        precipitacao_recente = janela["precipitacao"].sum()
        irrigacao_recente = janela["irrigacao_aplicada"].sum()
        media_umidade = janela["umidade_solo"].mean()
        media_evapotranspiracao = janela["evapotranspiracao"].mean()

        # Score agronômico inicial
        score = 0

        # Lista de regras acionadas
        regras_acionadas = []

        # Regra 1: umidade do solo muito baixa
        if umidade_solo < 30:
            score += 3
            regras_acionadas.append("umidade do solo muito baixa")

        # Regra 2: água disponível muito baixa
        if agua_disponivel < 45:
            score += 3
            regras_acionadas.append("água disponível muito baixa")

        # Regra 3: evapotranspiração elevada
        if evapotranspiracao > 6:
            score += 2
            regras_acionadas.append("evapotranspiração elevada")

        # Regra 4: pouca precipitação recente
        if precipitacao_recente < 5:
            score += 2
            regras_acionadas.append("baixa precipitação recente")

        # Regra 5: fase fenológica sensível com baixa água disponível
        if estagio_fenologico in ["R3", "R4", "R5"] and agua_disponivel < 65:
            score += 2
            regras_acionadas.append("fase fenológica sensível com baixa água disponível")

        # Regra 6: irrigação recente, mas umidade ainda baixa
        if irrigacao_recente > 20 and media_umidade < 40:
            score += 1
            regras_acionadas.append("irrigação recente insuficiente para recuperar a umidade")

        # Regra 7: boa precipitação, boa umidade e boa água disponível
        if precipitacao_recente >= 20 and umidade_solo > 55 and agua_disponivel > 85:
            score -= 2
            regras_acionadas.append("boa condição hídrica recente")

        # Regra 8: umidade média adequada e evapotranspiração moderada
        if media_umidade > 60 and media_evapotranspiracao < 5:
            score -= 1
            regras_acionadas.append("umidade média adequada na janela recente")

        # Impede score negativo
        if score < 0:
            score = 0

        # Classificação da criticidade agronômica
        if score == 0:
            criticidade = "baixo"
            recomendacao = "reduzir_irrigacao"
            prioridade = "baixa"

        elif score <= 2:
            criticidade = "moderado"
            recomendacao = "manter_irrigacao"
            prioridade = "media"

        elif score <= 4:
            criticidade = "alto"
            recomendacao = "iniciar_irrigacao"
            prioridade = "alta"

        else:
            criticidade = "critico"
            recomendacao = "aumentar_irrigacao"
            prioridade = "critica"

        # Confiança simples baseada na força das regras acionadas
        confianca = min(round(score / 6, 2), 1.0)

        return {
            "agente": "AGR",
            "criticidade": criticidade,
            "evidencia": criticidade,
            "score_agronomico": score,
            "confianca": confianca,
            "recomendacao": recomendacao,
            "decisao": recomendacao,
            "prioridade": prioridade,
            "regras_acionadas": regras_acionadas,
            "motivo": "análise baseada em regras agronômicas aplicadas à janela recente do histórico de contexto"
        }