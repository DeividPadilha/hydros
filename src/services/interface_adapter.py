"""Adaptador entre o núcleo científico do Hydros e a interface Streamlit.

O módulo mantém a interface desacoplada dos dicionários internos dos agentes,
centraliza rótulos de apresentação e garante que o banco receba o registro
integral de rastreabilidade produzido pelo ``HydrosEngine``.
"""

from __future__ import annotations

from hashlib import sha256
from typing import Any, Dict, Iterable, List, Mapping, Optional

from src.config.hydros_terms import DESCRICOES_DECISAO, VERSAO_ARQUITETURA
from src.database.database import Database


MODE_LABELS = {
    "historico": "Hydros Histórico",
    "instantaneo": "Hydros Instantâneo",
}

USER_STATUS_LABELS = {
    "nao_avaliada": "Não avaliada",
    "aceita": "Aceitar recomendação",
    "modificada": "Modificar recomendação",
    "rejeitada": "Rejeitar recomendação",
}

ACTION_LABELS = dict(DESCRICOES_DECISAO)


def compute_file_hash(content: bytes) -> str:
    """Retorna uma identificação curta e estável do arquivo analisado."""

    if not isinstance(content, (bytes, bytearray)):
        raise TypeError("O conteúdo do arquivo deve ser informado em bytes.")
    return sha256(bytes(content)).hexdigest()[:20]


def build_analysis_key(
    file_hash: str,
    algorithm: str,
    requested_mode: str,
) -> str:
    return f"{file_hash}:{algorithm}:{requested_mode}:{VERSAO_ARQUITETURA}"


def build_execution_view(result: Mapping[str, Any]) -> Dict[str, Any]:
    """Normaliza uma execução para apresentação e persistência."""

    trace = _mapping(result.get("registro_execucao"))
    decision = _mapping(trace.get("decision"))
    predictive = _mapping(trace.get("predictive_result"))
    consistency = _mapping(trace.get("consistency"))
    current_context = _mapping(trace.get("current_context"))
    metadata = _mapping(trace.get("metadata"))

    mode = str(trace.get("mode") or result.get("modo_execucao") or "nao_informado")
    action = str(
        decision.get("action")
        or _mapping(result.get("amdh")).get("decisao_final")
        or "nao_informada"
    )

    evidences = _mapping(trace.get("evidences"))
    semantic_inferences = trace.get("semantic_inferences") or []
    agronomic_rules = trace.get("agronomic_rules") or []

    return {
        "execution_id": str(trace.get("execution_id") or ""),
        "mode": mode,
        "mode_label": MODE_LABELS.get(mode, mode),
        "unit_id": str(
            trace.get("unit_id")
            or current_context.get("talhao")
            or "não informado"
        ),
        "analysis_timestamp": str(
            trace.get("analysis_timestamp")
            or current_context.get("data")
            or "não informado"
        ),
        "available_contexts": int(trace.get("available_contexts") or 0),
        "used_contexts": int(trace.get("used_contexts") or 0),
        "action": action,
        "action_label": ACTION_LABELS.get(action, action),
        "confidence": _float(decision.get("confidence")),
        "completeness": _float(decision.get("completeness")),
        "conflict_index": _float(decision.get("conflict_index")),
        "internal_condition": str(decision.get("internal_condition") or "não informada"),
        "semantic_condition": str(decision.get("semantic_condition") or "não informada"),
        "human_review_required": bool(decision.get("human_review_required", False)),
        "human_review_reasons": list(decision.get("human_review_reasons") or []),
        "governance_warnings": list(decision.get("governance_warnings") or []),
        "rationale": str(decision.get("rationale") or ""),
        "irrigation_state": str(decision.get("irrigation_state") or "desconhecida"),
        "irrigation_state_source": str(
            decision.get("irrigation_state_source") or "não informada"
        ),
        "irrigation_state_confidence": _float(
            decision.get("irrigation_state_confidence")
        ),
        "blocked_actions": list(decision.get("blocked_actions") or []),
        "class_scores": dict(_mapping(decision.get("class_scores"))),
        "evidence_summary": dict(_mapping(decision.get("evidence_summary"))),
        "evidences": dict(evidences),
        "evidence_count": len(evidences),
        "agronomic_rules": list(agronomic_rules),
        "semantic_inferences": list(semantic_inferences),
        "predictive_condition": str(
            predictive.get("predicted_condition") or "não informada"
        ),
        "aps_algorithm": str(predictive.get("algorithm") or "não informado"),
        "aps_model_version": str(
            predictive.get("model_version") or "não informada"
        ),
        "aps_scientific_status": str(
            predictive.get("scientific_status") or "não informado"
        ),
        "aps_domain_status": str(
            predictive.get("domain_status") or "não informado"
        ),
        "aps_domain_compatibility": _float(
            predictive.get("domain_compatibility")
        ),
        "aps_out_of_domain": bool(predictive.get("out_of_domain", False)),
        "aps_unknown_categories": predictive.get("unknown_categories") or [],
        "aps_warnings": list(predictive.get("warnings") or []),
        "aps_probabilities": dict(_mapping(predictive.get("probabilities"))),
        "aps_feature_importance": list(predictive.get("feature_importance") or []),
        "consistency": dict(consistency),
        "automatic_execution": bool(decision.get("automatic_execution", False)),
        "architecture_version": str(
            trace.get("architecture_version") or VERSAO_ARQUITETURA
        ),
        "ontology_integrated": bool(metadata.get("ontology_integrated", False)),
        "ontology_backend": str(metadata.get("ontology_backend") or "não informado"),
        "trace": dict(trace),
    }


def build_comparison_rows(
    results: Iterable[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for result in results:
        view = build_execution_view(result)
        rows.append(
            {
                "Modo": view["mode_label"],
                "Contextos usados": view["used_contexts"],
                "Decisão": view["action_label"],
                "Confiança": view["confidence"],
                "Completude": view["completeness"],
                "Conflito": view["conflict_index"],
                "Revisão especial": view["human_review_required"],
                "Domínio APS": view["aps_domain_status"],
                "Compatibilidade APS": view["aps_domain_compatibility"],
            }
        )
    return rows


def persist_execution(database: Database, result: Mapping[str, Any]) -> str:
    trace = _mapping(result.get("registro_execucao"))
    if not trace:
        raise ValueError("A execução não contém registro de rastreabilidade.")
    return database.salvar_registro_execucao(trace)


def register_user_evaluation(
    database: Database,
    execution_id: str,
    status: str,
    modified_action: Optional[str] = None,
    justification: Optional[str] = None,
) -> Dict[str, Any]:
    return database.registrar_avaliacao_usuario(
        execution_id=execution_id,
        status=status,
        acao_modificada=modified_action,
        justificativa=justification,
    )


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
