"""
Gerador de base sintética para treinamento do APS.

APS significa Agente Preditivo Supervisionado.

Este arquivo cria uma base simulada no padrão oficial do Hydros,
incluindo variáveis climáticas, hídricas, edáficas, fenológicas,
geográficas e produtivas.

Depois, essa base poderá ser substituída por dados do DSSAT,
sensores, IoT ou outras bases agrícolas.
"""

import random
import pandas as pd

from datetime import datetime, timedelta


# Quantidade de registros sintéticos que serão gerados
TOTAL_REGISTROS = 500


# Data inicial da série temporal
data_inicial = datetime(2026, 1, 1)


# Lista que armazenará os registros gerados
dados = []


# Cultura utilizada neste cenário sintético
cultura = "soja"


# Localização simplificada da unidade de manejo
# Evitamos vírgulas para não quebrar o CSV
loc = "Brasil_MT_Jaciara"


# Tipo de solo utilizado no cenário
solo = "argiloso"


# Lista de estágios fenológicos usados no treinamento
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

    # Variáveis climáticas
    precipitacao = random.randint(0, 35)
    temperatura = random.randint(24, 39)

    # Soma térmica simulada
    # Neste protótipo usamos um valor simples diário
    graus_dia = random.randint(16, 30)

    # Evapotranspiração simulada
    evapotranspiracao = round(
        random.uniform(2.5, 7.5),
        1
    )

    # Coeficiente de cultura simulado
    # Valores aproximados para representar variação fenológica
    coeficiente_cultura = round(
        random.uniform(0.70, 1.20),
        2
    )

    # Variáveis hídricas
    umidade_solo = random.randint(15, 85)
    agua_disponivel = random.randint(20, 130)
    irrigacao_aplicada = random.randint(0, 35)

    # Variável fenológica
    estagio_fenologico = random.choice(estagios_fenologicos)

    # Variável produtiva
    produtividade = random.randint(2200, 4600)

    # Regra sintética para gerar o alvo do treinamento
    # Essa regra ainda é provisória
    # Depois poderá ser substituída por dados reais ou simulados no DSSAT

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

    # Monta o registro no padrão oficial do Hydros
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


# Salva o CSV de treinamento no padrão Hydros
df.to_csv(
    "data/historico_treinamento_acl.csv",
    index=False
)


print("Base sintética do APS gerada com sucesso.")
print("Arquivo salvo em: data/historico_treinamento_acl.csv")