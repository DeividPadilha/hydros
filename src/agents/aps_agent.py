"""Agente Preditivo Supervisionado (APS) do Hydros.

O APS produz a evidência preditiva ``Eaps`` a partir do vetor de atributos
``Xt = F(H(Ui))``. Esta versão acrescenta controles necessários para uso
científico e rastreável do componente preditivo:

- identificação e versionamento do modelo carregado;
- detecção explícita de categorias não observadas no treinamento;
- verificação de compatibilidade numérica com o domínio de treinamento;
- ajuste da confiança pela compatibilidade do cenário;
- registro de valores imputados e avisos de uso fora do domínio;
- importância global dos atributos, sem apresentá-la como explicação local.

Categorias desconhecidas são codificadas como ``-1``. O APS continua
produzindo uma evidência para que o fluxo do Hydros não seja interrompido,
mas informa que a inferência deve ser interpretada com cautela. Nenhuma
categoria desconhecida é silenciosamente substituída por uma categoria do
conjunto de treinamento.
"""

from __future__ import annotations

from hashlib import sha256
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Mapping, Tuple

import joblib
import numpy as np
import pandas as pd

from src.config.hydros_terms import ALGORITMO_APS_PADRAO, ALGORITMOS_APS
from src.services.feature_extractor import FeatureExtractor


