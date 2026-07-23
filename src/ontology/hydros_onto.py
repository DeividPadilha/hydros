"""Integração operacional mínima da ontologia HydrosOnto.

A ontologia formal está descrita em ``ontology/hydros_onto.ttl`` e pode ser
aberta no Protégé. Este módulo fornece uma camada de inferência determinística
para o protótipo, permitindo que fatos do contexto agrícola sejam relacionados
às classes ``CondicaoAdequada``, ``CondicaoAtencao`` e ``CondicaoCritica``.

A implementação não pretende substituir um raciocinador OWL-DL completo. Ela
operacionaliza, de forma rastreável e reproduzível, as regras semânticas mínimas
necessárias ao fluxo atual do Hydros. Quando ``rdflib`` estiver instalado, o
arquivo Turtle também é validado sintaticamente; caso contrário, o motor usa
somente a biblioteca padrão do Python.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence
from uuid import uuid4

import pandas as pd


@dataclass(frozen=True)
class SemanticInference:
    """Resultado rastreável de uma inferência da HydrosOnto."""

    inference_id: str
    ontology: str
    ontology_version: str
    unit_id: str
    timestamp: str
    mode: str
    semantic_condition: str
    ontology_class: str
    internal_level: str
    confidence: float
    completeness: float
    rules_triggered: List[str] = field(default_factory=list)
    facts_used: Dict[str, Any] = field(default_factory=dict)
    explanation: str = ""
    backend: str = "lightweight_semantic_rules"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HydrosOnto:
    """Carrega o vocabulário da HydrosOnto e executa regras semânticas."""

    ONTOLOGY_VERSION = "0.1.0"

    REQUIRED_TOKENS: Sequence[str] = (
        "hydros:UnidadeManejo",
        "hydros:HistoricoContexto",
        "hydros:ContextoAgricola",
        "hydros:CondicaoAdequada",
        "hydros:CondicaoAtencao",
        "hydros:CondicaoCritica",
        "hydros:geraRecomendacao",
        "hydros:possuiHistoricoContexto",
    )

    def __init__(self, ontology_path: Optional[str | Path] = None) -> None:
        root = Path(__file__).resolve().parents[2]
        self.ontology_path = Path(
            ontology_path or root / "ontology" / "hydros_onto.ttl"
        )
        self.backend = "lightweight_semantic_rules"
        self.validation = self.validate_ontology()

    def validate_ontology(self) -> Dict[str, Any]:
        """Valida presença, vocabulário mínimo e, quando possível, Turtle."""

        if not self.ontology_path.exists():
            raise FileNotFoundError(
                f"Arquivo da HydrosOnto não encontrado: {self.ontology_path}"
            )

        text = self.ontology_path.read_text(encoding="utf-8")
        missing = [token for token in self.REQUIRED_TOKENS if token not in text]
        if missing:
            raise ValueError(
                "A HydrosOnto não contém o vocabulário mínimo: "
                + ", ".join(missing)
            )

        triples: Optional[int] = None
        syntax_validated = False
        try:
            from rdflib import Graph  # type: ignore

            graph = Graph()
            graph.parse(self.ontology_path, format="turtle")
            triples = len(graph)
            syntax_validated = True
            self.backend = "rdflib_plus_semantic_rules"
        except ImportError:
            pass
        except Exception as exc:  # pragma: no cover - depende do parser externo
            raise ValueError(f"Arquivo Turtle inválido: {exc}") from exc

        return {
            "path": str(self.ontology_path),
            "exists": True,
            "minimum_vocabulary_valid": True,
            "turtle_syntax_validated": syntax_validated,
            "triples": triples,
            "backend": self.backend,
        }

    def infer(self, dataframe: pd.DataFrame, mode: str) -> SemanticInference:
        """Classifica semanticamente a condição hídrica do contexto atual."""

        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("A HydrosOnto deve receber um DataFrame.")
        if dataframe.empty:
            raise ValueError("A HydrosOnto não pode inferir sobre dados vazios.")

        normalized_mode = str(mode).strip().lower()
        if normalized_mode not in {"historico", "instantaneo"}:
            raise ValueError(f"Modo semântico inválido: {mode}")

        current = dataframe.iloc[-1]
        window = dataframe.tail(5) if normalized_mode == "historico" else dataframe.tail(1)

        unit_id = self._first_text(current, "talhao", "unit_id", "unidade_manejo")
        timestamp = self._first_text(current, "data", "timestamp", "data_hora")

        rainfall_current = self._number(current.get("precipitacao"))
        rainfall_window = self._series_sum(window, "precipitacao")
        soil_moisture = self._number(current.get("umidade_solo"))
        available_water = self._number(current.get("agua_disponivel"))
        evapotranspiration = self._number(current.get("evapotranspiracao"))
        water_stress = self._normalize_stress(current.get("estresse_hidrico"))
        irrigation_applied = self._number(current.get("irrigacao_aplicada"))

        trend_water = self._trend(window, "agua_disponivel")
        trend_moisture = self._trend(window, "umidade_solo")

        required = {
            "precipitacao": rainfall_current,
            "umidade_solo": soil_moisture,
            "agua_disponivel": available_water,
            "evapotranspiracao": evapotranspiration,
            "estresse_hidrico": None if water_stress == "desconhecido" else water_stress,
        }
        available_count = sum(value is not None for value in required.values())
        completeness = available_count / len(required)

        facts = {
            "precipitacao_atual_mm": rainfall_current,
            "precipitacao_janela_mm": rainfall_window,
            "umidade_solo_pct": soil_moisture,
            "agua_disponivel_mm": available_water,
            "evapotranspiracao_mm": evapotranspiration,
            "estresse_hidrico": water_stress,
            "irrigacao_aplicada_mm": irrigation_applied,
            "tendencia_agua_disponivel": trend_water,
            "tendencia_umidade_solo": trend_moisture,
            "contextos_analisados": int(len(window)),
        }

        critical_rules: List[str] = []
        attention_rules: List[str] = []
        adequate_rules: List[str] = []

        if water_stress in {"alto", "critico"}:
            critical_rules.append("HO-R1: estresse hídrico alto ou crítico")
        if soil_moisture is not None and soil_moisture < 30.0:
            critical_rules.append("HO-R2: umidade do solo abaixo de 30%")
        if available_water is not None and available_water < 40.0:
            if evapotranspiration is not None and evapotranspiration >= 5.5:
                critical_rules.append(
                    "HO-R3: água disponível baixa com evapotranspiração elevada"
                )
        if (
            normalized_mode == "historico"
            and trend_water == "queda"
            and trend_moisture == "queda"
            and rainfall_window is not None
            and rainfall_window < 5.0
        ):
            critical_rules.append(
                "HO-R4: queda simultânea de água e umidade sem reposição recente"
            )

        if water_stress == "moderado":
            attention_rules.append("HO-R5: estresse hídrico moderado")
        if available_water is not None and 40.0 <= available_water < 65.0:
            attention_rules.append("HO-R6: água disponível em faixa de atenção")
        if soil_moisture is not None and 30.0 <= soil_moisture < 45.0:
            attention_rules.append("HO-R7: umidade do solo em faixa de atenção")
        if evapotranspiration is not None and evapotranspiration >= 4.5:
            if rainfall_window is not None and rainfall_window < 10.0:
                attention_rules.append(
                    "HO-R8: demanda evaporativa sem precipitação compensatória"
                )
        if normalized_mode == "historico" and (
            trend_water == "queda" or trend_moisture == "queda"
        ):
            attention_rules.append("HO-R9: tendência histórica de redução hídrica")

        adequate_prerequisites = [
            available_water is not None and available_water >= 65.0,
            soil_moisture is not None and soil_moisture >= 45.0,
            water_stress in {"baixo", "moderado", "desconhecido"},
        ]
        if all(adequate_prerequisites) and not critical_rules:
            adequate_rules.append("HO-R10: disponibilidade hídrica compatível")
        if rainfall_window is not None and rainfall_window >= 10.0:
            adequate_rules.append("HO-R11: precipitação recente relevante")

        if critical_rules:
            semantic_condition = "critica"
            ontology_class = "CondicaoCritica"
            internal_level = "critico"
            triggered = critical_rules + attention_rules
        elif attention_rules:
            semantic_condition = "atencao"
            ontology_class = "CondicaoAtencao"
            internal_level = "alto" if len(attention_rules) >= 3 else "moderado"
            triggered = attention_rules
        else:
            semantic_condition = "adequada"
            ontology_class = "CondicaoAdequada"
            internal_level = "baixo"
            triggered = adequate_rules or ["HO-R12: ausência de condição crítica ou de atenção"]

        # Confiança representa suporte dos dados e das regras, não criticidade.
        rule_support = min(1.0, 0.55 + 0.08 * len(triggered))
        history_support = 1.0 if normalized_mode == "historico" and len(window) >= 3 else 0.85
        confidence = self._clamp(0.65 * completeness + 0.25 * rule_support + 0.10 * history_support)

        explanation = (
            f"A HydrosOnto classificou o contexto como {semantic_condition} "
            f"pela aplicação de {len(triggered)} regra(s) semântica(s), "
            f"com completude {completeness:.2f}."
        )

        return SemanticInference(
            inference_id=str(uuid4()),
            ontology="HydrosOnto",
            ontology_version=self.ONTOLOGY_VERSION,
            unit_id=unit_id or "unidade_nao_informada",
            timestamp=timestamp or datetime.now(timezone.utc).isoformat(),
            mode=normalized_mode,
            semantic_condition=semantic_condition,
            ontology_class=ontology_class,
            internal_level=internal_level,
            confidence=round(confidence, 4),
            completeness=round(completeness, 4),
            rules_triggered=triggered,
            facts_used=facts,
            explanation=explanation,
            backend=self.backend,
        )

    @staticmethod
    def _number(value: Any) -> Optional[float]:
        if value is None or pd.isna(value):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def _series_sum(cls, dataframe: pd.DataFrame, column: str) -> Optional[float]:
        if column not in dataframe.columns:
            return None
        values = pd.to_numeric(dataframe[column], errors="coerce")
        if values.notna().sum() == 0:
            return None
        return float(values.sum())

    @classmethod
    def _trend(cls, dataframe: pd.DataFrame, column: str) -> str:
        if column not in dataframe.columns or len(dataframe) < 2:
            return "indisponivel"
        values = pd.to_numeric(dataframe[column], errors="coerce").dropna()
        if len(values) < 2:
            return "indisponivel"
        initial = float(values.iloc[0])
        final = float(values.iloc[-1])
        tolerance = max(0.01, abs(initial) * 0.01)
        if final < initial - tolerance:
            return "queda"
        if final > initial + tolerance:
            return "aumento"
        return "estavel"

    @staticmethod
    def _normalize_stress(value: Any) -> str:
        text = str(value if value is not None else "").strip().lower()
        aliases = {
            "crítico": "critico",
            "critica": "critico",
            "crítica": "critico",
            "alto": "alto",
            "alta": "alto",
            "moderada": "moderado",
            "médio": "moderado",
            "medio": "moderado",
            "baixo": "baixo",
            "baixa": "baixo",
            "não": "baixo",
            "nao": "baixo",
            "sim": "alto",
        }
        return aliases.get(text, text if text in {"baixo", "moderado", "alto", "critico"} else "desconhecido")

    @staticmethod
    def _first_text(row: Mapping[str, Any], *keys: str) -> str:
        for key in keys:
            value = row.get(key)
            if value is not None and not pd.isna(value) and str(value).strip():
                return str(value)
        return ""

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))
