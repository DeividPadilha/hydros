"""
Gerador de base sintÃ©tica para treinamento do APS.

APS significa Agente Preditivo Supervisionado.

Este arquivo cria uma base simulada no padrÃ£o oficial do Hydros,
incluindo variÃ¡veis climÃ¡ticas, hÃ­dricas, edÃ¡ficas, fenolÃ³gicas,
geogrÃ¡ficas e produtivas.

Depois, essa base poderÃ¡ ser substituÃ­da por dados do DSSAT,
sensores, IoT ou outras bases agrÃ­colas.
"""

import random
import pandas as pd

from datetime import datetime, timedelta


# Quantidade de registros sintÃ©ticos que serÃ£o gerados
TOTAL_REGISTROS = 500


# Data inicial da sÃ©rie temporal
data_inicial = datetime(2026, 1, 1)


# Lista que armazenarÃ¡ os registros gerados
dados = []


# Cultura utilizada neste cenÃ¡rio sintÃ©tico
cultura = "soja"


# LocalizaÃ§Ã£o simplificada da unidade de manejo
# Evitamos vÃ­rgulas para nÃ£o quebrar o CSV
loc = "Brasil_MT_Jaciara"


# Tipo de solo utilizado no cenÃ¡rio
solo = "argiloso"


# Lista de estÃ¡gios fenolÃ³gicos usados no treinamento
estagios_fenologicos = [
    "V3",
    "V4",
    "V5",
    "R1",
    "R2",
    "R3",
    "R4",
    "R5"
]


for i in range(TOTAL_REGISTROS):
    # Gera uma data sequencial
    data = data_inicial + timedelta(days=i)

    # VariÃ¡veis climÃ¡ticas
    precipitacao = random.randint(0, 35)
    temperatura = random.randint(24, 39)

    # Soma tÃ©rmica simulada
    # Neste protÃ³tipo usamos um valor simples diÃ¡rio
    graus_dia = random.randint(16, 30)

    # EvapotranspiraÃ§Ã£o simulada
    evapotranspiracao = round(
        random.uniform(2.5, 7.5),
        1
    )

    # Coeficiente de cultura simulado
    # Valores aproximados para representar variaÃ§Ã£o fenolÃ³gica
    coeficiente_cultura = round(
        random.uniform(0.70, 1.20),
        2
    )

    # VariÃ¡veis hÃ­dricas
    umidade_solo = random.randint(15, 85)
    agua_disponivel = random.randint(20, 130)
    irrigacao_aplicada = random.randint(0, 35)

    # VariÃ¡vel fenolÃ³gica
    estagio_fenologico = random.choice(estagios_fenologicos)

    # VariÃ¡vel produtiva
    produtividade = random.randint(2200, 4600)

    # Regra sintÃ©tica para gerar o alvo do treinamento
    # Essa regra ainda Ã© provisÃ³ria
    # Depois poderÃ¡ ser substituÃ­da por dados reais ou simulados no DSSAT

    if (
        umidade_solo < 30
        and agua_disponivel < 45
        and precipitacao < 5
        and evapotranspiracao > 5.5
    ):
        estresse_hidrico = "critico"

    elif (
        umidade_solo < 40
        and agua_disponivel < 65
        and evapotranspiracao > 5.0
    ):
        estresse_hidrico = "alto"

    elif (
        umidade_solo < 55
        or agua_disponivel < 85
    ):
        estresse_hidrico = "moderado"

    else:
        estresse_hidrico = "baixo"

    # Monta o registro no padrÃ£o oficial do Hydros
    dados.append({
        "data": data.strftime("%Y/%m/%d"),
        "talhao": "Talhao_01",
        "cultura": cultura,
        "loc": loc,
        "solo": solo,
        "precipitacao": precipitacao,
        "temperatura": temperatura,
        "graus_dia": graus_dia,
        "evapotranspiracao": evapotranspiracao,
        "coeficiente_cultura": coeficiente_cultura,
        "umidade_solo": umidade_solo,
        "agua_disponivel": agua_disponivel,
        "irrigacao_aplicada": irrigacao_aplicada,
        "estagio_fenologico": estagio_fenologico,
        "estresse_hidrico": estresse_hidrico,
        "produtividade": produtividade
    })


# Converte a lista de registros em DataFrame
df = pd.DataFrame(dados)


# Salva o CSV de treinamento no padrÃ£o Hydros
df.to_csv(
    "data/historico_treinamento_aps.csv",
    index=False
)


print("Base sintÃ©tica do APS gerada com sucesso.")
print("Arquivo salvo em: data/historico_treinamento_aps.csv")
