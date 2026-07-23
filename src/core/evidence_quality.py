"""Qualidade, completude e confiança das evidências do Hydros.

A criticidade expressa a gravidade da condição agrícola. A confiança
expressa quanto os dados disponíveis sustentam a evidência. Esses dois
conceitos são calculados separadamente.

Este módulo enriquece as saídas dos agentes sem alterar as regras que
produzem baixo, moderado, alto ou crítico. Assim, o comportamento
agronômico existente é preservado, enquanto o AIEC passa a integrar
somente evidências ativas e documentadas.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Dict, Mapping, Sequence

import pandas as pd


@dataclass(frozen=True)
class EvidenceQualitySpec:
    """Requisitos mínimos de dados para uma evidência especializada."""

    required_columns: tuple[str, ...]
    ideal_history_size: int = 1


AGENT_QUALITY_SPECS: Dict[str, EvidenceQualitySpec] = {
    "Aclim": EvidenceQualitySpec(
        required_columns=(
            "precipitacao",
            "temperatura",
            "graus_dia",
            "evapotranspiracao",
        ),
        ideal_history_size=5,
    ),
    "Ahid": EvidenceQualitySpec(
        required_columns=(
            "solo",
            "umidade_solo",
            "agua_disponivel",
            "irrigacao_aplicada",
            "estresse_hidrico",
        ),
        ideal_history_size=5,
    ),
    "Afen": EvidenceQualitySpec(
        required_columns=(
            "estagio_fenologico",
            "coeficiente_cultura",
            "graus_dia",
        ),
        ideal_history_size=5,
    ),
    "Ageo": EvidenceQualitySpec(
        required_columns=("loc", "solo"),
        ideal_history_size=1,
    ),
    "Aprod": EvidenceQualitySpec(
        required_columns=("produtividade",),
        ideal_history_size=5,
    ),
    "Ahist": EvidenceQualitySpec(
        required_columns=(
            "precipitacao",
            "temperatura",
            "graus_dia",
            "evapotranspiracao",
            "coeficiente_cultura",
            "umidade_solo",
            "agua_disponivel",
            "irrigacao_aplicada",
            "produtividade",
        ),
        ideal_history_size=5,
    ),
}


def clamp01(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default

    if not math.isfinite(number):
        number = default

    return max(0.0, min(1.0, number))


def value_is_present(value: Any) -> bool:
    """Retorna True quando o valor pode sustentar uma análise."""

    if value is None:
        return False

    try:
        if bool(pd.isna(value)):
            return False
    except (TypeError, ValueError):
        pass

    if isinstance(value, str):
        normalized = value.strip().lower()
        return normalized not in {"", "nan", "none", "null", "na", "n/a"}

    return True


def calculate_current_completeness(
    dataframe: pd.DataFrame,
    required_columns: Sequence[str],
) -> tuple[float, list[str]]:
    """Calcula completude sobre as variáveis realmente recebidas em C(t)."""

    if dataframe.empty or not required_columns:
        return 0.0, list(required_columns)

    current = dataframe.iloc[-1]
    missing: list[str] = []

    for column in required_columns:
        if column not in dataframe.columns or not value_is_present(current.get(column)):
            missing.append(column)

    completeness = 1.0 - (len(missing) / len(required_columns))
    return clamp01(completeness), missing


def calculate_indicator_consistency(result: Mapping[str, Any]) -> float:
    """Verifica se o agente devolveu indicadores rastreáveis.

    A consistência não mede criticidade. Ela apenas verifica se a saída
    contém indicadores utilizáveis e uma justificativa identificável.
    """

    indicators = result.get("indicadores")
    if not isinstance(indicators, Mapping) or not indicators:
        indicator_score = 0.0
    else:
        valid = sum(1 for value in indicators.values() if value_is_present(value))
        indicator_score = valid / len(indicators)

    has_justification = bool(
        str(result.get("motivo", result.get("explicacao", "")) or "").strip()
    )
    justification_score = 1.0 if has_justification else 0.0

    return clamp01(0.8 * indicator_score + 0.2 * justification_score)


def enrich_agent_evidence(
    result: Mapping[str, Any],
    dataframe: pd.DataFrame,
    agent_name: str,
    mode: str,
) -> Dict[str, Any]:
    """Adiciona completude e confiança dos dados sem recalibrar decisões.

    Nesta etapa, a chave histórica ``confianca`` é preservada para evitar
    alterar silenciosamente os pesos já calibrados do protótipo. A nova
    chave ``confianca_dados`` separa a confiabilidade da entrada da força
    interna da evidência. A migração da fórmula de integração para essa
    nova confiança será feita somente após análise de sensibilidade.
    """

    enriched: Dict[str, Any] = dict(result)

    if bool(enriched.get("desativado", False)):
        enriched.update(
            {
                "completude": 0.0,
                "confianca_dados": 0.0,
                "qualidade_dados": 0.0,
                "qualidade": 0.0,
                "cobertura_historica": 0.0,
                "variaveis_obrigatorias": [],
                "variaveis_ausentes": [],
                "evidencia_ativa": False,
                "metodo_confianca_dados": "evidencia_desativada",
            }
        )
        return enriched

    spec = AGENT_QUALITY_SPECS.get(agent_name)
    if spec is None:
        enriched.setdefault("completude", 1.0)
        enriched.setdefault("confianca_dados", 1.0)
        enriched.setdefault("qualidade_dados", 1.0)
        enriched["evidencia_ativa"] = True
        return enriched

    completeness, missing = calculate_current_completeness(
        dataframe,
        spec.required_columns,
    )
    history_coverage = clamp01(len(dataframe) / max(1, spec.ideal_history_size))
    consistency = calculate_indicator_consistency(enriched)
    data_confidence = clamp01(
        0.65 * completeness
        + 0.20 * history_coverage
        + 0.15 * consistency
    )
    data_quality = clamp01(completeness * data_confidence)

    warnings = list(enriched.get("avisos", enriched.get("warnings", [])) or [])
    if missing:
        warnings.append(
            "Variáveis obrigatórias ausentes: " + ", ".join(missing)
        )

    original_confidence = clamp01(enriched.get("confianca", 0.5), 0.5)
    integration_quality = clamp01(original_confidence * completeness)

    enriched.update(
        {
            "confianca": original_confidence,
            "confianca_dados": round(data_confidence, 4),
            "completude": round(completeness, 4),
            "qualidade_dados": round(data_quality, 4),
            "qualidade": round(integration_quality, 4),
            "cobertura_historica": round(history_coverage, 4),
            "consistencia_saida": round(consistency, 4),
            "variaveis_obrigatorias": list(spec.required_columns),
            "variaveis_ausentes": missing,
            "evidencia_ativa": True,
            "metodo_confianca_dados": (
                "0.65*completude + 0.20*cobertura_historica "
                "+ 0.15*consistencia_saida"
            ),
            "avisos": warnings,
            "modo_execucao": mode,
        }
    )

    return enriched
