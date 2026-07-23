"""
ARG Agent do Hydros.

ARG significa Agente de Regras Agronômicas.

Responsabilidade no modelo Hydros:
aplicar regras agronômicas sobre o vetor de atributos do histórico
de contexto e produzir a evidência agronômica Earg.

Entrada:
Xt = vetor de atributos extraído do histórico de contexto
R  = conjunto de regras agronômicas

Saída:
Earg em {baixo, moderado, alto, critico}
"""


class ARGAgent:
    """
    Agente de Regras Agronômicas do modelo Hydros.
    """

    def __init__(self):
        """
        Inicializa o ARG com pesos para cada regra agronômica.
        """

        self.tamanho_janela = 5
        self.nome_evidencia = "Earg"

        # Pesos das regras r1 até r8
        # A soma dos pesos é igual a 1
        self.pesos_regras = {
            "r1": 0.12,
            "r2": 0.16,
            "r3": 0.16,
            "r4": 0.14,
            "r5": 0.14,
            "r6": 0.14,
            "r7": 0.07,
            "r8": 0.07
        }

        # Variáveis do modelo usadas pelas regras
        self.variaveis_modelo = [
            "p",
            "ad",
            "us",
            "ef",
            "kc",
            "et",
            "eh",
            "irr",
            "H(Ui)"
        ]

    def avaliar(self, df, semantic_inference=None):
        """
        Aplica as regras agronômicas e gera Earg.
        """

        janela = df.tail(self.tamanho_janela)
        contexto_atual = janela.iloc[-1]

        # Variáveis atuais
        precipitacao_atual = contexto_atual["precipitacao"]
        agua_disponivel = contexto_atual["agua_disponivel"]
        umidade_solo = contexto_atual["umidade_solo"]
        estagio_fenologico = str(
            contexto_atual["estagio_fenologico"]
        ).upper()
        coeficiente_cultura = contexto_atual["coeficiente_cultura"]
        evapotranspiracao = contexto_atual["evapotranspiracao"]
        estresse_hidrico = str(
            contexto_atual["estresse_hidrico"]
        ).lower()
        irrigacao_aplicada = contexto_atual["irrigacao_aplicada"]

        # Variáveis históricas da janela
        precipitacao_acumulada = janela["precipitacao"].sum()
        irrigacao_acumulada = janela["irrigacao_aplicada"].sum()

        agua_inicial = janela["agua_disponivel"].iloc[0]
        agua_final = janela["agua_disponivel"].iloc[-1]

        umidade_inicial = janela["umidade_solo"].iloc[0]
        umidade_final = janela["umidade_solo"].iloc[-1]

        tendencia_agua = self.calcular_tendencia(
            agua_inicial,
            agua_final
        )

        tendencia_umidade = self.calcular_tendencia(
            umidade_inicial,
            umidade_final
        )

        # Aplica r1 até r8
        r1 = self.r1_precipitacao(
            precipitacao_acumulada
        )

        r2 = self.r2_agua_disponivel(
            agua_disponivel
        )

        r3 = self.r3_umidade_solo(
            umidade_solo
        )

        r4 = self.r4_fenologia_kc(
            estagio_fenologico,
            coeficiente_cultura
        )

        r5 = self.r5_evapotranspiracao_tendencia_agua(
            evapotranspiracao,
            tendencia_agua
        )

        r6 = self.r6_estresse_hidrico(
            estresse_hidrico
        )

        r7 = self.r7_irrigacao_anterior(
            irrigacao_acumulada,
            agua_disponivel,
            umidade_solo
        )

        r8 = self.r8_tendencia_historica(
            tendencia_agua,
            tendencia_umidade,
            precipitacao_acumulada
        )

        pontuacoes_regras = {
            "r1": r1,
            "r2": r2,
            "r3": r3,
            "r4": r4,
            "r5": r5,
            "r6": r6,
            "r7": r7,
            "r8": r8
        }

        score_arg = self.calcular_score_arg(
            pontuacoes_regras
        )

        earg = self.converter_score_para_evidencia(
            score_arg
        )

        confianca_base = self.calcular_confianca(
            score_arg
        )

        integracao_semantica = self.integrar_inferencia_semantica(
            earg=earg,
            confianca_base=confianca_base,
            semantic_inference=semantic_inference,
        )
        confianca = integracao_semantica["confianca_ajustada"]

        regras_acionadas = self.gerar_regras_acionadas(
            pontuacoes_regras
        )

        return {
            "agente": "ARG",
            "nome_agente": "Agente de Regras Agronômicas",
            "evidencia_nome": self.nome_evidencia,
            "Earg": earg,
            "evidencia": earg,
            "criticidade": earg,
            "score": round(score_arg, 2),
            "score_arg": round(score_arg, 2),
            "confianca": confianca,
            "confianca_base": confianca_base,
            "inferencia_semantica": integracao_semantica["inferencia"],
            "consistencia_semantica": integracao_semantica["consistencia"],
            "impacto_semantico": integracao_semantica["impacto"],
            "regras_semanticas": integracao_semantica["regras_semanticas"],
            "avisos": integracao_semantica["avisos"],
            "pesos_regras": self.pesos_regras,
            "pontuacoes_regras": pontuacoes_regras,
            "variaveis_modelo": self.variaveis_modelo,
            "indicadores": {
                "precipitacao_atual": precipitacao_atual,
                "precipitacao_acumulada": round(precipitacao_acumulada, 2),
                "agua_disponivel": agua_disponivel,
                "umidade_solo": umidade_solo,
                "estagio_fenologico": estagio_fenologico,
                "coeficiente_cultura": coeficiente_cultura,
                "evapotranspiracao": evapotranspiracao,
                "estresse_hidrico": estresse_hidrico,
                "irrigacao_aplicada": irrigacao_aplicada,
                "irrigacao_acumulada": round(irrigacao_acumulada, 2),
                "tendencia_agua": tendencia_agua,
                "tendencia_umidade": tendencia_umidade
            },
            "regras_acionadas": regras_acionadas,
            "motivo": (
                "aplicação ponderada das regras agronômicas r1 até r8 "
                "sobre o histórico de contexto, com verificação de "
                "consistência pela HydrosOnto"
            )
        }


    def integrar_inferencia_semantica(
        self,
        *,
        earg,
        confianca_base,
        semantic_inference,
    ):
        """Integra a HydrosOnto como verificação semântica do ARG.

        A ontologia não substitui as regras r1-r8 e não cria uma quarta
        evidência para o AMDH. Ela verifica se a condição inferida pela
        representação semântica é compatível com a evidência agronômica.
        A concordância aumenta discretamente o suporte da evidência; a
        divergência reduz sua confiança e é registrada para explicação.
        """

        if semantic_inference is None:
            return {
                "inferencia": None,
                "consistencia": "nao_avaliada",
                "impacto": 0.0,
                "confianca_ajustada": round(float(confianca_base), 4),
                "regras_semanticas": [],
                "avisos": ["HydrosOnto não forneceu inferência semântica."],
            }

        if hasattr(semantic_inference, "to_dict"):
            inference = semantic_inference.to_dict()
        else:
            inference = dict(semantic_inference)

        semantic_arg = self.condicao_semantica(earg)
        semantic_onto = str(
            inference.get("semantic_condition", "")
        ).strip().lower()
        semantic_confidence = self.limitar_intervalo(
            inference.get("confidence", 0.0)
        )

        if semantic_onto not in {"adequada", "atencao", "critica"}:
            return {
                "inferencia": inference,
                "consistencia": "inferencia_invalida",
                "impacto": -0.05,
                "confianca_ajustada": round(
                    self.limitar_intervalo(float(confianca_base) * 0.90), 4
                ),
                "regras_semanticas": list(
                    inference.get("rules_triggered", [])
                ),
                "avisos": [
                    "A HydrosOnto retornou uma condição semântica inválida."
                ],
            }

        if semantic_arg == semantic_onto:
            consistency = "concordante"
            impact = 0.03 * semantic_confidence
            adjusted = float(confianca_base) + impact
            warnings = []
        else:
            consistency = "divergente"
            impact = -0.08 * semantic_confidence
            adjusted = float(confianca_base) + impact
            warnings = [
                "A evidência agronômica divergiu da condição inferida "
                "pela HydrosOnto; a confiança do ARG foi reduzida."
            ]

        return {
            "inferencia": inference,
            "consistencia": consistency,
            "impacto": round(impact, 4),
            "confianca_ajustada": round(
                self.limitar_intervalo(adjusted), 4
            ),
            "regras_semanticas": list(
                inference.get("rules_triggered", [])
            ),
            "avisos": warnings,
        }

    @staticmethod
    def condicao_semantica(evidencia):
        mapa = {
            "baixo": "adequada",
            "moderado": "atencao",
            "alto": "atencao",
            "critico": "critica",
            "crítico": "critica",
        }
        return mapa.get(str(evidencia).strip().lower(), "atencao")

    @staticmethod
    def limitar_intervalo(value):
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = 0.0
        return max(0.0, min(1.0, number))

    def r1_precipitacao(self, precipitacao_acumulada):
        """
        r1 avalia a precipitação recente ou acumulada.
        """

        if precipitacao_acumulada >= 20:
            return 1

        if precipitacao_acumulada >= 10:
            return 2

        if precipitacao_acumulada >= 5:
            return 3

        return 4

    def r2_agua_disponivel(self, agua_disponivel):
        """
        r2 avalia a disponibilidade de água no solo.
        """

        if agua_disponivel >= 90:
            return 1

        if agua_disponivel >= 65:
            return 2

        if agua_disponivel >= 40:
            return 3

        return 4

    def r3_umidade_solo(self, umidade_solo):
        """
        r3 avalia a umidade do solo.
        """

        if umidade_solo >= 65:
            return 1

        if umidade_solo >= 45:
            return 2

        if umidade_solo >= 30:
            return 3

        return 4

    def r4_fenologia_kc(self, estagio_fenologico, coeficiente_cultura):
        """
        r4 avalia estágio fenológico e coeficiente de cultura.
        """

        if estagio_fenologico in ["R3", "R4", "R5"] and coeficiente_cultura >= 1.0:
            return 4

        if estagio_fenologico in ["R1", "R2", "R3", "R4", "R5"]:
            return 3

        if coeficiente_cultura >= 0.85:
            return 2

        return 1

    def r5_evapotranspiracao_tendencia_agua(
        self,
        evapotranspiracao,
        tendencia_agua
    ):
        """
        r5 avalia evapotranspiração e tendência de redução da água disponível.
        """

        if evapotranspiracao >= 6.5 and tendencia_agua == "queda":
            return 4

        if evapotranspiracao >= 5.5 or tendencia_agua == "queda":
            return 3

        if evapotranspiracao >= 4.5:
            return 2

        return 1

    def r6_estresse_hidrico(self, estresse_hidrico):
        """
        r6 avalia a ocorrência de estresse hídrico.
        """

        mapa = {
            "baixo": 1,
            "moderado": 2,
            "alto": 3,
            "critico": 4
        }

        return mapa.get(
            estresse_hidrico,
            2
        )

    def r7_irrigacao_anterior(
        self,
        irrigacao_acumulada,
        agua_disponivel,
        umidade_solo
    ):
        """
        r7 avalia os efeitos da irrigação aplicada anteriormente.
        """

        if irrigacao_acumulada == 0 and agua_disponivel < 65:
            return 4

        if irrigacao_acumulada > 0 and agua_disponivel < 50:
            return 4

        if irrigacao_acumulada > 0 and umidade_solo < 40:
            return 3

        if irrigacao_acumulada > 0 and agua_disponivel >= 80:
            return 1

        return 2

    def r8_tendencia_historica(
        self,
        tendencia_agua,
        tendencia_umidade,
        precipitacao_acumulada
    ):
        """
        r8 avalia a tendência histórica da condição hídrica.
        """

        if (
            tendencia_agua == "queda"
            and tendencia_umidade == "queda"
            and precipitacao_acumulada < 5
        ):
            return 4

        if tendencia_agua == "queda" and tendencia_umidade == "queda":
            return 3

        if tendencia_agua == "queda" or tendencia_umidade == "queda":
            return 2

        return 1

    def calcular_score_arg(self, pontuacoes_regras):
        """
        Calcula o score agronômico ponderado.
        """

        score = 0

        for regra, pontuacao in pontuacoes_regras.items():
            peso = self.pesos_regras.get(
                regra,
                0
            )

            score += peso * pontuacao

        return score

    def converter_score_para_evidencia(self, score):
        """
        Converte ScoreARG em Earg.
        """

        if score < 1.5:
            return "baixo"

        if score < 2.5:
            return "moderado"

        if score < 3.3:
            return "alto"

        return "critico"

    def calcular_confianca(self, score):
        """
        Calcula confiança simples para Earg.
        """

        confianca = score / 4

        if confianca > 1:
            confianca = 1

        return round(
            confianca,
            2
        )

    def calcular_tendencia(self, valor_inicial, valor_final):
        """
        Calcula tendência simples.
        """

        if valor_final < valor_inicial:
            return "queda"

        if valor_final > valor_inicial:
            return "aumento"

        return "estavel"

    def gerar_regras_acionadas(self, pontuacoes_regras):
        """
        Gera lista textual das regras com maior criticidade.
        """

        regras_acionadas = []

        descricoes = {
            "r1": "r1: precipitação recente ou acumulada",
            "r2": "r2: disponibilidade de água no solo",
            "r3": "r3: umidade do solo",
            "r4": "r4: estágio fenológico e coeficiente de cultura",
            "r5": "r5: evapotranspiração e tendência da água disponível",
            "r6": "r6: estresse hídrico",
            "r7": "r7: irrigação aplicada anteriormente",
            "r8": "r8: tendência histórica da condição hídrica"
        }

        for regra, pontuacao in pontuacoes_regras.items():
            if pontuacao >= 3:
                regras_acionadas.append(
                    f"{descricoes[regra]} com criticidade {pontuacao}"
                )

        if not regras_acionadas:
            regras_acionadas.append(
                "nenhuma regra apresentou criticidade elevada"
            )

        return regras_acionadas
