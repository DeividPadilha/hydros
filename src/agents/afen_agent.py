"""
Afen Agent do Hydros.

Afen significa Agente Fenológico.

Responsabilidade no modelo Hydros:
analisar as variáveis fenológicas do histórico de contexto
e produzir a evidência fenológica Efen.

Variáveis analisadas:
ef = estágio fenológico
kc = coeficiente de cultura
gd = soma térmica

Saída:
Efen em {baixo, moderado, alto, critico}
"""


class AfenAgent:
    """
    Agente fenológico do modelo Hydros.
    """

    def __init__(self):
        """
        Inicializa o agente fenológico.
        """

        self.tamanho_janela = 5
        self.nome_evidencia = "Efen"

        self.variaveis_modelo = [
            "ef",
            "kc",
            "gd"
        ]

        self.colunas_csv = [
            "estagio_fenologico",
            "coeficiente_cultura",
            "graus_dia"
        ]

    def analisar(self, df):
        """
        Analisa o histórico de contexto e gera a evidência fenológica Efen.
        """

        janela = df.tail(self.tamanho_janela)
        contexto_atual = janela.iloc[-1]

        estagio_fenologico = str(
            contexto_atual["estagio_fenologico"]
        ).upper()

        coeficiente_cultura = contexto_atual["coeficiente_cultura"]
        graus_dia_atual = contexto_atual["graus_dia"]

        kc_medio = janela["coeficiente_cultura"].mean()
        graus_dia_medio = janela["graus_dia"].mean()

        primeiro_kc = janela["coeficiente_cultura"].iloc[0]
        ultimo_kc = janela["coeficiente_cultura"].iloc[-1]

        primeiro_gd = janela["graus_dia"].iloc[0]
        ultimo_gd = janela["graus_dia"].iloc[-1]

        if ultimo_kc > primeiro_kc:
            tendencia_kc = "aumento"
        elif ultimo_kc < primeiro_kc:
            tendencia_kc = "queda"
        else:
            tendencia_kc = "estavel"

        if ultimo_gd > primeiro_gd:
            tendencia_graus_dia = "aumento"
        elif ultimo_gd < primeiro_gd:
            tendencia_graus_dia = "queda"
        else:
            tendencia_graus_dia = "estavel"

        score = 0
        regras_acionadas = []

        # Regra fenológica 1:
        # fases reprodutivas tendem a ser mais sensíveis ao déficit hídrico
        if estagio_fenologico in ["R1", "R2"]:
            score += 1
            regras_acionadas.append(
                "fase reprodutiva inicial com maior atenção hídrica"
            )

        elif estagio_fenologico in ["R3", "R4", "R5"]:
            score += 2
            regras_acionadas.append(
                "fase reprodutiva sensível ao déficit hídrico"
            )

        # Regra fenológica 2:
        # fases vegetativas avançadas também exigem atenção
        if estagio_fenologico in ["V4", "V5", "V6"]:
            score += 1
            regras_acionadas.append(
                "fase vegetativa avançada com demanda crescente"
            )

        # Regra fenológica 3:
        # Kc elevado indica maior demanda hídrica da cultura
        if coeficiente_cultura >= 1.05:
            score += 2
            regras_acionadas.append(
                "coeficiente de cultura elevado"
            )

        elif coeficiente_cultura >= 0.85:
            score += 1
            regras_acionadas.append(
                "coeficiente de cultura moderadamente elevado"
            )

        # Regra fenológica 4:
        # soma térmica elevada indica avanço no desenvolvimento da cultura
        if graus_dia_atual >= 27:
            score += 1
            regras_acionadas.append(
                "soma térmica atual elevada"
            )

        # Regra fenológica 5:
        # aumento do Kc indica crescimento da demanda hídrica
        if tendencia_kc == "aumento":
            score += 1
            regras_acionadas.append(
                "tendência de aumento do coeficiente de cultura"
            )

        # Regra fenológica 6:
        # aumento da soma térmica indica avanço fenológico recente
        if tendencia_graus_dia == "aumento":
            score += 1
            regras_acionadas.append(
                "tendência de aumento da soma térmica"
            )

        # Regra de redução:
        # fase inicial e Kc baixo indicam menor demanda fenológica
        if estagio_fenologico in ["V1", "V2", "V3"] and coeficiente_cultura < 0.80:
            score -= 1
            regras_acionadas.append(
                "fase inicial com baixo coeficiente de cultura"
            )

        if score < 0:
            score = 0

        evidencia = self.converter_score_para_evidencia(score)
        confianca = self.calcular_confianca(score)

        return {
            "agente": "Afen",
            "nome_agente": "Agente Fenológico",
            "evidencia_nome": self.nome_evidencia,
            "Efen": evidencia,
            "evidencia": evidencia,
            "criticidade": evidencia,
            "score": score,
            "confianca": confianca,
            "variaveis_modelo": self.variaveis_modelo,
            "colunas_csv": self.colunas_csv,
            "indicadores": {
                "estagio_fenologico": estagio_fenologico,
                "coeficiente_cultura_atual": coeficiente_cultura,
                "coeficiente_cultura_medio": round(kc_medio, 2),
                "graus_dia_atual": graus_dia_atual,
                "graus_dia_medio": round(graus_dia_medio, 2),
                "tendencia_kc": tendencia_kc,
                "tendencia_graus_dia": tendencia_graus_dia
            },
            "regras_acionadas": regras_acionadas,
            "motivo": "análise fenológica baseada em estágio fenológico, coeficiente de cultura e soma térmica"
        }

    def converter_score_para_evidencia(self, score):
        """
        Converte o score fenológico em evidência Efen.
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
        Calcula uma confiança simples para a evidência fenológica.
        """

        confianca = score / 6

        if confianca > 1:
            confianca = 1

        return round(confianca, 2)
