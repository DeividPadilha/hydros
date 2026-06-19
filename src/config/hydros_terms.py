"""
Termos oficiais do modelo Hydros.

Este arquivo centraliza as terminologias, variáveis, evidências,
funções conceituais, regras e classes de decisão do modelo Hydros.

Objetivo:
evitar inconsistências no software, na interface e na documentação.

Base conceitual:
Capítulo 4 do modelo Hydros.
"""


# Nome do modelo computacional
MODELO = "Hydros"


# Estrutura formal do histórico de contexto
ESTRUTURA_CONTEXTO = {
    "unidade_manejo": "Uᵢ",
    "historico_contexto": "H(Uᵢ)",
    "contexto_temporal": "C(t)",
    "vetor_atributos": "Xₜ",
    "decisao_final": "D(Uᵢ)"
}


# Fórmulas conceituais do modelo
FORMULAS = {
    "historico_contexto": "H(Uᵢ) = {C(1), C(2), C(3), ..., C(n)}",
    "contexto_agricola": "C(t) = {loc, solo, p, temp, gd, et, kc, us, ad, irr, ef, eh, prod}",
    "estresse_hidrico": "EH = f(solo, ef, kc, ad, us, et)",
    "evidencia_agente": "Eᵢ = Aᵢ(H)",
    "conjunto_evidencias": "E = {Eclim, Ehid, Efen, Egeo, Eprod, Ehist}",
    "evidencia_contextual": "Ehc = AIEC(E)",
    "vetor_aps": "Xₜ = F(H(Uᵢ))",
    "evidencia_aps": "Eaps = M(Xₜ)",
    "evidencia_arg": "Earg = ARG(Xₜ, R)",
    "decisao_amdh": "D(Uᵢ) = φ(Ehc, Earg, Eaps)",
    "score_amdh": "Score = (whc × V(Ehc)) + (warg × V(Earg)) + (waps × V(Eaps))"
}


# Agentes centrais do modelo
AGENTES_CENTRAIS = {
    "AIEC": "Agente Integrador de Evidências Contextuais",
    "ARG": "Agente de Regras Agronômicas",
    "APS": "Agente Preditivo Supervisionado",
    "AMDH": "Agente Motor de Decisão Híbrido"
}


# Camada de agentes de histórico de contexto
CAMADA_AHC = {
    "AHC": "Agentes de Histórico de Contexto"
}


# Agentes especializados
AGENTES_ESPECIALIZADOS = {
    "Aclim": "Agente Climático",
    "Ahid": "Agente Hídrico",
    "Afen": "Agente Fenológico",
    "Ageo": "Agente Geográfico",
    "Aprod": "Agente Produtivo",
    "Ahist": "Agente Histórico-Contextual"
}


# Evidências dos agentes especializados
EVIDENCIAS_ESPECIALIZADAS = {
    "Eclim": "Evidência climática",
    "Ehid": "Evidência hídrica",
    "Efen": "Evidência fenológica",
    "Egeo": "Evidência geográfica",
    "Eprod": "Evidência produtiva",
    "Ehist": "Evidência histórico-contextual"
}


# Evidências principais usadas pelo motor híbrido
EVIDENCIAS_PRINCIPAIS = {
    "Ehc": "Evidência contextual consolidada",
    "Earg": "Evidência agronômica",
    "Eaps": "Evidência preditiva supervisionada"
}


# Níveis de criticidade usados no modelo
NIVEIS_CRITICIDADE = [
    "baixo",
    "moderado",
    "alto",
    "critico"
]


# Função V
# Converte criticidade textual em valor numérico
FUNCAO_V = {
    "baixo": 1,
    "moderado": 2,
    "alto": 3,
    "critico": 4
}


# Classes de decisão do AMDH
CLASSES_DECISAO = [
    "iniciar_irrigacao",
    "manter_irrigacao",
    "aumentar_irrigacao",
    "reduzir_irrigacao",
    "finalizar_irrigacao"
]


