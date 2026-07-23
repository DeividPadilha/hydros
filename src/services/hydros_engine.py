"""Motor principal do Hydros.

Coordena o fluxo da arquitetura híbrida orientada por princípios de
Agentic AI:

H(Ui) -> agentes especializados -> AIEC -> Ehc
C(t), H(Ui) -> ARG -> Earg
C(t), H(Ui) -> APS -> Eaps
Ehc, Earg, Eaps -> AMDH -> D(Ui)

O motor oferece dois modos experimentais:

- historico: utiliza C(t) e H(Ui);
- instantaneo: utiliza somente C(t).

Além de manter todas as chaves usadas pela interface atual, o motor agora
gera ``registro_execucao`` e ``rastreabilidade`` em formato serializável.
Esses registros documentam agentes, evidências, regras, resultado preditivo,
confiança, completude, conflito, decisão e supervisão humana.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd

from src.agents.aclim_agent import AclimAgent
from src.agents.ahid_agent import AhidAgent
from src.agents.afen_agent import AfenAgent
from src.agents.ageo_agent import AgeoAgent
from src.agents.aprod_agent import AprodAgent
from src.agents.ahist_agent import AhistAgent
from src.agents.aiec_agent import AIECAgent
from src.agents.arg_agent import ARGAgent
from src.agents.aps_agent import APSAgent
from src.agents.amdh_agent import AMDHAgent
from src.config.hydros_terms import (
    MODO_EXECUCAO_PADRAO,
    MODOS_EXECUCAO,
    VERSAO_ARQUITETURA,
)
from src.core.contracts import build_execution_trace
from src.core.evidence_quality import enrich_agent_evidence
from src.core.irrigation_state import infer_irrigation_state
from src.ontology.hydros_onto import HydrosOnto


class HydrosEngine:
    """Executa o fluxo completo do modelo Hydros."""

    def __init__(
        self,
        algoritmo_aps: str = "random_forest",
        modo_execucao: str = MODO_EXECUCAO_PADRAO,
    ) -> None:
        self.aclim = AclimAgent()
        self.ahid = AhidAgent()
        self.afen = AfenAgent()
        self.ageo = AgeoAgent()
        self.aprod = AprodAgent()
        self.ahist = AhistAgent()

        self.aiec = AIECAgent()
        self.arg = ARGAgent()

        self.algoritmo_aps = algoritmo_aps
        self.aps = APSAgent(algoritmo=algoritmo_aps)
        self.amdh = AMDHAgent()
        self.hydros_onto = HydrosOnto()

        self.modo_execucao = self.validar_modo(modo_execucao)

    def executar(
        self,
        df: pd.DataFrame,
        modo_execucao: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mantém compatibilidade com a interface atual."""
        return self.processar(df, modo_execucao=modo_execucao)

    def processar(
        self,
        df: pd.DataFrame,
        modo_execucao: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Executa o Hydros no modo histórico ou instantâneo."""

        self.validar_dataframe(df)

        modo = self.validar_modo(
            modo_execucao if modo_execucao is not None else self.modo_execucao
        )

        historico_completo = df.copy()
        contexto_atual_df = historico_completo.tail(1).copy()
        contexto_atual = contexto_atual_df.iloc[-1].to_dict()

        # O estado operacional é tratado separadamente da lâmina aplicada.
        # Fontes que informam irrigacao_ativa possuem prioridade; na ausência
        # desse campo, o sistema registra que realizou uma inferência por
        # irrigacao_aplicada, sem ocultar essa aproximação.
        estado_irrigacao = infer_irrigation_state(contexto_atual)
        contexto_atual["irrigacao_ativa"] = estado_irrigacao.active
        contexto_atual["origem_estado_irrigacao"] = estado_irrigacao.source
        contexto_atual["confianca_estado_irrigacao"] = (
            estado_irrigacao.confidence
        )

        # No modo histórico, os agentes recebem H(Ui).
        # No modo instantâneo, recebem apenas C(t).
        dados_execucao = (
            historico_completo
            if modo == "historico"
            else contexto_atual_df
        )

        resultado_aclim = enrich_agent_evidence(
            self.aclim.analisar(dados_execucao),
            dados_execucao,
            "Aclim",
            modo,
        )
        resultado_ahid = enrich_agent_evidence(
            self.ahid.analisar(dados_execucao),
            dados_execucao,
            "Ahid",
            modo,
        )
        resultado_afen = enrich_agent_evidence(
            self.afen.analisar(dados_execucao),
            dados_execucao,
            "Afen",
            modo,
        )
        resultado_ageo = enrich_agent_evidence(
            self.ageo.analisar(dados_execucao),
            dados_execucao,
            "Ageo",
            modo,
        )
        resultado_aprod = enrich_agent_evidence(
            self.aprod.analisar(dados_execucao),
            dados_execucao,
            "Aprod",
            modo,
        )

        if modo == "historico":
            resultado_ahist = enrich_agent_evidence(
                self.ahist.analisar(historico_completo),
                historico_completo,
                "Ahist",
                modo,
            )
        else:
            resultado_ahist = enrich_agent_evidence(
                self.criar_evidencia_historica_desativada(),
                contexto_atual_df,
                "Ahist",
                modo,
            )

        resultado_aiec = self.aiec.integrar(
            resultado_aclim,
            resultado_ahid,
            resultado_afen,
            resultado_ageo,
            resultado_aprod,
            resultado_ahist,
        )
        resultado_aiec["modo_execucao"] = modo

        inferencia_semantica = self.hydros_onto.infer(
            dados_execucao,
            mode=modo,
        )
        inferencia_semantica_dict = inferencia_semantica.to_dict()

        resultado_arg = self.arg.avaliar(
            dados_execucao,
            semantic_inference=inferencia_semantica,
        )
        resultado_arg["agente_modelo"] = "ARG"
        resultado_arg["evidencia_nome"] = "Earg"
        resultado_arg["Earg"] = resultado_arg.get(
            "evidencia",
            resultado_arg.get("criticidade", "moderado"),
        )
        resultado_arg["modo_execucao"] = modo

        resultado_aps = self.aps.classificar(dados_execucao)
        resultado_aps["agente_modelo"] = "APS"
        resultado_aps["evidencia_nome"] = "Eaps"
        resultado_aps["Eaps"] = resultado_aps.get(
            "evidencia",
            resultado_aps.get("criticidade", "moderado"),
        )
        resultado_aps["modo_execucao"] = modo

        resultado_amdh = self.amdh.decidir(
            resultado_arg,
            resultado_aiec,
            resultado_aps,
            contexto_atual,
            estado_irrigacao=estado_irrigacao,
        )
        resultado_amdh["modo_execucao"] = modo
        resultado_amdh["contextos_utilizados"] = len(dados_execucao)

        resultados_agentes = {
            "aclim": resultado_aclim,
            "ahid": resultado_ahid,
            "afen": resultado_afen,
            "ageo": resultado_ageo,
            "aprod": resultado_aprod,
            "ahist": resultado_ahist,
            "aiec": resultado_aiec,
            "arg": resultado_arg,
            "aps": resultado_aps,
        }

        registro_execucao = build_execution_trace(
            mode=modo,
            architecture_version=VERSAO_ARQUITETURA,
            history_dataframe=historico_completo,
            current_context=contexto_atual,
            available_contexts=len(historico_completo),
            used_contexts=len(dados_execucao),
            agent_results=resultados_agentes,
            amdh_result=resultado_amdh,
            semantic_inferences=[inferencia_semantica_dict],
            metadata={
                "aps_algorithm": self.algoritmo_aps,
                "ontology_integrated": True,
                "ontology": "HydrosOnto",
                "ontology_version": inferencia_semantica_dict[
                    "ontology_version"
                ],
                "ontology_backend": inferencia_semantica_dict["backend"],
                "automatic_irrigation": False,
                "irrigation_state": estado_irrigacao.to_dict(),
            },
        ).to_dict()

        return {
            "modo_execucao": modo,
            "descricao_modo": MODOS_EXECUCAO[modo],
            "quantidade_contextos_disponiveis": len(historico_completo),
            "quantidade_contextos_utilizados": len(dados_execucao),
            "H(Ui)": (
                "histórico completo utilizado"
                if modo == "historico"
                else "histórico preservado, mas não utilizado na decisão"
            ),
            "C(t)": contexto_atual,
            "ultimo_contexto": contexto_atual,
            "estado_irrigacao": estado_irrigacao.to_dict(),
            "hydros_onto": inferencia_semantica_dict,
            "inferencias_semanticas": [inferencia_semantica_dict],
            "aclim": resultado_aclim,
            "ahid": resultado_ahid,
            "afen": resultado_afen,
            "ageo": resultado_ageo,
            "aprod": resultado_aprod,
            "ahist": resultado_ahist,
            "aiec": resultado_aiec,
            "arg": resultado_arg,
            "aps": resultado_aps,
            "amdh": resultado_amdh,
            # Novos contratos padronizados. As duas chaves apontam para o
            # mesmo conteúdo para facilitar o uso pela API, banco e artigo.
            "registro_execucao": registro_execucao,
            "rastreabilidade": registro_execucao,
        }

    @staticmethod
    def validar_modo(modo_execucao: str) -> str:
        modo = str(modo_execucao or "").strip().lower()

        aliases = {
            "histórico": "historico",
            "instantâneo": "instantaneo",
        }
        modo = aliases.get(modo, modo)

        if modo not in MODOS_EXECUCAO:
            modos_validos = ", ".join(sorted(MODOS_EXECUCAO.keys()))
            raise ValueError(
                f"Modo de execução inválido: {modo_execucao}. "
                f"Use um destes valores: {modos_validos}."
            )

        return modo

    @staticmethod
    def validar_dataframe(df: pd.DataFrame) -> None:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("A entrada do Hydros deve ser um DataFrame.")

        if df.empty:
            raise ValueError("O histórico de contexto não pode estar vazio.")

    @staticmethod
    def criar_evidencia_historica_desativada() -> Dict[str, Any]:
        """Produz uma evidência neutra e de peso efetivo zero."""

        return {
            "agente": "Ahist",
            "nome_agente": "Agente Histórico-Contextual",
            "evidencia_nome": "Ehist",
            "Ehist": "moderado",
            "evidencia": "moderado",
            "criticidade": "moderado",
            "score": 0.0,
            "confianca": 0.0,
            "completude": 0.0,
            "qualidade": 0.0,
            "desativado": True,
            "modo_execucao": "instantaneo",
            "variaveis_modelo": [],
            "indicadores": {
                "historico_utilizado": False,
                "quantidade_contextos": 0,
            },
            "regras_acionadas": [],
            "motivo": (
                "Ehist foi desativada porque o modo instantâneo utiliza "
                "somente o contexto atual C(t)."
            ),
        }
