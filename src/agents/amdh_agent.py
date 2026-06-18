"""
AMDH Agent do Hydros.

AMDH significa Agente Motor de Decisão Híbrido.

Responsabilidade no modelo Hydros:
integrar a evidência contextual consolidada Ehc,
a evidência agronômica Earg
e a evidência preditiva supervisionada Eaps
para gerar a decisão final D(Ui).

Entrada:
Ehc  = evidência contextual consolidada
Earg = evidência agronômica
Eaps = evidência preditiva supervisionada

Saída:
D(Ui) em {
    iniciar_irrigacao,
    manter_irrigacao,
    aumentar_irrigacao,
    reduzir_irrigacao,
    finalizar_irrigacao
}
"""


from src.config.hydros_terms import FUNCAO_V, PESOS_AMDH, LIMIARES_AMDH


class AMDHAgent:
    """
    Agente Motor de Decisão Híbrido do modelo Hydros.
    """

    def __init__(self):
        """
        Inicializa o AMDH com pesos e limiares de decisão.
        """

        # Pesos do motor híbrido definidos no arquivo oficial de termos
        self.pesos = PESOS_AMDH

        # Função V definida no arquivo oficial de termos
        self.mapa_criticidade = FUNCAO_V

        # Limiares definidos no arquivo oficial de termos
        self.limiares = LIMIARES_AMDH

    def decidir(
        self,
        resultado_arg,
        resultado_aiec,
        resultado_aps,
        contexto_atual=None
    ):
        """
        Integra Ehc, Earg e Eaps para gerar D(Ui).
        """

        # Extrai Ehc do AIEC
        ehc = self.extrair_evidencia(
            resultado_aiec,
            "Ehc"
        )

        # Extrai Earg do ARG
        earg = self.extrair_evidencia(
            resultado_arg,
            "Earg"
        )

        # Extrai Eaps do APS
        eaps = self.extrair_evidencia(
            resultado_aps,
            "Eaps"
        )

        # Calcula score híbrido
        score = self.calcular_score_hibrido(
            ehc,
            earg,
            eaps
        )

        # Identifica se há irrigação ativa no contexto atual
        irrigacao_ativa = self.verificar_irrigacao_ativa(
            contexto_atual
        )

        # Converte score em decisão final
        decisao_final = self.converter_score_para_decisao(
            score,
            irrigacao_ativa
        )

        # Ajuste operacional baseado nas evidências
        decisao_final = self.aplicar_ajuste_operacional(
            decisao_final,
            score,
            ehc,
            earg,
            eaps,
            irrigacao_ativa
        )

        # Calcula confiança híbrida
        confianca = self.calcular_confianca(
            score,
            resultado_aiec,
            resultado_arg,
            resultado_aps
        )

        # Gera explicação da decisão
        explicacao = self.gerar_explicacao(
            decisao_final,
            score,
            ehc,
            earg,
            eaps,
            irrigacao_ativa
        )

        return {
            "agente": "AMDH",
            "nome_agente": "Agente Motor de Decisão Híbrido",
            "D(Ui)": decisao_final,
            "decisao_final": decisao_final,
            "score": round(score, 2),
            "score_hibrido": round(score, 2),
            "confianca": confianca,
            "evidencias": {
                "Ehc": ehc,
                "Earg": earg,
                "Eaps": eaps
            },
            "pesos": self.pesos,
            "limiares": self.limiares,
            "irrigacao_ativa": irrigacao_ativa,
            "explicacao": explicacao,
            "motivo": "integração híbrida entre evidência contextual, evidência agronômica e evidência preditiva supervisionada"
        }

    def extrair_evidencia(self, resultado_agente, nome_evidencia):
        """
        Extrai uma evidência padronizada de um resultado de agente.
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

    def calcular_score_hibrido(self, ehc, earg, eaps):
        """
        Calcula o score híbrido do AMDH.

        Score =
        whc  * V(Ehc) +
        warg * V(Earg) +
        waps * V(Eaps)
        """

        valor_ehc = self.mapa_criticidade.get(
            ehc,
            2
        )

        valor_earg = self.mapa_criticidade.get(
            earg,
            2
        )

        valor_eaps = self.mapa_criticidade.get(
            eaps,
            2
        )

        score = (
            self.pesos["whc"] * valor_ehc
            + self.pesos["warg"] * valor_earg
            + self.pesos["waps"] * valor_eaps
        )

        return score

    def verificar_irrigacao_ativa(self, contexto_atual):
        """
        Verifica se existe irrigação ativa no contexto atual.

        Se o contexto atual não for informado, retorna None.
        """

        if contexto_atual is None:
            return None

        irrigacao_aplicada = contexto_atual.get(
            "irrigacao_aplicada",
            0
        )

        return irrigacao_aplicada > 0

    def converter_score_para_decisao(self, score, irrigacao_ativa=None):
        """
        Converte o score híbrido em decisão final de manejo hídrico.
        """

        alpha = self.limiares["alpha"]
        beta = self.limiares["beta"]
        gamma = self.limiares["gamma"]
        delta = self.limiares["delta"]

        # Caso não exista informação operacional da irrigação,
        # usa apenas os limiares formais do modelo
        if irrigacao_ativa is None:
            if score <= alpha:
                return "finalizar_irrigacao"

            if score <= beta:
                return "reduzir_irrigacao"

            if score <= gamma:
                return "manter_irrigacao"

            if score <= delta:
                return "iniciar_irrigacao"

            return "aumentar_irrigacao"

        # Caso a irrigação esteja ativa
        if irrigacao_ativa:
            if score <= alpha:
                return "finalizar_irrigacao"

            if score <= beta:
                return "reduzir_irrigacao"

            if score <= gamma:
                return "manter_irrigacao"

            if score <= delta:
                return "manter_irrigacao"

            return "aumentar_irrigacao"

        # Caso a irrigação não esteja ativa
        if not irrigacao_ativa:
            if score <= alpha:
                return "finalizar_irrigacao"

            if score <= beta:
                return "reduzir_irrigacao"

            if score <= gamma:
                return "manter_irrigacao"

            if score <= delta:
                return "iniciar_irrigacao"

            return "iniciar_irrigacao"

    def aplicar_ajuste_operacional(
        self,
        decisao_inicial,
        score,
        ehc,
        earg,
        eaps,
        irrigacao_ativa
    ):
        """
        Aplica ajuste operacional considerando o estado da irrigação
        e as evidências Ehc, Earg e Eaps.

        Essa regra evita que o sistema mantenha irrigação quando
        a irrigação já está ativa, mas a condição continua crítica.
        """

        # Se a irrigação já está ativa, mas as evidências contextual
        # e agronômica indicam alta criticidade, aumenta a irrigação
        if irrigacao_ativa is True:
            if earg == "critico" and ehc in ["alto", "critico"]:
                return "aumentar_irrigacao"

            if score >= self.limiares["delta"]:
                return "aumentar_irrigacao"

        # Se a irrigação não está ativa e a criticidade é alta,
        # a decisão deve ser iniciar irrigação
        if irrigacao_ativa is False:
            if score >= self.limiares["gamma"]:
                return "iniciar_irrigacao"

        return decisao_inicial

    def calcular_confianca(
        self,
        score,
        resultado_aiec,
        resultado_arg,
        resultado_aps
    ):
        """
        Calcula a confiança híbrida usando as confianças das evidências.
        """

        confianca_ehc = resultado_aiec.get(
            "confianca",
            0.5
        )

        confianca_earg = resultado_arg.get(
            "confianca",
            0.5
        )

        confianca_eaps = resultado_aps.get(
            "confianca",
            0.5
        )

        confianca = (
            self.pesos["whc"] * confianca_ehc
            + self.pesos["warg"] * confianca_earg
            + self.pesos["waps"] * confianca_eaps
        )

        return round(
            confianca,
            2
        )

    def gerar_explicacao(
        self,
        decisao_final,
        score,
        ehc,
        earg,
        eaps,
        irrigacao_ativa
    ):
        """
        Gera explicação textual da decisão final D(Ui).
        """

        if irrigacao_ativa is True:
            estado_irrigacao = "a irrigação estava ativa no contexto atual"
        elif irrigacao_ativa is False:
            estado_irrigacao = "a irrigação não estava ativa no contexto atual"
        else:
            estado_irrigacao = "o estado operacional da irrigação não foi informado"

        return (
            f"A decisão final D(Ui) foi {decisao_final}. "
            f"O score híbrido calculado foi {round(score, 2)}. "
            f"As evidências utilizadas foram: "
            f"Ehc={ehc}, Earg={earg} e Eaps={eaps}. "
            f"No momento da decisão, {estado_irrigacao}. "
            f"A decisão foi obtida pela integração ponderada entre "
            f"a evidência contextual consolidada, a evidência agronômica "
            f"e a evidência preditiva supervisionada."
        )


