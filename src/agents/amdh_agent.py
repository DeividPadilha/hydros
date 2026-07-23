"""Agente Motor de Decisão Híbrido do Hydros.

O AMDH integra Ehc, Earg e Eaps e calcula um escore para cada ação
possível. A recomendação final é obtida por ``argmax`` entre as ações
operacionalmente válidas, conforme descrito na proposta de tese.

O agente não aciona equipamentos. A recomendação permanece sob
supervisão do agricultor, técnico agrícola ou gestor.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

from src.config.hydros_terms import (
    ACOES_VALIDAS_POR_ESTADO,
    ALVOS_CRITICIDADE_ACAO,
    CLASSES_DECISAO,
    FUNCAO_V,
    LIMIARES_AMDH,
    ORDEM_DESEMPATE_ACOES,
    PENALIDADES_CONFLITO_ACAO,
    PESOS_AMDH,
)
from src.core.irrigation_state import IrrigationState, infer_irrigation_state


class AMDHAgent:
    """Integra evidências e produz D(Ui) por escore de ação."""

    def __init__(self) -> None:
        self.pesos = dict(PESOS_AMDH)
        self.mapa_criticidade = dict(FUNCAO_V)
        self.mapa_criticidade["medio"] = self.mapa_criticidade["moderado"]
        self.limiares = dict(LIMIARES_AMDH)
        self.alvos_acoes = dict(ALVOS_CRITICIDADE_ACAO)
        self.penalidades_conflito = dict(PENALIDADES_CONFLITO_ACAO)
        self.acoes_validas_por_estado = {
            key: list(value)
            for key, value in ACOES_VALIDAS_POR_ESTADO.items()
        }
        self.ordem_desempate = list(ORDEM_DESEMPATE_ACOES)

        self.peso_penalidade_conflito = float(
            self.limiares.get("peso_penalidade_conflito", 0.20)
        )

    def decidir(
        self,
        resultado_arg: Mapping[str, Any],
        resultado_aiec: Mapping[str, Any],
        resultado_aps: Mapping[str, Any],
        contexto_atual: Mapping[str, Any] | None = None,
        estado_irrigacao: Mapping[str, Any] | IrrigationState | None = None,
    ) -> Dict[str, Any]:
        """Integra Ehc, Earg e Eaps e seleciona a melhor ação válida."""

        ehc = self.extrair_evidencia(resultado_aiec, "Ehc")
        earg = self.extrair_evidencia(resultado_arg, "Earg")
        eaps = self.extrair_evidencia(resultado_aps, "Eaps")

        score_bruto = self.calcular_score_hibrido(ehc, earg, eaps)

        estado = self.obter_estado_irrigacao(
            contexto_atual,
            estado_irrigacao,
        )

        pesos_efetivos = self.calcular_pesos_efetivos(
            resultado_aiec,
            resultado_arg,
            resultado_aps,
        )

        # O conflito entre os três ramos considera os pesos efetivos. Assim,
        # uma previsão reconhecidamente fora do domínio continua registrada,
        # mas não recebe a mesma influência de evidências válidas e completas.
        conflito_principal = self.calcular_conflito_principal(
            ehc,
            earg,
            eaps,
            pesos_efetivos=pesos_efetivos,
        )
        conflito_contextual = self.limitar_intervalo(
            self.converter_float(
                resultado_aiec.get("indice_conflito", 0.0),
                0.0,
            )
        )
        indice_conflito = max(conflito_principal, conflito_contextual)

        penalidade_conflito = (
            self.peso_penalidade_conflito * indice_conflito
        )
        score_ajustado = max(1.0, score_bruto - penalidade_conflito)

        # A confiança final usa os mesmos pesos efetivos empregados no
        # argmax. Assim, uma evidência APS reconhecidamente fora do domínio
        # perde influência sem derrubar artificialmente a confiança dos
        # ramos contextual e agronômico que permanecem válidos.
        confianca_base = self.calcular_confianca_base(
            resultado_aiec,
            resultado_arg,
            resultado_aps,
            pesos_efetivos=pesos_efetivos,
        )
        confianca = self.limitar_intervalo(
            confianca_base * (1.0 - 0.5 * indice_conflito)
        )

        completude = self.calcular_completude_decisao(
            resultado_aiec,
            resultado_arg,
            resultado_aps,
        )

        calculo_acoes = self.calcular_escores_acoes(
            ehc=ehc,
            earg=earg,
            eaps=eaps,
            indice_conflito=indice_conflito,
            estado=estado,
            pesos_efetivos=pesos_efetivos,
        )
        decisao_final = self.selecionar_acao(
            calculo_acoes["escores_validos"]
        )
        score_decisao = calculo_acoes["escores_validos"][decisao_final]

        dependencia_aps = self.analisar_dependencia_aps(
            ehc=ehc,
            earg=earg,
            eaps=eaps,
            indice_conflito_contextual=conflito_contextual,
            estado=estado,
            pesos_efetivos=pesos_efetivos,
            decisao_com_aps=decisao_final,
            resultado_aps=resultado_aps,
        )

        alerta_aiec = bool(
            resultado_aiec.get("revisao_humana_requerida", False)
        )
        motivos_revisao = self.identificar_motivos_revisao(
            decisao_final=decisao_final,
            confianca=confianca,
            completude=completude,
            indice_conflito=indice_conflito,
            estado=estado,
            dependencia_aps=dependencia_aps,
        )
        avisos_governanca = self.identificar_avisos_governanca(
            confianca=confianca,
            alerta_aiec=alerta_aiec,
            resultado_aps=resultado_aps,
            dependencia_aps=dependencia_aps,
        )
        revisao_humana = bool(motivos_revisao)

        explicacao = self.gerar_explicacao(
            decisao_final=decisao_final,
            score_decisao=score_decisao,
            score_bruto=score_bruto,
            score_ajustado=score_ajustado,
            ehc=ehc,
            earg=earg,
            eaps=eaps,
            estado=estado,
            confianca=confianca,
            completude=completude,
            indice_conflito=indice_conflito,
            revisao_humana=revisao_humana,
            motivos_revisao=motivos_revisao,
            avisos_governanca=avisos_governanca,
            dependencia_aps=dependencia_aps,
        )

        return {
            "agente": "AMDH",
            "agente_modelo": "AMDH",
            "nome_agente": "Agente Motor de Decisão Híbrido",
            "D(Ui)": decisao_final,
            "decisao_final": decisao_final,
            # Mantidos para compatibilidade com a interface e os experimentos.
            "score": round(score_ajustado, 4),
            "score_hibrido": round(score_ajustado, 4),
            "score_bruto": round(score_bruto, 4),
            "score_ajustado": round(score_ajustado, 4),
            # Escore efetivamente usado no argmax da ação.
            "score_decisao": round(score_decisao, 6),
            "escores_acoes": self.arredondar_escores(
                calculo_acoes["escores_todas"]
            ),
            "escores_acoes_validos": self.arredondar_escores(
                calculo_acoes["escores_validos"]
            ),
            "escores_acoes_brutos": self.arredondar_escores(
                calculo_acoes["escores_brutos"]
            ),
            "suporte_evidencias_por_acao": calculo_acoes[
                "suporte_evidencias_por_acao"
            ],
            "acoes_bloqueadas": calculo_acoes["acoes_bloqueadas"],
            "criterio_selecao": "argmax_d S(d)",
            "penalidade_conflito": round(penalidade_conflito, 4),
            "confianca_base": round(confianca_base, 4),
            "confianca": round(confianca, 4),
            "completude": round(completude, 4),
            "indice_conflito": round(indice_conflito, 4),
            "conflito_principal": round(conflito_principal, 4),
            "conflito_contextual": round(conflito_contextual, 4),
            "revisao_humana_requerida": revisao_humana,
            "motivos_revisao_humana": motivos_revisao,
            "avisos_governanca": avisos_governanca,
            "alerta_aiec": alerta_aiec,
            "dependencia_aps": dependencia_aps,
            "modo_degradado_aps": bool(
                resultado_aps.get("status_dominio") != "dentro_dominio"
            ),
            "supervisao_humana": {
                "execucao_automatica": False,
                "acoes_permitidas": ["aceitar", "modificar", "rejeitar"],
            },
            "evidencias": {
                "Ehc": ehc,
                "Earg": earg,
                "Eaps": eaps,
            },
            "dominio_aps": {
                "status": resultado_aps.get("status_dominio", "nao_informado"),
                "compatibilidade": resultado_aps.get("compatibilidade_dominio"),
                "fora_dominio": bool(resultado_aps.get("fora_dominio", False)),
                "avisos": list(resultado_aps.get("avisos", [])),
            },
            "pesos": self.pesos,
            "pesos_efetivos": {
                key: round(value, 6)
                for key, value in pesos_efetivos.items()
            },
            "alvos_criticidade_acoes": self.alvos_acoes,
            "limiares": self.limiares,
            "irrigacao_ativa": estado.active,
            "estado_irrigacao": estado.to_dict(),
            "explicacao": explicacao,
            "motivo": (
                "integração de Ehc, Earg e Eaps com cálculo de escore "
                "por ação, restrições operacionais e seleção por argmax"
            ),
        }

    def extrair_evidencia(
        self,
        resultado_agente: Mapping[str, Any],
        nome_evidencia: str,
    ) -> str:
        valor = resultado_agente.get(
            nome_evidencia,
            resultado_agente.get(
                "evidencia",
                resultado_agente.get("criticidade", "moderado"),
            ),
        )

        evidencia = str(valor or "moderado").strip().lower()
        aliases = {
            "médio": "moderado",
            "medio": "moderado",
            "crítico": "critico",
        }
        evidencia = aliases.get(evidencia, evidencia)

        if evidencia not in self.mapa_criticidade:
            return "moderado"

        return evidencia

    def calcular_score_hibrido(
        self,
        ehc: str,
        earg: str,
        eaps: str,
    ) -> float:
        """Calcula o escore contínuo de criticidade para compatibilidade."""

        valor_ehc = float(self.mapa_criticidade.get(ehc, 2))
        valor_earg = float(self.mapa_criticidade.get(earg, 2))
        valor_eaps = float(self.mapa_criticidade.get(eaps, 2))

        return (
            float(self.pesos["whc"]) * valor_ehc
            + float(self.pesos["warg"]) * valor_earg
            + float(self.pesos["waps"]) * valor_eaps
        )

    def calcular_escores_acoes(
        self,
        *,
        ehc: str,
        earg: str,
        eaps: str,
        indice_conflito: float,
        estado: IrrigationState,
        pesos_efetivos: Mapping[str, float],
    ) -> Dict[str, Any]:
        """Calcula S(d) para cada ação prevista pelo Hydros."""

        evidencias = {
            "Ehc": float(self.mapa_criticidade.get(ehc, 2)),
            "Earg": float(self.mapa_criticidade.get(earg, 2)),
            "Eaps": float(self.mapa_criticidade.get(eaps, 2)),
        }

        escores_brutos: Dict[str, float] = {}
        escores_todas: Dict[str, Optional[float]] = {}
        suporte_por_acao: Dict[str, Dict[str, float]] = {}

        estado_nome = estado.state
        acoes_validas = set(
            self.acoes_validas_por_estado.get(
                estado_nome,
                self.acoes_validas_por_estado["desconhecida"],
            )
        )
        acoes_bloqueadas = [
            action for action in CLASSES_DECISAO if action not in acoes_validas
        ]

        for action in CLASSES_DECISAO:
            target = float(self.alvos_acoes[action])
            supports: Dict[str, float] = {}

            for evidence_name, evidence_value in evidencias.items():
                support = self.suporte_acao(
                    evidence_value,
                    target,
                )
                supports[evidence_name] = support

            raw_score = sum(
                float(pesos_efetivos[evidence_name])
                * supports[evidence_name]
                for evidence_name in ("Ehc", "Earg", "Eaps")
            )

            conflict_penalty = (
                float(self.penalidades_conflito.get(action, 0.0))
                * indice_conflito
            )
            adjusted_score = raw_score - conflict_penalty

            # Quando o estado não é conhecido, ações que alteram o manejo
            # recebem uma pequena penalização de segurança. A manutenção
            # continua disponível como recomendação conservadora.
            if estado.active is None and action != "manter_irrigacao":
                adjusted_score -= 0.03

            escores_brutos[action] = raw_score
            suporte_por_acao[action] = {
                key: round(value, 6)
                for key, value in supports.items()
            }

            if action in acoes_validas:
                escores_todas[action] = self.limitar_intervalo(
                    adjusted_score
                )
            else:
                escores_todas[action] = None

        escores_validos = {
            action: float(score)
            for action, score in escores_todas.items()
            if score is not None
        }

        if not escores_validos:
            raise RuntimeError(
                "Nenhuma ação operacionalmente válida foi encontrada."
            )

        return {
            "escores_brutos": escores_brutos,
            "escores_todas": escores_todas,
            "escores_validos": escores_validos,
            "suporte_evidencias_por_acao": suporte_por_acao,
            "acoes_bloqueadas": acoes_bloqueadas,
        }

    @staticmethod
    def suporte_acao(evidence_value: float, action_target: float) -> float:
        """Calcula o suporte normalizado de uma evidência para uma ação."""

        distance = abs(float(evidence_value) - float(action_target))
        return max(0.0, min(1.0, 1.0 - distance / 3.0))

    def selecionar_acao(self, scores: Mapping[str, float]) -> str:
        """Seleciona argmax com desempate conservador e determinístico."""

        best_score = max(float(value) for value in scores.values())
        tolerance = 1e-12
        candidates = {
            action
            for action, value in scores.items()
            if abs(float(value) - best_score) <= tolerance
        }

        for action in self.ordem_desempate:
            if action in candidates:
                return action

        return sorted(candidates)[0]

    def calcular_pesos_efetivos(
        self,
        resultado_aiec: Mapping[str, Any],
        resultado_arg: Mapping[str, Any],
        resultado_aps: Mapping[str, Any],
    ) -> Dict[str, float]:
        """Ajusta os pesos pela confiança e completude de cada evidência."""

        results = {
            "Ehc": (resultado_aiec, float(self.pesos["whc"])),
            "Earg": (resultado_arg, float(self.pesos["warg"])),
            "Eaps": (resultado_aps, float(self.pesos["waps"])),
        }

        raw_weights: Dict[str, float] = {}
        for evidence_name, (result, base_weight) in results.items():
            confidence = self.limitar_intervalo(
                self.converter_float(result.get("confianca", 0.5), 0.5)
            )
            completeness = self.limitar_intervalo(
                self.converter_float(result.get("completude", 1.0), 1.0)
            )
            raw_weights[evidence_name] = (
                base_weight * max(confidence * completeness, 0.05)
            )

        total = sum(raw_weights.values())
        if total <= 0.0:
            return {
                "Ehc": float(self.pesos["whc"]),
                "Earg": float(self.pesos["warg"]),
                "Eaps": float(self.pesos["waps"]),
            }

        return {
            key: value / total
            for key, value in raw_weights.items()
        }

    def calcular_conflito_principal(
        self,
        ehc: str,
        earg: str,
        eaps: str,
        pesos_efetivos: Mapping[str, float] | None = None,
    ) -> float:
        """Calcula divergência ponderada entre Ehc, Earg e Eaps.

        O conflito é a média das distâncias normalizadas entre pares,
        ponderada pelo menor peso efetivo do par. Essa formulação impede que
        um ramo com baixa validade científica domine o indicador global.
        """

        valores = {
            "Ehc": float(self.mapa_criticidade.get(ehc, 2)),
            "Earg": float(self.mapa_criticidade.get(earg, 2)),
            "Eaps": float(self.mapa_criticidade.get(eaps, 2)),
        }
        pesos = pesos_efetivos or {
            "Ehc": float(self.pesos["whc"]),
            "Earg": float(self.pesos["warg"]),
            "Eaps": float(self.pesos["waps"]),
        }

        pares = (("Ehc", "Earg"), ("Ehc", "Eaps"), ("Earg", "Eaps"))
        numerador = 0.0
        denominador = 0.0
        for esquerda, direita in pares:
            peso_par = min(
                max(float(pesos.get(esquerda, 0.0)), 0.0),
                max(float(pesos.get(direita, 0.0)), 0.0),
            )
            if peso_par <= 0.0:
                continue
            distancia = abs(valores[esquerda] - valores[direita]) / 3.0
            numerador += peso_par * distancia
            denominador += peso_par

        if denominador <= 0.0:
            return 0.0
        return self.limitar_intervalo(numerador / denominador)

    def obter_estado_irrigacao(
        self,
        contexto_atual: Mapping[str, Any] | None,
        estado_irrigacao: Mapping[str, Any] | IrrigationState | None,
    ) -> IrrigationState:
        if isinstance(estado_irrigacao, IrrigationState):
            return estado_irrigacao

        if isinstance(estado_irrigacao, Mapping):
            active = estado_irrigacao.get(
                "active",
                estado_irrigacao.get("ativa"),
            )
            if active not in (True, False, None):
                active = None

            state = str(
                estado_irrigacao.get(
                    "state",
                    "ativa" if active is True else (
                        "inativa" if active is False else "desconhecida"
                    ),
                )
            )
            return IrrigationState(
                active=active,
                state=state,
                source=str(estado_irrigacao.get("source", "fornecido_ao_amdh")),
                confidence=self.limitar_intervalo(
                    self.converter_float(
                        estado_irrigacao.get("confidence", 1.0),
                        1.0,
                    )
                ),
                applied_mm=self.converter_float_opcional(
                    estado_irrigacao.get("applied_mm")
                ),
                explicit=bool(estado_irrigacao.get("explicit", False)),
            )

        return infer_irrigation_state(contexto_atual)

    def calcular_confianca_base(
        self,
        resultado_aiec: Mapping[str, Any],
        resultado_arg: Mapping[str, Any],
        resultado_aps: Mapping[str, Any],
        pesos_efetivos: Mapping[str, float] | None = None,
    ) -> float:
        confiancas = {
            "Ehc": self.limitar_intervalo(
                self.converter_float(resultado_aiec.get("confianca", 0.5), 0.5)
            ),
            "Earg": self.limitar_intervalo(
                self.converter_float(resultado_arg.get("confianca", 0.5), 0.5)
            ),
            "Eaps": self.limitar_intervalo(
                self.converter_float(resultado_aps.get("confianca", 0.5), 0.5)
            ),
        }

        weights = pesos_efetivos or {
            "Ehc": float(self.pesos["whc"]),
            "Earg": float(self.pesos["warg"]),
            "Eaps": float(self.pesos["waps"]),
        }
        total = sum(float(weights.get(key, 0.0)) for key in confiancas)
        if total <= 0.0:
            return 0.0

        return self.limitar_intervalo(
            sum(
                float(weights.get(key, 0.0)) * confidence
                for key, confidence in confiancas.items()
            )
            / total
        )

    def calcular_completude_decisao(
        self,
        resultado_aiec: Mapping[str, Any],
        resultado_arg: Mapping[str, Any],
        resultado_aps: Mapping[str, Any],
    ) -> float:
        completude_ehc = self.limitar_intervalo(
            self.converter_float(resultado_aiec.get("completude", 1.0), 1.0)
        )
        completude_earg = self.limitar_intervalo(
            self.converter_float(resultado_arg.get("completude", 1.0), 1.0)
        )
        completude_eaps = self.limitar_intervalo(
            self.converter_float(resultado_aps.get("completude", 1.0), 1.0)
        )

        return self.limitar_intervalo(
            float(self.pesos["whc"]) * completude_ehc
            + float(self.pesos["warg"]) * completude_earg
            + float(self.pesos["waps"]) * completude_eaps
        )

    def analisar_dependencia_aps(
        self,
        *,
        ehc: str,
        earg: str,
        eaps: str,
        indice_conflito_contextual: float,
        estado: IrrigationState,
        pesos_efetivos: Mapping[str, float],
        decisao_com_aps: str,
        resultado_aps: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """Executa análise contrafactual retirando a influência do APS.

        O objetivo é distinguir um simples aviso de domínio de uma situação
        em que a recomendação final depende materialmente de uma previsão que
        não possui suporte científico suficiente para o cenário analisado.
        """

        status_dominio = str(
            resultado_aps.get("status_dominio", "nao_informado")
        )
        fora_dominio = status_dominio != "dentro_dominio"

        peso_ehc = max(float(pesos_efetivos.get("Ehc", 0.0)), 0.0)
        peso_earg = max(float(pesos_efetivos.get("Earg", 0.0)), 0.0)
        total_sem_aps = peso_ehc + peso_earg
        if total_sem_aps <= 0.0:
            pesos_sem_aps = {"Ehc": 0.5, "Earg": 0.5, "Eaps": 0.0}
        else:
            pesos_sem_aps = {
                "Ehc": peso_ehc / total_sem_aps,
                "Earg": peso_earg / total_sem_aps,
                "Eaps": 0.0,
            }

        conflito_sem_aps = self.calcular_conflito_principal(
            ehc,
            earg,
            eaps,
            pesos_efetivos=pesos_sem_aps,
        )
        indice_sem_aps = max(
            conflito_sem_aps,
            self.limitar_intervalo(indice_conflito_contextual),
        )
        calculo_sem_aps = self.calcular_escores_acoes(
            ehc=ehc,
            earg=earg,
            eaps=eaps,
            indice_conflito=indice_sem_aps,
            estado=estado,
            pesos_efetivos=pesos_sem_aps,
        )
        decisao_sem_aps = self.selecionar_acao(
            calculo_sem_aps["escores_validos"]
        )
        influencia_material = decisao_sem_aps != decisao_com_aps

        return {
            "status_dominio": status_dominio,
            "fora_dominio": fora_dominio,
            "peso_efetivo_aps": round(
                float(pesos_efetivos.get("Eaps", 0.0)), 6
            ),
            "decisao_com_aps": decisao_com_aps,
            "decisao_sem_aps": decisao_sem_aps,
            "influencia_material": influencia_material,
            "concordancia_ehc_earg": ehc == earg,
            "conflito_sem_aps": round(indice_sem_aps, 6),
            "criterio": (
                "A influência é material quando a retirada contrafactual do "
                "APS altera D(Ui)."
            ),
        }

    def identificar_motivos_revisao(
        self,
        *,
        decisao_final: str,
        confianca: float,
        completude: float,
        indice_conflito: float,
        estado: IrrigationState,
        dependencia_aps: Mapping[str, Any],
    ) -> list[str]:
        """Identifica somente situações que exigem revisão humana especial.

        Toda recomendação do Hydros permanece sob decisão humana. Este campo
        representa uma revisão excepcional, distinta da supervisão ordinária.
        """

        motivos: list[str] = []

        confianca_intervencao = float(
            self.limiares.get("confianca_intervencao", 0.50)
        )
        conflito_critico = float(
            self.limiares.get("conflito_critico", 0.80)
        )
        conflito_intervencao = float(
            self.limiares.get(
                "conflito_intervencao",
                self.limiares.get("conflito_maximo", 0.45),
            )
        )

        if completude < float(self.limiares["completude_minima"]):
            motivos.append("completude_abaixo_do_limiar")

        if indice_conflito > conflito_critico:
            motivos.append("conflito_critico_entre_evidencias")

        if (
            bool(dependencia_aps.get("fora_dominio", False))
            and bool(dependencia_aps.get("influencia_material", False))
        ):
            motivos.append("decisao_dependente_de_aps_fora_do_dominio")

        intervention_actions = {
            "iniciar_irrigacao",
            "aumentar_irrigacao",
            "reduzir_irrigacao",
            "finalizar_irrigacao",
        }

        if decisao_final in intervention_actions:
            if confianca < confianca_intervencao:
                motivos.append("baixa_confianca_para_intervencao")

            if indice_conflito > conflito_intervencao:
                motivos.append("conflito_na_recomendacao_de_intervencao")

            if estado.active is None:
                motivos.append("estado_da_irrigacao_desconhecido")
            elif estado.confidence < 0.50:
                motivos.append("baixa_confianca_no_estado_da_irrigacao")

        return motivos

    def identificar_avisos_governanca(
        self,
        *,
        confianca: float,
        alerta_aiec: bool,
        resultado_aps: Mapping[str, Any],
        dependencia_aps: Mapping[str, Any],
    ) -> list[str]:
        """Registra limitações sem convertê-las automaticamente em revisão."""

        avisos: list[str] = []
        confianca_critica = float(
            self.limiares.get("confianca_critica", 0.40)
        )
        if confianca < confianca_critica:
            avisos.append("confianca_global_baixa")
        if alerta_aiec:
            avisos.append("alerta_interno_do_aiec")
        if resultado_aps.get("status_dominio") != "dentro_dominio":
            avisos.append("aps_fora_ou_parcialmente_fora_do_dominio")
        if dependencia_aps.get("influencia_material", False):
            avisos.append("aps_alterou_a_decisao_no_teste_contrafactual")
        return avisos

    def gerar_explicacao(
        self,
        *,
        decisao_final: str,
        score_decisao: float,
        score_bruto: float,
        score_ajustado: float,
        ehc: str,
        earg: str,
        eaps: str,
        estado: IrrigationState,
        confianca: float,
        completude: float,
        indice_conflito: float,
        revisao_humana: bool,
        motivos_revisao: list[str],
        avisos_governanca: list[str],
        dependencia_aps: Mapping[str, Any],
    ) -> str:
        review_text = (
            "A recomendação requer revisão humana especial pelos motivos: "
            + ", ".join(motivos_revisao)
            + "."
            if revisao_humana
            else "A recomendação não ultrapassou os limiares de revisão especial."
        )
        warning_text = (
            " Avisos de governança: " + ", ".join(avisos_governanca) + "."
            if avisos_governanca
            else ""
        )
        aps_text = (
            " A análise contrafactual do APS produziu "
            f"D_sem_APS={dependencia_aps.get('decisao_sem_aps')}; "
            f"influência material={dependencia_aps.get('influencia_material')}."
        )

        return (
            f"D(Ui)={decisao_final}, selecionada por argmax dos escores "
            f"das ações válidas, com S(d)={score_decisao:.3f}. "
            f"Ehc={ehc}, Earg={earg} e Eaps={eaps}. O escore contínuo "
            f"de criticidade foi {score_bruto:.2f} e o valor ajustado foi "
            f"{score_ajustado:.2f}. O estado da irrigação foi classificado "
            f"como {estado.state}, com origem '{estado.source}' e confiança "
            f"{estado.confidence:.2f}. Confiança da decisão={confianca:.2f}, "
            f"completude={completude:.2f} e conflito={indice_conflito:.2f}. "
            f"{review_text}{warning_text}{aps_text} A decisão é uma "
            "recomendação e não aciona "
            f"automaticamente o sistema de irrigação."
        )

    @staticmethod
    def arredondar_escores(
        scores: Mapping[str, Optional[float]],
    ) -> Dict[str, Optional[float]]:
        return {
            key: None if value is None else round(float(value), 6)
            for key, value in scores.items()
        }

    @staticmethod
    def converter_float(valor: Any, padrao: float) -> float:
        try:
            return float(valor)
        except (TypeError, ValueError):
            return float(padrao)

    @staticmethod
    def converter_float_opcional(valor: Any) -> Optional[float]:
        try:
            return float(valor)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def limitar_intervalo(valor: float) -> float:
        return max(0.0, min(1.0, float(valor)))
