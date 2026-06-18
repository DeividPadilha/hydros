"""
Ageo Agent do Hydros.

Ageo significa Agente Geográfico.

Responsabilidade no modelo Hydros:
analisar a localização da unidade de manejo
e produzir a evidência geográfica Egeo.

Variável analisada:
loc = localização geográfica da unidade de manejo

Saída:
Egeo em {baixo, moderado, alto, critico}
"""


class AgeoAgent:
    """
    Agente geográfico do modelo Hydros.
    """

    def __init__(self):
        """
        Inicializa o agente geográfico.
        """

        self.nome_evidencia = "Egeo"

        self.variaveis_modelo = [
            "loc"
        ]

        self.colunas_csv = [
            "loc"
        ]

    def analisar(self, df):
        """
        Analisa o contexto geográfico da unidade de manejo.
        """

        contexto_atual = df.iloc[-1]

        loc = str(
            contexto_atual["loc"]
        ).strip()

        score = 0
        regras_acionadas = []

        # Regra geográfica 1:
        # localização ausente reduz a qualidade contextual da análise
        if loc == "":
            score += 2
            regras_acionadas.append(
                "localização geográfica ausente"
            )

        else:
            regras_acionadas.append(
                "localização geográfica informada"
            )

        # Regra geográfica 2:
        # nesta versão inicial, a localização é usada para rastreabilidade
        # e contextualização da unidade de manejo
        if "MT" in loc or "MATO_GROSSO" in loc.upper():
            score += 1
            regras_acionadas.append(
                "unidade localizada em região agrícola de Mato Grosso"
            )

        evidencia = self.converter_score_para_evidencia(
            score
        )

        confianca = self.calcular_confianca(
            score,
            loc
        )

        return {
            "agente": "Ageo",
            "nome_agente": "Agente Geográfico",
            "evidencia_nome": self.nome_evidencia,
            "Egeo": evidencia,
            "evidencia": evidencia,
            "criticidade": evidencia,
            "score": score,
            "confianca": confianca,
            "variaveis_modelo": self.variaveis_modelo,
            "colunas_csv": self.colunas_csv,
            "indicadores": {
                "loc": loc
            },
            "regras_acionadas": regras_acionadas,
            "motivo": "análise geográfica baseada na localização da unidade de manejo"
        }

    def converter_score_para_evidencia(self, score):
        """
        Converte o score geográfico em evidência Egeo.
        """

        if score == 0:
            return "baixo"

        if score == 1:
            return "moderado"

        if score == 2:
            return "alto"

        return "critico"

    def calcular_confianca(self, score, loc):
        """
        Calcula uma confiança simples para a evidência geográfica.
        """

        if loc == "":
            return 0.2

        if score == 0:
            return 0.6

        return 0.5
