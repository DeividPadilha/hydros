"""Contratos padronizados de execução, evidência e decisão do Hydros.

Este módulo não substitui os dicionários retornados pelos agentes atuais.
Ele os normaliza em um registro único, serializável e rastreável, mantendo
compatibilidade com a interface e os testes já existentes.

A estrutura atende aos elementos especificados na proposta de tese:

- unidade de manejo e instante da análise;
- modo Histórico ou Instantâneo;
- contextos e janela temporal utilizados;
- agentes acionados;
- evidências e variáveis utilizadas;
- regras agronômicas aplicadas;
- resultado preditivo;
- confiança, completude e conflito;
- recomendação final e supervisão humana;
- espaço reservado para inferências da HydrosOnto e resposta do usuário.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import date, datetime
from enum import Enum
import math
from typing import Any, Dict, Iterable, List, Mapping, Optional
from uuid import uuid4


class SemanticCondition(str, Enum):
    """Escala semântica de três níveis definida na proposta de tese."""

    ADEQUADA = "adequada"
    ATENCAO = "atencao"
    CRITICA = "critica"


_INTERNAL_LEVEL_ALIASES: Dict[str, str] = {
    "baixo": "baixo",
    "baixa": "baixo",
    "adequado": "baixo",
    "adequada": "baixo",
    "moderado": "moderado",
    "moderada": "moderado",
    "medio": "moderado",
    "médio": "moderado",
    "atencao": "moderado",
    "atenção": "moderado",
    "alto": "alto",
    "alta": "alto",
    "critico": "critico",
    "crítico": "critico",
    "critica": "critico",
    "crítica": "critico",
}

_SEMANTIC_CONDITION_BY_INTERNAL_LEVEL: Dict[str, SemanticCondition] = {
    "baixo": SemanticCondition.ADEQUADA,
    "moderado": SemanticCondition.ATENCAO,
    "alto": SemanticCondition.ATENCAO,
    "critico": SemanticCondition.CRITICA,
}


@dataclass
class AgentEvidenceRecord:
    """Evidência padronizada produzida por um agente do Hydros."""

    agent: str
    evidence_name: str
    unit_id: str
    timestamp: str
    internal_level: str
    semantic_condition: str
    score: float
    confidence: float
    completeness: float
    quality: float
    active: bool = True
    variables_used: List[str] = field(default_factory=list)
    indicators: Dict[str, Any] = field(default_factory=dict)
    rules_triggered: List[str] = field(default_factory=list)
    justification: str = ""
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return to_serializable(asdict(self))


@dataclass
class HydrosDecisionRecord:
    """Registro padronizado da recomendação produzida pelo AMDH."""

    action: str
    unit_id: str
    timestamp: str
    mode: str
    internal_condition: str
    semantic_condition: str
    score: float
    raw_score: float
    confidence: float
    completeness: float
    conflict_index: float
    human_review_required: bool
    human_review_reasons: List[str] = field(default_factory=list)
    governance_warnings: List[str] = field(default_factory=list)
    aps_degraded_mode: bool = False
    aps_dependency: Dict[str, Any] = field(default_factory=dict)
    irrigation_active: Optional[bool] = None
    irrigation_state: str = "desconhecida"
    irrigation_state_source: str = "nao_informado"
    irrigation_state_confidence: float = 0.0
    blocked_actions: List[str] = field(default_factory=list)
    evidence_summary: Dict[str, str] = field(default_factory=dict)
    class_scores: Dict[str, Any] = field(default_factory=dict)
    rationale: str = ""
    automatic_execution: bool = False
    user_status: str = "nao_avaliada"
    user_modified_action: Optional[str] = None
    user_justification: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return to_serializable(asdict(self))


@dataclass
class ExecutionTraceRecord:
    """Rastreabilidade completa de uma execução do Hydros."""

    execution_id: str
    executed_at: str
    architecture_version: str
    unit_id: str
    analysis_timestamp: str
    mode: str
    available_contexts: int
    used_contexts: int
    historical_window: Dict[str, Any]
    current_context: Dict[str, Any]
    agents_executed: List[str]
    evidences: Dict[str, AgentEvidenceRecord]
    agronomic_rules: List[str]
    predictive_result: Dict[str, Any]
    semantic_inferences: List[Dict[str, Any]]
    consistency: Dict[str, Any]
    decision: HydrosDecisionRecord
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        return to_serializable(payload)


def normalize_internal_level(value: Any, default: str = "moderado") -> str:
    """Normaliza níveis internos sem alterar a escala atual do protótipo."""

    text = str(value if value is not None else default).strip().lower()
    return _INTERNAL_LEVEL_ALIASES.get(text, default)


def semantic_condition_for(value: Any) -> str:
    """Converte a escala interna em adequada, atenção ou crítica."""

    internal_level = normalize_internal_level(value)
    return _SEMANTIC_CONDITION_BY_INTERNAL_LEVEL[internal_level].value


def clamp01(value: Any, default: float = 0.0) -> float:
    """Converte um valor para o intervalo fechado [0, 1]."""

    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default

    if not math.isfinite(number):
        number = default

    return max(0.0, min(1.0, number))


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float(default)

    return number if math.isfinite(number) else float(default)


def infer_evidence_name(agent_name: str, result: Mapping[str, Any]) -> str:
    explicit = result.get("evidencia_nome")
    if explicit:
        return str(explicit)

    mapping = {
        "Aclim": "Eclim",
        "Ahid": "Ehid",
        "Afen": "Efen",
        "Ageo": "Egeo",
        "Aprod": "Eprod",
        "Ahist": "Ehist",
        "AIEC": "Ehc",
        "ARG": "Earg",
        "APS": "Eaps",
    }
    return mapping.get(agent_name, "E")


def extract_evidence_level(result: Mapping[str, Any], evidence_name: str) -> str:
    value = result.get(
        evidence_name,
        result.get("evidencia", result.get("criticidade", "moderado")),
    )
    return normalize_internal_level(value)


def extract_variables(result: Mapping[str, Any]) -> List[str]:
    candidates: Iterable[Any] = (
        result.get("variaveis_utilizadas"),
        result.get("variaveis_modelo"),
        result.get("features_usadas"),
        result.get("colunas_csv"),
    )

    variables: List[str] = []
    for candidate in candidates:
        if not candidate:
            continue
        if isinstance(candidate, str):
            values = [candidate]
        else:
            try:
                values = list(candidate)
            except TypeError:
                values = [candidate]

        for value in values:
            text = str(value)
            if text not in variables:
                variables.append(text)

    return variables


def infer_completeness(result: Mapping[str, Any]) -> float:
    """Obtém a completude declarada sem inventar dados ausentes.

    Agentes que ainda não calculam completude recebem temporariamente 1.0.
    Essa compatibilidade será substituída no próximo ajuste, quando cada
    agente passará a validar suas variáveis obrigatórias diretamente.
    """

    if "completude" in result:
        return clamp01(result.get("completude"), 0.0)
    if result.get("desativado") is True:
        return 0.0
    return 1.0


def build_evidence_record(
    result: Mapping[str, Any],
    unit_id: str,
    timestamp: str,
) -> AgentEvidenceRecord:
    agent = str(result.get("agente_modelo", result.get("agente", "desconhecido")))
    evidence_name = infer_evidence_name(agent, result)
    internal_level = extract_evidence_level(result, evidence_name)
    confidence = clamp01(result.get("confianca", 0.0), 0.0)
    completeness = infer_completeness(result)
    active = not bool(result.get("desativado", False))
    quality = clamp01(confidence * completeness, 0.0) if active else 0.0

    warnings: List[str] = []
    raw_warnings = result.get("avisos", result.get("warnings", []))
    if isinstance(raw_warnings, str):
        warnings = [raw_warnings]
    elif raw_warnings:
        warnings = [str(item) for item in raw_warnings]

    return AgentEvidenceRecord(
        agent=agent,
        evidence_name=evidence_name,
        unit_id=unit_id,
        timestamp=timestamp,
        internal_level=internal_level,
        semantic_condition=semantic_condition_for(internal_level),
        score=safe_float(
            result.get("score_contextual", result.get("score_arg", result.get("score", 0.0))),
            0.0,
        ),
        confidence=confidence,
        completeness=completeness,
        quality=quality,
        active=active,
        variables_used=extract_variables(result),
        indicators=to_serializable(result.get("indicadores", {})),
        rules_triggered=[str(item) for item in result.get("regras_acionadas", [])],
        justification=str(
            result.get("explicacao", result.get("motivo", "")) or ""
        ),
        warnings=warnings,
        metadata={
            "algorithm": result.get("algoritmo"),
            "model": result.get("modelo"),
            "model_version": result.get("versao_modelo"),
            "model_hash": result.get("hash_modelo"),
            "scientific_status": result.get("status_cientifico_modelo"),
            "probability_calibration": result.get("calibracao_probabilidades"),
            "probabilities": to_serializable(result.get("probabilidades", {})),
            "raw_model_confidence": result.get("confianca_bruta_modelo"),
            "domain_adjusted_confidence": result.get("confianca_ajustada_dominio"),
            "domain_compatibility": result.get("compatibilidade_dominio"),
            "domain_status": result.get("status_dominio"),
            "out_of_domain": bool(result.get("fora_dominio", False)),
            "unknown_categories": to_serializable(
                result.get("categorias_desconhecidas", {})
            ),
            "out_of_range_features": to_serializable(
                result.get("features_fora_faixa", {})
            ),
            "imputed_values": to_serializable(
                result.get("valores_imputados", {})
            ),
            "feature_importance": to_serializable(
                result.get("importancia_atributos", [])
            ),
            "explainability_type": result.get("tipo_explicabilidade_aps"),
            "mode": result.get("modo_execucao"),
            "disabled": bool(result.get("desativado", False)),
        },
    )


def _extract_unit_id(context: Mapping[str, Any]) -> str:
    for key in ("talhao", "unit_id", "unidade_manejo", "cenario_id"):
        value = context.get(key)
        if value is not None and str(value).strip():
            return str(value)
    return "unidade_nao_informada"


def _extract_timestamp(context: Mapping[str, Any]) -> str:
    for key in ("data", "timestamp", "data_hora", "date"):
        value = context.get(key)
        if value is not None and str(value).strip():
            return str(to_serializable(value))
    return "instante_nao_informado"


def _historical_window(
    history_dataframe: Any,
    available_contexts: int,
    used_contexts: int,
    mode: str,
) -> Dict[str, Any]:
    start = None
    end = None

    try:
        if history_dataframe is not None and len(history_dataframe) > 0:
            date_column = next(
                (
                    column
                    for column in ("data", "timestamp", "data_hora", "date")
                    if column in history_dataframe.columns
                ),
                None,
            )
            if date_column:
                start = to_serializable(history_dataframe.iloc[0][date_column])
                end = to_serializable(history_dataframe.iloc[-1][date_column])
    except (AttributeError, IndexError, KeyError, TypeError):
        start = None
        end = None

    return {
        "mode": mode,
        "start": start,
        "end": end,
        "available_contexts": int(available_contexts),
        "used_contexts": int(used_contexts),
        "history_used": mode == "historico",
    }


def build_execution_trace(
    *,
    mode: str,
    architecture_version: str,
    history_dataframe: Any,
    current_context: Mapping[str, Any],
    available_contexts: int,
    used_contexts: int,
    agent_results: Mapping[str, Mapping[str, Any]],
    amdh_result: Mapping[str, Any],
    semantic_inferences: Optional[List[Mapping[str, Any]]] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> ExecutionTraceRecord:
    """Constrói o registro rastreável sem alterar o fluxo decisório atual."""

    unit_id = _extract_unit_id(current_context)
    timestamp = _extract_timestamp(current_context)

    evidences: Dict[str, AgentEvidenceRecord] = {}
    for key, result in agent_results.items():
        if not isinstance(result, Mapping):
            continue
        record = build_evidence_record(result, unit_id, timestamp)
        evidences[key] = record

    aiec_result = agent_results.get("aiec", {})
    arg_result = agent_results.get("arg", {})
    aps_result = agent_results.get("aps", {})

    evidence_summary = {
        "Ehc": extract_evidence_level(aiec_result, "Ehc"),
        "Earg": extract_evidence_level(arg_result, "Earg"),
        "Eaps": extract_evidence_level(aps_result, "Eaps"),
    }
    decision_internal_condition = evidence_summary["Ehc"]

    decision = HydrosDecisionRecord(
        action=str(
            amdh_result.get("decisao_final", amdh_result.get("D(Ui)", "nao_informada"))
        ),
        unit_id=unit_id,
        timestamp=timestamp,
        mode=mode,
        internal_condition=decision_internal_condition,
        semantic_condition=semantic_condition_for(decision_internal_condition),
        score=safe_float(
            amdh_result.get("score_ajustado", amdh_result.get("score", 0.0)),
            0.0,
        ),
        raw_score=safe_float(
            amdh_result.get("score_bruto", amdh_result.get("score", 0.0)),
            0.0,
        ),
        confidence=clamp01(amdh_result.get("confianca", 0.0), 0.0),
        completeness=clamp01(amdh_result.get("completude", 0.0), 0.0),
        conflict_index=clamp01(amdh_result.get("indice_conflito", 0.0), 0.0),
        human_review_required=bool(
            amdh_result.get("revisao_humana_requerida", False)
        ),
        human_review_reasons=[
            str(item) for item in amdh_result.get("motivos_revisao_humana", [])
        ],
        governance_warnings=[
            str(item) for item in amdh_result.get("avisos_governanca", [])
        ],
        aps_degraded_mode=bool(
            amdh_result.get("modo_degradado_aps", False)
        ),
        aps_dependency=to_serializable(
            amdh_result.get("dependencia_aps", {})
        ),
        irrigation_active=amdh_result.get("irrigacao_ativa"),
        irrigation_state=str(
            amdh_result.get("estado_irrigacao", {}).get(
                "state",
                "desconhecida",
            )
        ),
        irrigation_state_source=str(
            amdh_result.get("estado_irrigacao", {}).get(
                "source",
                "nao_informado",
            )
        ),
        irrigation_state_confidence=clamp01(
            amdh_result.get("estado_irrigacao", {}).get(
                "confidence",
                0.0,
            ),
            0.0,
        ),
        blocked_actions=[
            str(item)
            for item in amdh_result.get("acoes_bloqueadas", [])
        ],
        evidence_summary=evidence_summary,
        class_scores=to_serializable(amdh_result.get("escores_acoes", {})),
        rationale=str(amdh_result.get("explicacao", "") or ""),
        automatic_execution=bool(
            amdh_result.get("supervisao_humana", {}).get(
                "execucao_automatica", False
            )
        ),
    )

    agronomic_rules = [
        str(item) for item in arg_result.get("regras_acionadas", [])
    ]

    predictive_result = {
        "algorithm": aps_result.get("algoritmo"),
        "model": aps_result.get("modelo"),
        "model_version": aps_result.get("versao_modelo"),
        "model_hash": aps_result.get("hash_modelo"),
        "scientific_status": aps_result.get("status_cientifico_modelo"),
        "predicted_condition": evidence_summary["Eaps"],
        "semantic_condition": semantic_condition_for(evidence_summary["Eaps"]),
        "confidence": clamp01(aps_result.get("confianca", 0.0), 0.0),
        "raw_confidence": clamp01(
            aps_result.get("confianca_bruta_modelo", 0.0), 0.0
        ),
        "domain_adjusted_confidence": clamp01(
            aps_result.get("confianca_ajustada_dominio", 0.0), 0.0
        ),
        "domain_compatibility": clamp01(
            aps_result.get("compatibilidade_dominio", 0.0), 0.0
        ),
        "domain_status": aps_result.get("status_dominio"),
        "probabilities": to_serializable(aps_result.get("probabilidades", {})),
        "features_used": [str(item) for item in aps_result.get("features_usadas", [])],
        "feature_importance": to_serializable(
            aps_result.get("importancia_atributos", [])
        ),
        "out_of_domain": bool(aps_result.get("fora_dominio", False)),
        "unknown_categories": to_serializable(
            aps_result.get("categorias_desconhecidas", [])
        ),
        "warnings": [str(item) for item in aps_result.get("avisos", [])],
    }

    consistency = {
        "contextual_conflict": clamp01(aiec_result.get("indice_conflito", 0.0), 0.0),
        "decision_conflict": clamp01(amdh_result.get("indice_conflito", 0.0), 0.0),
        "completeness": clamp01(amdh_result.get("completude", 0.0), 0.0),
        "confidence": clamp01(amdh_result.get("confianca", 0.0), 0.0),
        "human_review_required": bool(
            amdh_result.get("revisao_humana_requerida", False)
        ),
        "human_review_reasons": [
            str(item) for item in amdh_result.get("motivos_revisao_humana", [])
        ],
        "governance_warnings": [
            str(item) for item in amdh_result.get("avisos_governanca", [])
        ],
        "aps_degraded_mode": bool(
            amdh_result.get("modo_degradado_aps", False)
        ),
        "aps_dependency": to_serializable(
            amdh_result.get("dependencia_aps", {})
        ),
        "irrigation_state": to_serializable(
            amdh_result.get("estado_irrigacao", {})
        ),
        "blocked_actions": [
            str(item) for item in amdh_result.get("acoes_bloqueadas", [])
        ],
        "action_scores": to_serializable(
            amdh_result.get("escores_acoes", {})
        ),
    }

    warnings: List[str] = []
    if decision.human_review_required:
        warnings.append("revisao_humana_especial_requerida")
    if decision.completeness < 0.70:
        warnings.append("completude_insuficiente")
    if predictive_result["out_of_domain"]:
        warnings.append("cenario_fora_do_dominio_do_aps")
    warnings.extend(
        str(item) for item in amdh_result.get("avisos_governanca", [])
        if str(item) not in warnings
    )

    return ExecutionTraceRecord(
        execution_id=str(uuid4()),
        executed_at=datetime.now().isoformat(timespec="seconds"),
        architecture_version=architecture_version,
        unit_id=unit_id,
        analysis_timestamp=timestamp,
        mode=mode,
        available_contexts=int(available_contexts),
        used_contexts=int(used_contexts),
        historical_window=_historical_window(
            history_dataframe,
            available_contexts,
            used_contexts,
            mode,
        ),
        current_context=to_serializable(dict(current_context)),
        agents_executed=[
            "Aclim",
            "Ahid",
            "Afen",
            "Ageo",
            "Aprod",
            "Ahist",
            "AIEC",
            "ARG",
            "APS",
            "AMDH",
        ],
        evidences=evidences,
        agronomic_rules=agronomic_rules,
        predictive_result=predictive_result,
        semantic_inferences=[
            to_serializable(dict(item))
            for item in (semantic_inferences or [])
        ],
        consistency=consistency,
        decision=decision,
        warnings=warnings,
        metadata=to_serializable(dict(metadata or {})),
    )


def to_serializable(value: Any) -> Any:
    """Converte objetos do Hydros, pandas e NumPy para estruturas JSON."""

    if value is None or isinstance(value, (str, int, bool)):
        return value

    if isinstance(value, float):
        return value if math.isfinite(value) else None

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if is_dataclass(value):
        return to_serializable(asdict(value))

    if isinstance(value, Mapping):
        return {
            str(to_serializable(key)): to_serializable(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [to_serializable(item) for item in value]

    # Compatibilidade sem dependência obrigatória de NumPy/pandas.
    if hasattr(value, "item"):
        try:
            return to_serializable(value.item())
        except (ValueError, TypeError):
            pass

    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except (AttributeError, TypeError, ValueError):
            pass

    try:
        if math.isnan(value):
            return None
    except (TypeError, ValueError):
        pass

    return str(value)
