"""Agente Integrador de Evidências Contextuais do Hydros.

O AIEC integra Eclim, Ehid, Efen, Egeo, Eprod e Ehist. A integração
considera somente evidências ativas e utiliza peso, confiança,
completude e qualidade explicitamente calculados a partir dos dados.

Ehc = Σ(wj × Qj × V(Ej)) / Σ(wj × Qj)
Qj = completudej × confiancaj
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping

from src.config.hydros_terms import FUNCAO_V, LIMIARES_AMDH, PESOS_AIEC
from src.core.contracts import semantic_condition_for


class AIECAgent:
    """Coordena e consolida as evidências contextuais."""

    def __init__(self) -> None:
        self.nome_evidencia = "Ehc"
        self.pesos = dict(PESOS_AIEC)
        self.mapa_criticidade = dict(FUNCAO_V)
        self.mapa_criticidade["medio"] = self.mapa_criticidade["moderado"]

    def integrar(
        self,
        resultado_aclim: Mapping[str, Any],
        resultado_ahid: Mapping[str, Any],
        resultado_afen: Mapping[str, Any],
        resultado_ageo: Mapping[str, Any],
        resultado_aprod: Mapping[str, Any],
        resultado_ahist: Mapping[str, Any],
    ) -> Dict[str, Any]:
        resultados = {
            "Eclim": resultado_aclim,
            "Ehid": resultado_ahid,
            "Efen": resultado_afen,
            "Egeo": resultado_ageo,
            "Eprod": resultado_aprod,
            "Ehist": resultado_ahist,
        }

        evidencias: Dict[str, str] = {}
        confiancas: Dict[str, float] = {}
        completudes: Dict[str, float] = {}
        qualidades: Dict[str, float] = {}
        valores: Dict[str, float] = {}
        ativas: list[str] = []
        desativadas: list[str] = []

        for evidence_name, result in resultados.items():
            evidence = self.extrair_evidencia(result, evidence_name)
            active = self.evidencia_ativa(result)

            evidencias[evidence_name] = evidence

            if not active:
                confiancas[evidence_name] = 0.0
                completudes[evidence_name] = 0.0
                qualidades[evidence_name] = 0.0
                valores[evidence_name] = float(
                    self.mapa_criticidade.get(evidence, 2)
                )
                desativadas.append(evidence_name)
                continue

            confidence = self.extrair_intervalo(result, "confianca", 0.0)
            completeness = self.extrair_intervalo(result, "completude", 0.0)
            declared_quality = result.get("qualidade")
            quality = (
                self.limitar_intervalo(float(declared_quality))
                if declared_quality is not None
                else self.limitar_intervalo(confidence * completeness)
            )

            confiancas[evidence_name] = confidence
            completudes[evidence_name] = completeness
            qualidades[evidence_name] = quality
            valores[evidence_name] = float(
                self.mapa_criticidade.get(evidence, 2)
            )
            ativas.append(evidence_name)

        score_contextual = self.calcular_score_contextual(
            valores=valores,
            qualidades=qualidades,
            evidencias_ativas=ativas,
        )
        ehc = self.converter_score_para_evidencia(score_contextual)

        confidence_context = self.calcular_media_ponderada(
            values=confiancas,
            factors=qualidades,
            active_evidences=ativas,
        )
        completeness_context = self.calcular_media_ponderada(
            values=completudes,
            factors=None,
            active_evidences=ativas,
        )
        quality_context = self.limitar_intervalo(
            confidence_context * completeness_context
        )
        conflict_index = self.calcular_indice_conflito(
            valores[name] for name in ativas
        )

        human_review = (
            confidence_context < LIMIARES_AMDH["confianca_minima"]
            or completeness_context < LIMIARES_AMDH["completude_minima"]
            or conflict_index > LIMIARES_AMDH["conflito_maximo"]
        )

        explanation = self.gerar_explicacao(
            ehc=ehc,
            score_contextual=score_contextual,
            confidence=confidence_context,
            completeness=completeness_context,
            conflict_index=conflict_index,
            evidences=evidencias,
            active_evidences=ativas,
            disabled_evidences=desativadas,
        )

        return {
            "agente": "AIEC",
            "nome_agente": "Agente Integrador de Evidências Contextuais",
            "evidencia_nome": self.nome_evidencia,
            "Ehc": ehc,
            "evidencia": ehc,
            "criticidade": ehc,
            "condicao_semantica": semantic_condition_for(ehc),
            "score": round(score_contextual, 4),
            "score_contextual": round(score_contextual, 4),
            "confianca": round(confidence_context, 4),
            "completude": round(completeness_context, 4),
            "qualidade": round(quality_context, 4),
            "indice_conflito": round(conflict_index, 4),
            "revisao_humana_requerida": human_review,
            "pesos": self.pesos,
            "evidencias_contextuais": evidencias,
            "evidencias_ativas": ativas,
            "evidencias_desativadas": desativadas,
            "confiancas_evidencias": {
                key: round(value, 4) for key, value in confiancas.items()
            },
            "completudes_evidencias": {
                key: round(value, 4) for key, value in completudes.items()
            },
            "qualidades_evidencias": {
                key: round(value, 4) for key, value in qualidades.items()
            },
            "explicacao": explanation,
            "motivo": (
                "integração ponderada das evidências ativas, considerando "
                "peso, confiança, completude e qualidade dos dados"
            ),
        }

    @staticmethod
    def evidencia_ativa(result: Mapping[str, Any]) -> bool:
        if bool(result.get("desativado", False)):
            return False
        if "evidencia_ativa" in result:
            return bool(result.get("evidencia_ativa"))
        return True

    @staticmethod
    def normalizar_evidencia(value: Any) -> str:
        evidence = str(value or "moderado").strip().lower()
        aliases = {
            "médio": "moderado",
            "medio": "moderado",
            "crítico": "critico",
            "crítica": "critico",
            "critica": "critico",
        }
        return aliases.get(evidence, evidence)

    def extrair_evidencia(
        self,
        result: Mapping[str, Any],
        evidence_name: str,
    ) -> str:
        value = result.get(
            evidence_name,
            result.get("evidencia", result.get("criticidade", "moderado")),
        )
        evidence = self.normalizar_evidencia(value)
        return evidence if evidence in self.mapa_criticidade else "moderado"

    @staticmethod
    def extrair_intervalo(
        result: Mapping[str, Any],
        key: str,
        default: float,
    ) -> float:
        try:
            value = float(result.get(key, default))
        except (TypeError, ValueError):
            value = default
        return AIECAgent.limitar_intervalo(value)

    def calcular_score_contextual(
        self,
        valores: Mapping[str, float],
        qualidades: Mapping[str, float],
        evidencias_ativas: Iterable[str],
    ) -> float:
        numerator = 0.0
        denominator = 0.0

        for name in evidencias_ativas:
            weight = float(self.pesos.get(name, 0.0))
            quality = float(qualidades.get(name, 0.0))
            effective_weight = weight * quality
            numerator += effective_weight * float(valores[name])
            denominator += effective_weight

        return numerator / denominator if denominator > 0 else 2.0

    def calcular_media_ponderada(
        self,
        values: Mapping[str, float],
        factors: Mapping[str, float] | None,
        active_evidences: Iterable[str],
    ) -> float:
        numerator = 0.0
        denominator = 0.0

        for name in active_evidences:
            weight = float(self.pesos.get(name, 0.0))
            if factors is not None:
                weight *= float(factors.get(name, 0.0))
            numerator += weight * float(values.get(name, 0.0))
            denominator += weight

        return self.limitar_intervalo(numerator / denominator) if denominator > 0 else 0.0

    @staticmethod
    def calcular_indice_conflito(values: Iterable[float]) -> float:
        items = list(values)
        if len(items) < 2:
            return 0.0
        return AIECAgent.limitar_intervalo((max(items) - min(items)) / 3.0)

    @staticmethod
    def converter_score_para_evidencia(score: float) -> str:
        if score < 1.5:
            return "baixo"
        if score < 2.5:
            return "moderado"
        if score < 3.3:
            return "alto"
        return "critico"

    @staticmethod
    def gerar_explicacao(
        ehc: str,
        score_contextual: float,
        confidence: float,
        completeness: float,
        conflict_index: float,
        evidences: Mapping[str, str],
        active_evidences: Iterable[str],
        disabled_evidences: Iterable[str],
    ) -> str:
        active_set = set(active_evidences)
        evidence_text = ", ".join(
            f"{name}={value}"
            for name, value in evidences.items()
            if name in active_set
        )
        disabled = list(disabled_evidences)
        disabled_text = (
            " Evidências desativadas e excluídas do cálculo: "
            + ", ".join(disabled)
            + "."
            if disabled
            else ""
        )

        return (
            f"Ehc foi classificada como {ehc}, com score "
            f"{score_contextual:.2f}, confiança {confidence:.2f}, "
            f"completude {completeness:.2f} e índice de conflito "
            f"{conflict_index:.2f}. Evidências ativas: "
            f"{evidence_text}.{disabled_text}"
        )

    @staticmethod
    def limitar_intervalo(value: float) -> float:
        return max(0.0, min(1.0, float(value)))
