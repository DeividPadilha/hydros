"""
Teste dos cenários funcionais do Hydros.

Este teste executa diferentes históricos de contexto
para verificar se o modelo responde de forma coerente
em situações distintas de manejo hídrico.
"""

import pandas as pd

from src.services.hydros_engine import HydrosEngine


CENARIOS = {
    "cenario_01_baixa_criticidade.csv": {
        "descricao": "Baixa criticidade hídrica",
        "decisoes_esperadas": [
            "finalizar_irrigacao",
            "reduzir_irrigacao"
        ]
    },
    "cenario_02_moderado_manutencao.csv": {
        "descricao": "Criticidade moderada com irrigação ativa",
        "decisoes_esperadas": [
            "manter_irrigacao",
            "reduzir_irrigacao"
        ]
    },
    "cenario_03_alta_sem_irrigacao.csv": {
        "descricao": "Alta criticidade sem irrigação ativa",
        "decisoes_esperadas": [
            "iniciar_irrigacao"
        ]
    },
    "cenario_04_critico_com_irrigacao_ativa.csv": {
        "descricao": "Condição crítica com irrigação ativa",
        "decisoes_esperadas": [
            "aumentar_irrigacao"
        ]
    }
}


def executar_cenario(nome_arquivo, configuracao):
    """
    Executa um cenário de teste.
    """

    caminho = f"data/cenarios_teste/{nome_arquivo}"

    df = pd.read_csv(
        caminho
    )

    engine = HydrosEngine()

    resultados = engine.executar(
        df
    )

    decisao = resultados["amdh"]["D(Ui)"]
    score = resultados["amdh"]["score_hibrido"]

    ehc = resultados["aiec"]["Ehc"]
    earg = resultados["arg"]["Earg"]
    eaps = resultados["aps"]["Eaps"]

    esperadas = configuracao["decisoes_esperadas"]

    passou = decisao in esperadas

    print("\n----------------------------------------")
    print(f"Cenário: {nome_arquivo}")
    print(f"Descrição: {configuracao['descricao']}")
    print(f"Decisão esperada: {esperadas}")
    print(f"Decisão obtida: {decisao}")
    print(f"Ehc: {ehc}")
    print(f"Earg: {earg}")
    print(f"Eaps: {eaps}")
    print(f"Score: {score}")

    if passou:
        print("Status: OK")
    else:
        print("Status: VERIFICAR")

    return passou


def main():
    """
    Executa todos os cenários.
    """

    print("\n=== TESTE DE CENÁRIOS DO HYDROS ===")

    total = 0
    aprovados = 0

    for nome_arquivo, configuracao in CENARIOS.items():
        total += 1

        passou = executar_cenario(
            nome_arquivo,
            configuracao
        )

        if passou:
            aprovados += 1

    print("\n========================================")
    print(f"Cenários aprovados: {aprovados}/{total}")

    if aprovados == total:
        print("Resultado geral: TODOS OS CENÁRIOS ESTÃO COERENTES")
    else:
        print("Resultado geral: EXISTEM CENÁRIOS PARA AJUSTAR")


if __name__ == "__main__":
    main()
