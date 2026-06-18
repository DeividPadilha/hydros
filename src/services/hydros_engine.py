"""
Motor principal do Hydros.

Este serviço coordena o fluxo de execução do modelo Hydros.

Fluxo conceitual do modelo:

1. Recebe H(Ui), o histórico de contexto da unidade de manejo
2. Obtém C(t), o contexto agrícola mais recente
3. Executa os agentes especializados do histórico:
   Aclim, Ahid, Afen, Ageo, Aprod e Ahist
4. Executa o AIEC para gerar Ehc
5. Executa o agente de regras agronômicas para gerar Earg
6. Executa o agente preditivo supervisionado para gerar Eaps
7. Executa o AMDH para gerar D(Ui)

Nesta versão, os arquivos antigos ainda são mantidos para compatibilidade:
acl_agent.py representa temporariamente o APS
agr_agent.py representa temporariamente o ARG
"""

from src.agents.aclim_agent import AclimAgent
from src.agents.ahid_agent import AhidAgent
from src.agents.afen_agent import AfenAgent
from src.agents.ageo_agent import AgeoAgent
from src.agents.aprod_agent import AprodAgent
from src.agents.ahist_agent import AhistAgent
from src.agents.aiec_agent import AIECAgent

from src.agents.arg_agent import ARGAgent
from src.agents.acl_agent import ACLAgent
from src.agents.amdh_agent import AMDHAgent


class HydrosEngine:
    """
    Classe responsável por executar o fluxo principal do Hydros.
    """

    def __init__(self):
        """
        Inicializa todos os agentes utilizados pelo motor.
        """

        # Agentes especializados do histórico de contexto
        self.aclim = AclimAgent()
        self.ahid = AhidAgent()
        self.afen = AfenAgent()
        self.ageo = AgeoAgent()
        self.aprod = AprodAgent()
        self.ahist = AhistAgent()

        # Agente Integrador de Evidências Contextuais
        self.aiec = AIECAgent()

        # Agente de Regras Agronômicas
        # Nome antigo mantido temporariamente
        # Conceitualmente representa o ARG
        self.arg = ARGAgent()

        # Agente Preditivo Supervisionado
        # Nome antigo mantido temporariamente
        # Conceitualmente representa o APS
        self.aps = ACLAgent()

        # Agente Motor de Decisão Híbrido
        self.amdh = AMDHAgent()

    def executar(self, df):
        """
        Método principal chamado pelo app.py.

        Mantém compatibilidade com a interface atual do Streamlit.
        """
        return self.processar(df)

    def processar(self, df):
        """
        Executa o modelo Hydros sobre o histórico de contexto recebido.
        """

        # H(Ui): histórico de contexto da unidade de manejo
        historico_contexto = df

        # C(t): contexto mais recente do histórico
        contexto_atual = df.iloc[-1].to_dict()

        # 1. Executa agentes especializados do histórico de contexto
        resultado_aclim = self.aclim.analisar(
            historico_contexto
        )

        resultado_ahid = self.ahid.analisar(
            historico_contexto
        )

        resultado_afen = self.afen.analisar(
            historico_contexto
        )

        resultado_ageo = self.ageo.analisar(
            historico_contexto
        )

        resultado_aprod = self.aprod.analisar(
            historico_contexto
        )

        resultado_ahist = self.ahist.analisar(
            historico_contexto
        )

        # 2. Executa o AIEC
        # Gera Ehc a partir de Eclim, Ehid, Efen, Egeo, Eprod e Ehist
        resultado_aiec = self.aiec.integrar(
            resultado_aclim,
            resultado_ahid,
            resultado_afen,
            resultado_ageo,
            resultado_aprod,
            resultado_ahist
        )

        # 3. Executa o ARG
        # Nesta versão, o arquivo antigo agr_agent.py ainda é usado
        resultado_arg = self.arg.avaliar(
            historico_contexto
        )

        # Padroniza a saída do ARG para o modelo conceitual
        resultado_arg["agente_modelo"] = "ARG"
        resultado_arg["evidencia_nome"] = "Earg"
        resultado_arg["Earg"] = resultado_arg.get(
            "evidencia",
            resultado_arg.get("criticidade", "moderado")
        )

        # 4. Executa o APS
        # Nesta versão, o arquivo antigo acl_agent.py ainda é usado
        resultado_aps = self.aps.classificar(
            historico_contexto
        )

        # Padroniza a saída do APS para o modelo conceitual
        resultado_aps["agente_modelo"] = "APS"
        resultado_aps["evidencia_nome"] = "Eaps"
        resultado_aps["Eaps"] = resultado_aps.get(
            "evidencia",
            resultado_aps.get("criticidade", "moderado")
        )

        # 5. Executa o AMDH
        # Por enquanto, usamos a assinatura antiga do AMDH
        # Passando ARG, AIEC e APS nessa ordem
        resultado_amdh = self.amdh.decidir(
            resultado_arg,
            resultado_aiec,
            resultado_aps,
            contexto_atual
        )

        # Retorna todos os resultados
        # Mantemos chaves antigas para o app continuar funcionando
        return {
            "H(Ui)": "histórico de contexto representado pelo DataFrame de entrada",
            "C(t)": contexto_atual,
            "ultimo_contexto": contexto_atual,

            "aclim": resultado_aclim,
            "ahid": resultado_ahid,
            "afen": resultado_afen,
            "ageo": resultado_ageo,
            "aprod": resultado_aprod,
            "ahist": resultado_ahist,
            "ahc": resultado_ahist,

            "aiec": resultado_aiec,

            "arg": resultado_arg,
            "agr": resultado_arg,

            "aps": resultado_aps,
            "acl": resultado_aps,

            "amdh": resultado_amdh
        }




