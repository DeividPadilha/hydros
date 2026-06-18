class AMDHAgent:
    """
    AMDH: Agente Motor de Decisão Híbrida.

    Responsabilidade:
    combinar as evidências geradas pelos agentes AGR, AHC e ACL
    para produzir a decisão final de manejo hídrico.
    """

    def __init__(self):
        # Pesos dos agentes no cálculo híbrido
        # Esses pesos podem ser alterados depois conforme o artigo evoluir
        self.pesos = {
            "acl": 0.4,
            "agr": 0.3,
            "ahc": 0.3
        }

        # Conversão das evidências textuais para valores numéricos
        self.mapa_criticidade = {
            "baixo": 1,
            "moderado": 2,
            "medio": 2,
            "alto": 3,
            "critico": 4
        }

    def decidir(self, resultado_agr, resultado_ahc, resultado_acl):
        """
        Combina AGR, AHC e ACL usando score ponderado.
        """

        # Extrai a evidência do AGR
        evidencia_agr = resultado_agr.get("evidencia", resultado_agr.get("criticidade", "moderado"))

        # Extrai a evidência do AHC
        evidencia_ahc = resultado_ahc.get("evidencia", resultado_ahc.get("tendencia", "moderado"))

        # Extrai a evidência do ACL
        evidencia_acl = resultado_acl.get("evidencia", resultado_acl.get("risco_previsto", "moderado"))

        # Converte evidências textuais para valores numéricos
        valor_agr = self.mapa_criticidade.get(evidencia_agr, 2)
        valor_ahc = self.mapa_criticidade.get(evidencia_ahc, 2)
        valor_acl = self.mapa_criticidade.get(evidencia_acl, 2)

        # Calcula score híbrido ponderado
        score = (
            self.pesos["agr"] * valor_agr +
            self.pesos["ahc"] * valor_ahc +
            self.pesos["acl"] * valor_acl
        )

        # Converte score em decisão final
        decisao_final = self.converter_score_para_decisao(score)

        # Confiança simples baseada na intensidade do score
        confianca = round(score / 4, 2)

        # Gera explicação textual
        explicacao = self.gerar_explicacao(
            score,
            decisao_final,
            evidencia_agr,
            evidencia_ahc,
            evidencia_acl,
            resultado_agr,
            resultado_ahc,
            resultado_acl
        )

        return {
            "agente": "AMDH",
            "decisao_final": decisao_final,
            "score_hibrido": round(score, 2),
            "confianca": confianca,
            "evidencias": {
                "AGR": evidencia_agr,
                "AHC": evidencia_ahc,
                "ACL": evidencia_acl
            },
            "pesos": self.pesos,
            "explicacao": explicacao
        }

    def converter_score_para_decisao(self, score):
        """
        Converte o score híbrido em decisão de irrigação.
        """

        if score < 1.5:
            return "finalizar_irrigacao"

        if score < 2.3:
            return "reduzir_irrigacao"

        if score < 3.0:
            return "manter_irrigacao"

        if score < 3.5:
            return "iniciar_irrigacao"

        return "aumentar_irrigacao"

    def gerar_explicacao(
        self,
        score,
        decisao_final,
        evidencia_agr,
        evidencia_ahc,
        evidencia_acl,
        resultado_agr,
        resultado_ahc,
        resultado_acl
    ):
        """
        Gera explicação da decisão final.
        """

        return (
            f"A decisão final foi {decisao_final}. "
            f"O score híbrido calculado foi {round(score, 2)}. "
            f"O AGR gerou evidência {evidencia_agr}, "
            f"o AHC gerou evidência {evidencia_ahc} "
            f"e o ACL gerou evidência {evidencia_acl}. "
            f"O resultado foi obtido pela combinação ponderada das evidências dos agentes."
        )