class APSAgent:
    """Agente Preditivo Supervisionado do modelo Hydros."""

    COLUNAS_CATEGORICAS = (
        "cultura",
        "loc",
        "solo",
        "estagio_fenologico",
    )

    def __init__(self, algoritmo: str = ALGORITMO_APS_PADRAO) -> None:
        self.nome_evidencia = "Eaps"

        if algoritmo not in ALGORITMOS_APS:
            algoritmo = ALGORITMO_APS_PADRAO

        self.algoritmo = algoritmo
        self.nome_modelo = ALGORITMOS_APS[algoritmo]
        self.extrator = FeatureExtractor()

        self.diretorio_modelos = Path(__file__).resolve().parents[1] / "models"
        self.caminhos_modelos = {
            "random_forest": self.diretorio_modelos
            / "aps_random_forest_model.pkl",
            "gradient_boosting": self.diretorio_modelos
            / "aps_gradient_boosting_model.pkl",
            "decision_tree": self.diretorio_modelos
            / "aps_decision_tree_model.pkl",
        }

        self.caminho_modelo = self.caminhos_modelos[self.algoritmo]
        if not self.caminho_modelo.exists():
            raise FileNotFoundError(
                f"Modelo APS não encontrado: {self.caminho_modelo}. "
                "Execute: python -m src.models.train_aps_model"
            )

        self.modelo = joblib.load(self.caminho_modelo)
        self.label_encoder = self._carregar("aps_label_encoder.pkl")
        self.features = list(self._carregar("aps_features.pkl"))

        self.encoders = {
            "cultura": self._carregar("aps_cultura_encoder.pkl"),
            "loc": self._carregar("aps_loc_encoder.pkl"),
            "solo": self._carregar("aps_solo_encoder.pkl"),
            "estagio_fenologico": self._carregar(
                "aps_fenologico_encoder.pkl"
            ),
        }

        self.metadata = self._carregar_metadata()
        self.hash_modelo = self._calcular_hash(self.caminho_modelo)
        self.versao_modelo = str(
            self.metadata.get("model_version", f"sha256:{self.hash_modelo}")
        )

    def _carregar(self, nome_arquivo: str) -> Any:
        caminho = self.diretorio_modelos / nome_arquivo
        if not caminho.exists():
            raise FileNotFoundError(f"Artefato APS não encontrado: {caminho}")
        return joblib.load(caminho)

    def _carregar_metadata(self) -> Dict[str, Any]:
        caminho = self.diretorio_modelos / "aps_model_metadata.json"
        if not caminho.exists():
            return {
                "schema_version": "1.0",
                "model_version": "aps-legacy-sem-metadados",
                "scientific_status": "modelo_legado_requer_retreinamento_temporal",
                "confidence_calibration": "nao_calibrada",
                "numeric_ranges": {},
                "feature_defaults": {},
                "known_limitations": [
                    "Metadados de treinamento não estavam disponíveis."
                ],
            }

        with caminho.open("r", encoding="utf-8") as stream:
            payload = json.load(stream)
        return payload if isinstance(payload, dict) else {}

    @staticmethod
    def _calcular_hash(caminho: Path) -> str:
        digest = sha256()
        with caminho.open("rb") as stream:
            for bloco in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(bloco)
        return digest.hexdigest()[:16]

    def classificar(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Classifica a condição hídrica e documenta o domínio da inferência."""

        if not isinstance(df, pd.DataFrame):
            raise TypeError("A entrada do APS deve ser um DataFrame.")
        if df.empty:
            raise ValueError("O histórico fornecido ao APS não pode estar vazio.")

        xt_original = self.extrator.extrair(df)
        xt_modelo = xt_original.copy()

        categorias_desconhecidas: Dict[str, Dict[str, Any]] = {}
        codificacao_categorias: Dict[str, Dict[str, Any]] = {}

        for coluna in self.COLUNAS_CATEGORICAS:
            valor_original = xt_modelo[coluna].iloc[0]
            codigo, detalhe = self.transformar_categoria_segura(
                self.encoders[coluna],
                valor_original,
            )
            # Substitui a coluna inteira para evitar conflito de dtype
            # com o backend Arrow do pandas (string -> inteiro).
            xt_modelo[coluna] = pd.Series(
                [codigo] * len(xt_modelo),
                index=xt_modelo.index,
                dtype="int64",
            )
            codificacao_categorias[coluna] = detalhe
            if not detalhe["conhecida"]:
                categorias_desconhecidas[coluna] = detalhe

        valores_imputados: Dict[str, Any] = {}
        features_ausentes: List[str] = []
        defaults = self.metadata.get("feature_defaults", {}) or {}

        for feature in self.features:
            if feature not in xt_modelo.columns:
                features_ausentes.append(feature)
                valor_padrao = defaults.get(feature, 0.0)
                xt_modelo[feature] = valor_padrao
                valores_imputados[feature] = valor_padrao
                continue

            valor = xt_modelo[feature].iloc[0]
            if self._valor_ausente(valor):
                valor_padrao = defaults.get(feature, -1 if feature in self.COLUNAS_CATEGORICAS else 0.0)
                # Substitui a coluna inteira para permitir mudança segura
                # de dtype quando o valor imputado for numérico.
                xt_modelo[feature] = pd.Series(
                    [valor_padrao] * len(xt_modelo),
                    index=xt_modelo.index,
                )
                valores_imputados[feature] = valor_padrao

        xt_modelo = xt_modelo[self.features].copy()
        for feature in self.features:
            xt_modelo[feature] = pd.to_numeric(
                xt_modelo[feature], errors="coerce"
            )
            if xt_modelo[feature].isna().any():
                valor_padrao = float(defaults.get(feature, 0.0))
                xt_modelo[feature] = xt_modelo[feature].fillna(valor_padrao)
                valores_imputados[feature] = valor_padrao

        fora_faixa_numerica = self._verificar_faixas_numericas(xt_original)
        completude = self._calcular_completude(
            total_features=len(self.features),
            features_ausentes=features_ausentes,
            valores_imputados=valores_imputados,
        )
        compatibilidade = self._calcular_compatibilidade_dominio(
            categorias_desconhecidas=categorias_desconhecidas,
            fora_faixa_numerica=fora_faixa_numerica,
            completude=completude,
        )
        status_dominio = self._classificar_status_dominio(compatibilidade)

        predicao = self.modelo.predict(xt_modelo)[0]
        probabilidades = self.modelo.predict_proba(xt_modelo)[0]
        eaps = str(self.label_encoder.inverse_transform([predicao])[0])

        confianca_bruta = float(np.max(probabilidades))
        confianca_ajustada = max(
            0.0,
            min(1.0, confianca_bruta * compatibilidade),
        )

        distribuicao_probabilidades = {
            str(classe): 0.0 for classe in self.label_encoder.classes_
        }
        for indice, classe_codificada in enumerate(self.modelo.classes_):
            classe_nome = str(
                self.label_encoder.inverse_transform([classe_codificada])[0]
            )
            distribuicao_probabilidades[classe_nome] = round(
                float(probabilidades[indice]), 6
            )

        avisos = self._gerar_avisos(
            categorias_desconhecidas=categorias_desconhecidas,
            fora_faixa_numerica=fora_faixa_numerica,
            features_ausentes=features_ausentes,
            valores_imputados=valores_imputados,
            status_dominio=status_dominio,
        )
        importancias = self._obter_importancias_globais()

        return {
            "agente": "APS",
            "agente_modelo": "APS",
            "nome_agente": "Agente Preditivo Supervisionado",
            "algoritmo": self.algoritmo,
            "modelo": self.nome_modelo,
            "versao_modelo": self.versao_modelo,
            "hash_modelo": self.hash_modelo,
            "status_cientifico_modelo": self.metadata.get(
                "scientific_status",
                "nao_informado",
            ),
            "calibracao_probabilidades": self.metadata.get(
                "confidence_calibration",
                "nao_informada",
            ),
            "evidencia_nome": self.nome_evidencia,
            "Eaps": eaps,
            "evidencia": eaps,
            "criticidade": eaps,
            "risco_previsto": eaps,
            "confianca": round(confianca_ajustada, 6),
            "confianca_bruta_modelo": round(confianca_bruta, 6),
            "confianca_ajustada_dominio": round(confianca_ajustada, 6),
            "completude": round(completude, 6),
            "qualidade": round(confianca_ajustada * completude, 6),
            "compatibilidade_dominio": round(compatibilidade, 6),
            "status_dominio": status_dominio,
            "fora_dominio": status_dominio == "fora_dominio",
            "uso_cientifico_restrito": status_dominio != "dentro_dominio",
            "categorias_desconhecidas": categorias_desconhecidas,
            "codificacao_categorias": codificacao_categorias,
            "features_ausentes": features_ausentes,
            "valores_imputados": valores_imputados,
            "features_fora_faixa": fora_faixa_numerica,
            "features_usadas": list(self.features),
            "probabilidades": distribuicao_probabilidades,
            "Xt": self._serializar_linha(xt_modelo.iloc[0].to_dict()),
            "Xt_original": self._serializar_linha(
                xt_original.iloc[0].to_dict()
            ),
            "importancia_atributos": importancias,
            "tipo_explicabilidade_aps": "importancia_global_do_modelo",
            "avisos": avisos,
            "revisao_humana_requerida": (
                status_dominio != "dentro_dominio"
                or confianca_ajustada < 0.60
                or completude < 0.90
            ),
            "metadata_treinamento": {
                "fonte": self.metadata.get("training_source"),
                "estrategia_divisao": self.metadata.get("training_split"),
                "distribuicao_alvo": self.metadata.get(
                    "target_distribution", {}
                ),
                "limitacoes_conhecidas": self.metadata.get(
                    "known_limitations", []
                ),
            },
            "motivo": (
                "classificação supervisionada baseada no vetor Xt extraído "
                "do histórico de contexto, com confiança ajustada pela "
                "compatibilidade do cenário ao domínio de treinamento"
            ),
        }

    def transformar_categoria_segura(
        self,
        encoder: Any,
        valor: Any,
    ) -> Tuple[int, Dict[str, Any]]:
        """Codifica uma categoria sem mascarar categorias desconhecidas."""

        valor_texto = str(valor)
        classes = [str(item) for item in encoder.classes_]
        conhecida = valor_texto in classes

        if conhecida:
            codigo = int(encoder.transform([valor_texto])[0])
        else:
            codigo = -1

        return codigo, {
            "valor_original": valor_texto,
            "codigo": codigo,
            "conhecida": conhecida,
            "categorias_treinamento": classes,
            "estrategia_desconhecida": (
                None if conhecida else "codigo_reservado_-1"
            ),
        }

    @staticmethod
    def _valor_ausente(valor: Any) -> bool:
        if valor is None:
            return True
        try:
            return bool(pd.isna(valor))
        except (TypeError, ValueError):
            return False

    def _verificar_faixas_numericas(
        self,
        xt_original: pd.DataFrame,
    ) -> Dict[str, Dict[str, float]]:
        ranges: Mapping[str, Any] = self.metadata.get("numeric_ranges", {}) or {}
        result: Dict[str, Dict[str, float]] = {}

        for feature, limites in ranges.items():
            if feature not in xt_original.columns:
                continue
            if not isinstance(limites, Mapping):
                continue

            try:
                value = float(xt_original[feature].iloc[0])
                minimum = float(limites["min"])
                maximum = float(limites["max"])
            except (KeyError, TypeError, ValueError):
                continue

            if not math.isfinite(value):
                continue
            if value < minimum or value > maximum:
                result[feature] = {
                    "valor": round(value, 6),
                    "min_treinamento": round(minimum, 6),
                    "max_treinamento": round(maximum, 6),
                }

        return result

    def _calcular_completude(
        self,
        *,
        total_features: int,
        features_ausentes: List[str],
        valores_imputados: Mapping[str, Any],
    ) -> float:
        if total_features <= 0:
            return 0.0
        affected = set(features_ausentes) | set(valores_imputados.keys())
        return max(0.0, 1.0 - len(affected) / total_features)

    def _calcular_compatibilidade_dominio(
        self,
        *,
        categorias_desconhecidas: Mapping[str, Any],
        fora_faixa_numerica: Mapping[str, Any],
        completude: float,
    ) -> float:
        categorical_total = len(self.COLUNAS_CATEGORICAS)
        categorical_score = 1.0 - (
            len(categorias_desconhecidas) / categorical_total
        )

        ranges = self.metadata.get("numeric_ranges", {}) or {}
        numeric_total = max(len(ranges), 1)
        numeric_score = 1.0 - min(
            1.0,
            len(fora_faixa_numerica) / numeric_total,
        )

        compatibility = (
            0.45 * categorical_score
            + 0.35 * numeric_score
            + 0.20 * completude
        )
        return max(0.0, min(1.0, compatibility))

    @staticmethod
    def _classificar_status_dominio(compatibilidade: float) -> str:
        if compatibilidade >= 0.85:
            return "dentro_dominio"
        if compatibilidade >= 0.55:
            return "parcialmente_fora_dominio"
        return "fora_dominio"

    def _obter_importancias_globais(self) -> List[Dict[str, Any]]:
        values: np.ndarray | None = None

        if hasattr(self.modelo, "feature_importances_"):
            values = np.asarray(self.modelo.feature_importances_, dtype=float)
        elif hasattr(self.modelo, "coef_"):
            coefficients = np.asarray(self.modelo.coef_, dtype=float)
            values = np.mean(np.abs(coefficients), axis=0)

        if values is None or len(values) != len(self.features):
            return []

        pairs = sorted(
            zip(self.features, values.tolist()),
            key=lambda item: float(item[1]),
            reverse=True,
        )
        return [
            {
                "atributo": feature,
                "importancia_global": round(float(value), 8),
            }
            for feature, value in pairs[:10]
        ]

    @staticmethod
    def _gerar_avisos(
        *,
        categorias_desconhecidas: Mapping[str, Any],
        fora_faixa_numerica: Mapping[str, Any],
        features_ausentes: List[str],
        valores_imputados: Mapping[str, Any],
        status_dominio: str,
    ) -> List[str]:
        warnings: List[str] = []

        if categorias_desconhecidas:
            columns = ", ".join(sorted(categorias_desconhecidas.keys()))
            warnings.append(
                "Categorias não observadas no treinamento: " + columns + "."
            )
        if fora_faixa_numerica:
            columns = ", ".join(sorted(fora_faixa_numerica.keys()))
            warnings.append(
                "Atributos numéricos fora da faixa de treinamento: "
                + columns
                + "."
            )
        if features_ausentes:
            warnings.append(
                "Features ausentes: " + ", ".join(sorted(features_ausentes)) + "."
            )
        if valores_imputados:
            warnings.append(
                "Foram imputados valores em: "
                + ", ".join(sorted(valores_imputados.keys()))
                + "."
            )
        if status_dominio != "dentro_dominio":
            warnings.append(
                "A evidência preditiva foi produzida fora ou parcialmente "
                "fora do domínio de treinamento e não deve ser interpretada "
                "isoladamente."
            )

        return warnings

    @staticmethod
    def _serializar_linha(payload: Mapping[str, Any]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in payload.items():
            if isinstance(value, np.generic):
                value = value.item()
            if isinstance(value, float) and not math.isfinite(value):
                value = None
            result[str(key)] = value
        return result
