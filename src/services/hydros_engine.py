#Orquestrador
# Importa os agentes do Hydros
from src.agents.agr_agent import AGRAgent
from src.agents.ahc_agent import AHCAgent
from src.agents.acl_agent import ACLAgent
from src.agents.amdh_agent import AMDHAgent


class HydrosEngine:
    """
    Motor principal do Hydros.

    Responsabilidade:
    centralizar a execução dos agentes.

    Assim o app.py fica responsável apenas pela interface,
    e este arquivo fica responsável pela lógica principal.
    """

    def executar(self, df):
        """
        Executa o fluxo completo de análise do Hydros.
        Recebe o histórico de contexto em formato DataFrame.
        """

        # Pega a última linha do CSV.
        # Essa linha representa o contexto agrícola mais recente.
        ultimo_contexto = df.iloc[-1].to_dict()

        # Executa o AGR.
        # O AGR aplica regras agronômicas sobre o contexto atual.
        agr = AGRAgent()
        # Executa o AGR usando o histórico recente do talhão
        resultado_agr = agr.avaliar(df)

        # Executa o AHC.
        # O AHC procura padrões e contextos semelhantes no histórico.
        ahc = AHCAgent()
        resultado_ahc = ahc.analisar(df)

        # Executa o ACL.
        # O ACL usa Random Forest para prever o risco hídrico.
        acl = ACLAgent()
        resultado_acl = acl.classificar(df)

        # Executa o AMDH.
        # O AMDH combina AGR, AHC e ACL para gerar a decisão final.
        amdh = AMDHAgent()
        resultado_amdh = amdh.decidir(
            resultado_agr,
            resultado_ahc,
            resultado_acl
        )

        # Retorna tudo organizado para o app.py mostrar no dashboard.
        return {
            "ultimo_contexto": ultimo_contexto,
            "agr": resultado_agr,
            "ahc": resultado_ahc,
            "acl": resultado_acl,
            "amdh": resultado_amdh
        }