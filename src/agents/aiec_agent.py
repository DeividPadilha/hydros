"""
AIEC Agent do Hydros.

AIEC significa Agente Integrador de Evidências Contextuais.

Responsabilidade no modelo Hydros:
integrar as evidências produzidas pelos agentes especializados
do histórico de contexto e produzir a evidência contextual consolidada Ehc.

Entradas:
Eclim = evidência climática
Ehid  = evidência hídrica
Efen  = evidência fenológica
Egeo  = evidência geográfica
Eprod = evidência produtiva
Ehist = evidência histórico-contextual

Saída:
Ehc em {baixo, moderado, alto, critico}
"""


class AIECAgent:
    """
    Agente Integrador de Evidências Contextuais do modelo Hydros.
    """

    def __init__(self):
        """
        Inicializa o AIEC com pesos para integração contextual.
        """

        self.nome_evidencia = "Ehc"

        # Pesos das evidências contextuais
        # A soma dos pesos deve ser igual a 1
        self.pesos = {
            "Eclim": 0.20,
            "Ehid": 0.25,
            "Efen": 0.15,
            "Egeo": 0.10,
            "Eprod": 0.10,
            "Ehist": 0.20
        }

        # Função V do modelo
        # Converte criticidade textual em valor numérico
        self.mapa_criticidade = {
            "baixo": 1,
            "moderado": 2,
            "medio": 2,
            "alto": 3,
            "critico": 4
        }

    def integrar(
        self,
        resultado_aclim,
        resultado_ahid,
        resultado_afen,
        resultado_ageo,
        resultado_aprod,
        resultado_ahist
    ):
        """
        Integra Eclim, Ehid, Efen, Egeo, Eprod e Ehist para gerar Ehc.
        """

        # Extrai as evidências produzidas por cada agente especializado
        eclim = self.extrair_evidencia(
            resultado_aclim,
            "Eclim"
        )

        ehid = self.extrair_evidencia(
            resultado_ahid,
            "Ehid"
        )

        efen = self.extrair_evidencia(
            resultado_afen,
            "Efen"
        )

        egeo = self.extrair_evidencia(
            resultado_ageo,
            "Egeo"
        )

        eprod = self.extrair_evidencia(
            resultado_aprod,
            "Eprod"
        )

        ehist = self.extrair_evidencia(
            resultado_ahist,
            "Ehist"
        )

        evidencias = {
            "Eclim": eclim,
            "Ehid": ehid,
            "Efen": efen,
            "Egeo": egeo,
            "Eprod": eprod,
            "Ehist": ehist
        }

        # Calcula o score contextual consolidado
        score_contextual = self.calcular_score_contextual(
            evidencias
        )

        # Converte o score em Ehc
        ehc = self.converter_score_para_evidencia(
            score_contextual
        )

        # Calcula a confiança consolidada
        confianca = self.calcular_confianca_contextual(
            resultado_aclim,
            resultado_ahid,
            resultado_afen,
            resultado_ageo,
            resultado_aprod,
            resultado_ahist
        )

        explicacao = self.gerar_explicacao(
            ehc,
            score_contextual,
            evidencias
        )

        return {
            "agente": "AIEC",
            "nome_agente": "Agente Integrador de Evidências Contextuais",
            "evidencia_nome": self.nome_evidencia,
            "Ehc": ehc,
            "evidencia": ehc,
            "criticidade": ehc,
            "score": round(score_contextual, 2),
            "score_contextual": round(score_contextual, 2),
            "confianca": confianca,
            "pesos": self.pesos,
            "evidencias_contextuais": evidencias,
            "explicacao": explicacao,
            "motivo": "integração ponderada das evidências dos agentes especializados do histórico de contexto"
        }

    def extrair_evidencia(self, resultado_agente, nome_evidencia):
        """
        Extrai a evidência de um agente especializado.
        """

        return resultado_agente.get(
            nome_evidencia,
            resultado_agente.get(
                "evidencia",
                resultado_agente.get(
                    "criticidade",
                    "moderado"
                )
            )
        )

    def calcular_score_contextual(self, evidencias):
        """
        Calcula o score contextual consolidado.

        ScoreEhc =
        wclim * V(Eclim) +
        whid  * V(Ehid)  +
        wfen  * V(Efen)  +
        wgeo  * V(Egeo)  +
        wprod * V(Eprod) +
        whist * V(Ehist)
        """

        score = 0

        for nome_evidencia, criticidade in evidencias.items():
            valor = self.mapa_criticidade.get(
                criticidade,
                2
            )

            peso = self.pesos.get(
                nome_evidencia,
                0
            )

            score += peso * valor

        return score

    def converter_score_para_evidencia(self, score):
        """
        Converte o score contextual em evidência Ehc.
        """

        if score < 1.5:
            return "baixo"

        if score < 2.5:
            return "moderado"

        if score < 3.3:
            return "alto"

        return "critico"

    def calcular_confianca_contextual(
        self,
        resultado_aclim,
        resultado_ahid,
        resultado_afen,
        resultado_ageo,
        resultado_aprod,
        resultado_ahist
    ):
        """
        Calcula a confiança contextual consolidada
        usando a confiança ponderada dos agentes especializados.
        """

        confiancas = {
            "Eclim": resultado_aclim.get("confianca", 0.5),
            "Ehid": resultado_ahid.get("confianca", 0.5),
            "Efen": resultado_afen.get("confianca", 0.5),
            "Egeo": resultado_ageo.get("confianca", 0.5),
            "Eprod": resultado_aprod.get("confianca", 0.5),
            "Ehist": resultado_ahist.get("confianca", 0.5)
        }

        confianca = 0

        for nome_evidencia, valor_confianca in confiancas.items():
            peso = self.pesos.get(
                nome_evidencia,
                0
            )

            confianca += peso * valor_confianca

        return round(
            confianca,
            2
        )

    def gerar_explicacao(self, ehc, score_contextual, evidencias):
        """
        Gera explicação textual da evidência contextual consolidada.
        """

        return (
            f"A evidência contextual consolidada Ehc foi classificada como {ehc}. "
            f"O score contextual calculado foi {round(score_contextual, 2)}. "
            f"As evidências consideradas foram: "
            f"Eclim={evidencias['Eclim']}, "
            f"Ehid={evidencias['Ehid']}, "
            f"Efen={evidencias['Efen']}, "
            f"Egeo={evidencias['Egeo']}, "
            f"Eprod={evidencias['Eprod']} e "
            f"Ehist={evidencias['Ehist']}."
        )