# Descrições das decisões
DESCRICOES_DECISAO = {
    "iniciar_irrigacao": "Iniciar irrigação",
    "manter_irrigacao": "Manter irrigação",
    "aumentar_irrigacao": "Aumentar irrigação",
    "reduzir_irrigacao": "Reduzir irrigação",
    "finalizar_irrigacao": "Finalizar irrigação"
}


# Variáveis formais do contexto C(t)
VARIAVEIS_MODELO = {
    "loc": "Localização geográfica",
    "solo": "Tipo de solo",
    "p": "Precipitação",
    "temp": "Temperatura média",
    "gd": "Graus-dia ou soma térmica",
    "et": "Evapotranspiração",
    "kc": "Coeficiente de cultura",
    "us": "Umidade do solo",
    "ad": "Água disponível no solo",
    "irr": "Irrigação aplicada",
    "ef": "Estágio fenológico",
    "eh": "Estresse hídrico",
    "prod": "Produtividade estimada"
}


# Variável adicional usada no software
# A cultura é citada no texto da proposta e mantida no protótipo
VARIAVEIS_ADICIONAIS_SOFTWARE = {
    "cultura": "Cultura agrícola analisada"
}


# Mapeamento entre nomes formais do modelo e colunas do CSV
MAPEAMENTO_CSV_MODELO = {
    "loc": "loc",
    "solo": "solo",
    "p": "precipitacao",
    "temp": "temperatura",
    "gd": "graus_dia",
    "et": "evapotranspiracao",
    "kc": "coeficiente_cultura",
    "us": "umidade_solo",
    "ad": "agua_disponivel",
    "irr": "irrigacao_aplicada",
    "ef": "estagio_fenologico",
    "eh": "estresse_hidrico",
    "prod": "produtividade",
    "cultura": "cultura"
}


# Regras agronômicas do ARG
REGRAS_ARG = {
    "r1": "Avalia a precipitação recente ou acumulada",
    "r2": "Avalia a disponibilidade de água no solo",
    "r3": "Avalia a umidade do solo",
    "r4": "Avalia o estágio fenológico e o coeficiente de cultura",
    "r5": "Avalia a evapotranspiração e a tendência de redução da água disponível",
    "r6": "Avalia a ocorrência de estresse hídrico",
    "r7": "Avalia os efeitos da irrigação aplicada anteriormente",
    "r8": "Avalia a tendência histórica da condição hídrica da unidade de manejo"
}


# Pesos iniciais do ARG
# Podem ser calibrados futuramente
PESOS_REGRAS_ARG = {
    "wr1": 0.12,
    "wr2": 0.16,
    "wr3": 0.16,
    "wr4": 0.14,
    "wr5": 0.14,
    "wr6": 0.14,
    "wr7": 0.07,
    "wr8": 0.07
}


# Pesos iniciais do AMDH
# Podem ser calibrados futuramente
PESOS_AMDH = {
    "whc": 0.40,
    "warg": 0.30,
    "waps": 0.30
}


# Limiares iniciais do AMDH
# Podem ser calibrados futuramente
LIMIARES_AMDH = {
    "alpha": 1.5,
    "beta": 2.3,
    "gamma": 3.0,
    "delta": 3.5
}


# Tecnologias e métodos citados no modelo
TECNOLOGIAS_METODOS = {
    "DSSAT": "Decision Support System for Agrotechnology Transfer",
    "IoT": "Internet das Coisas",
    "IA": "Inteligência Artificial",
    "ML": "Machine Learning ou Aprendizado de Máquina",
    "Random Forest": "Algoritmo supervisionado utilizado inicialmente pelo APS"
}

# Algoritmos disponíveis para o APS
# Random Forest permanece como algoritmo padrão
ALGORITMOS_APS = {
    "random_forest": "Random Forest",
    "gradient_boosting": "Gradient Boosting",
    "decision_tree": "Decision Tree"
}

ALGORITMO_APS_PADRAO = "random_forest"
