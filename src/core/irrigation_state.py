"""Determinação explícita do estado operacional da irrigação.

O Hydros distingue a lâmina aplicada no contexto atual do estado operacional
utilizado pelo AMDH. Quando ``irrigacao_ativa`` é informado pela fonte de
dados, esse valor possui prioridade. Quando não existe informação explícita,
o protótipo utiliza ``irrigacao_aplicada`` como aproximação documentada.

Essa separação evita que o motor de decisão trate silenciosamente um volume
de água como se fosse um estado operacional conhecido com certeza absoluta.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class IrrigationState:
    """Estado operacional utilizado pelo AMDH."""

    active: Optional[bool]
    state: str
    source: str
    confidence: float
    applied_mm: Optional[float]
    explicit: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def infer_irrigation_state(
    current_context: Mapping[str, Any] | None,
) -> IrrigationState:
    """Obtém o estado da irrigação a partir do contexto atual.

    Ordem de prioridade:

    1. campo explícito ``irrigacao_ativa``;
    2. campo explícito equivalente em inglês;
    3. campo textual ``estado_irrigacao``;
    4. inferência documentada por ``irrigacao_aplicada``;
    5. estado desconhecido.
    """

    if current_context is None:
        return IrrigationState(
            active=None,
            state="desconhecida",
            source="contexto_ausente",
            confidence=0.0,
            applied_mm=None,
            explicit=False,
        )

    explicit_keys = (
        "irrigacao_ativa",
        "irrigation_active",
        "estado_irrigacao",
    )

    for key in explicit_keys:
        if key not in current_context:
            continue

        parsed = _parse_boolean_state(current_context.get(key))
        if parsed is None:
            continue

        applied_mm = _safe_optional_float(
            current_context.get("irrigacao_aplicada")
        )
        source = str(
            current_context.get(
                "origem_estado_irrigacao",
                f"campo_explicito:{key}",
            )
        )

        return IrrigationState(
            active=parsed,
            state="ativa" if parsed else "inativa",
            source=source,
            confidence=1.0,
            applied_mm=applied_mm,
            explicit=True,
        )

    if "irrigacao_aplicada" in current_context:
        applied_mm = _safe_optional_float(
            current_context.get("irrigacao_aplicada")
        )

        if applied_mm is not None:
            active = applied_mm > 0.0
            return IrrigationState(
                active=active,
                state="ativa" if active else "inativa",
                source="inferido_por_irrigacao_aplicada",
                confidence=0.70,
                applied_mm=applied_mm,
                explicit=False,
            )

    return IrrigationState(
        active=None,
        state="desconhecida",
        source="nao_informado",
        confidence=0.0,
        applied_mm=None,
        explicit=False,
    )


def _parse_boolean_state(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None

        if not math.isfinite(number):
            return None
        if number == 1.0:
            return True
        if number == 0.0:
            return False
        return None

    if value is None:
        return None

    text = str(value).strip().lower()
    true_values = {
        "1",
        "true",
        "sim",
        "ativa",
        "ativo",
        "ligada",
        "ligado",
        "on",
    }
    false_values = {
        "0",
        "false",
        "nao",
        "não",
        "inativa",
        "inativo",
        "desligada",
        "desligado",
        "off",
    }

    if text in true_values:
        return True
    if text in false_values:
        return False
    return None


def _safe_optional_float(value: Any) -> Optional[float]:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(number):
        return None
    return number
