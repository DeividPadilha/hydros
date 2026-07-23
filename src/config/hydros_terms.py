"""
Termos oficiais do modelo Hydros.

Este arquivo centraliza a terminologia, as fórmulas operacionais,
os agentes, as evidências, os modos de execução e os parâmetros
iniciais usados pelo protótipo.

A arquitetura do Hydros é híbrida e orientada por princípios de
Agentic AI. O sistema produz recomendações de manejo hídrico sob
supervisão humana e não executa automaticamente a irrigação.
"""

# -----------------------------------------------------------------------------
# Identificação do modelo
# -----------------------------------------------------------------------------

MODELO = "Hydros"
VERSAO_ARQUITETURA = "0.3.0-agentic"

DESCRICAO_ARQUITETURA = (
    "Arquitetura híbrida orientada por princípios de Agentic AI, "
    "com agentes especializados, memória contextual, integração de "
    "evidências, regras agronômicas, aprendizado supervisionado e "
    "supervisão humana."
)

# -----------------------------------------------------------------------------
# Estrutura formal do contexto
# -----------------------------------------------------------------------------

ESTRUTURA_CONTEXTO = {
    "unidade_manejo": "Uᵢ",
    "historico_contexto": "H(Uᵢ)",
    "contexto_temporal": "C(t)",
    "vetor_atributos": "Xₜ",
    "decisao_final": "D(Uᵢ)",
}

FORMULAS = {
    "historico_contexto": "H(Uᵢ) = {C(t₁), C(t₂), ..., C(tₙ)}",
    "contexto_agricola": (
        "C(t) = {loc, solo, p, temp, gd, et, kc, us, ad, "
        "irr, ef, eh, prod}"
    ),
    "estresse_hidrico": "EH = f(solo, ef, kc, ad, us, et)",
    "evidencia_agente": "Eⱼ(t) = Aⱼ(C(t), H(Uᵢ))",
    "conjunto_evidencias": (
        "E(t) = {Eclim, Ehid, Efen, Egeo, Eprod, Ehist}"
    ),
    "qualidade_evidencia": "Qⱼ = completudeⱼ × confiancaⱼ",
    "evidencia_contextual": (
        "Ehc = Σ(wⱼ × Qⱼ × V(Eⱼ)) / Σ(wⱼ × Qⱼ)"
    ),
    "vetor_aps": "Xₜ = F(C(t), H(Uᵢ))",
    "evidencia_aps": "Eaps = M(Xₜ)",
    "evidencia_arg": "Earg = ARG(Xₜ, R)",
    "score_amdh": (
        "S(d) = whc×Shc(d) + warg×Sarg(d) + "
        "waps×Saps(d) - Pconflito(d)"
    ),
    "decisao_amdh": "D(Uᵢ) = argmax_d S(d)",
    "revisao_humana": (
        "RH = 1 se confiança < τc ou completude < τq "
        "ou conflito > τf"
    ),
}

# -----------------------------------------------------------------------------
# Modos de execução usados no experimento
# -----------------------------------------------------------------------------

MODOS_EXECUCAO = {
    "historico": "Hydros Histórico: utiliza C(t) e H(Uᵢ)",
    "instantaneo": "Hydros Instantâneo: utiliza somente C(t)",
}

MODO_EXECUCAO_PADRAO = "historico"

# -----------------------------------------------------------------------------
# Agentes e evidências
# -----------------------------------------------------------------------------

AGENTES_CENTRAIS = {
    "AIEC": "Agente Integrador de Evidências Contextuais",
    "ARG": "Agente de Regras Agronômicas",
    "APS": "Agente Preditivo Supervisionado",
    "AMDH": "Agente Motor de Decisão Híbrido",
}

CAMADA_AHC = {
    "AHC": "Agentes de Histórico de Contexto",
}

AGENTES_ESPECIALIZADOS = {
    "Aclim": "Agente Climático",
    "Ahid": "Agente Hídrico",
    "Afen": "Agente Fenológico",
    "Ageo": "Agente Geográfico",
    "Aprod": "Agente Produtivo",
    "Ahist": "Agente Histórico-Contextual",
}

EVIDENCIAS_ESPECIALIZADAS = {
    "Eclim": "Evidência climática",
    "Ehid": "Evidência hídrica",
    "Efen": "Evidência fenológica",
    "Egeo": "Evidência geográfica",
    "Eprod": "Evidência produtiva",
    "Ehist": "Evidência histórico-contextual",
}

EVIDENCIAS_PRINCIPAIS = {
    "Ehc": "Evidência contextual consolidada",
    "Earg": "Evidência agronômica",
    "Eaps": "Evidência preditiva supervisionada",
}

# -----------------------------------------------------------------------------
# Criticidade e decisões
# -----------------------------------------------------------------------------

NIVEIS_CRITICIDADE = [
    "baixo",
    "moderado",
    "alto",
    "critico",
]

FUNCAO_V = {
    "baixo": 1,
    "moderado": 2,
    "alto": 3,
    "critico": 4,
}

CLASSES_DECISAO = [
    "iniciar_irrigacao",
    "manter_irrigacao",
    "aumentar_irrigacao",
    "reduzir_irrigacao",
    "finalizar_irrigacao",
]

DESCRICOES_DECISAO = {
    "iniciar_irrigacao": "Iniciar irrigação",
    "manter_irrigacao": "Manter irrigação",
    "aumentar_irrigacao": "Aumentar irrigação",
    "reduzir_irrigacao": "Reduzir irrigação",
    "finalizar_irrigacao": "Finalizar irrigação",
}

# Perfil de criticidade que oferece maior suporte a cada ação.
# Os valores usam a mesma escala interna de FUNCAO_V: baixo=1 e crítico=4.
ALVOS_CRITICIDADE_ACAO = {
    "finalizar_irrigacao": 1.00,
    "reduzir_irrigacao": 1.60,
    "manter_irrigacao": 2.25,
    "iniciar_irrigacao": 3.10,
    "aumentar_irrigacao": 4.00,
}

# Penalização aplicada aos escores das ações diante de conflito.
# Ações que alteram o manejo recebem penalização ligeiramente maior
# que a manutenção do estado atual.
PENALIDADES_CONFLITO_ACAO = {
    "finalizar_irrigacao": 0.04,
    "reduzir_irrigacao": 0.03,
    "manter_irrigacao": 0.01,
    "iniciar_irrigacao": 0.04,
    "aumentar_irrigacao": 0.05,
}

ACOES_VALIDAS_POR_ESTADO = {
    "ativa": [
        "finalizar_irrigacao",
        "reduzir_irrigacao",
        "manter_irrigacao",
        "aumentar_irrigacao",
    ],
    "inativa": [
        "manter_irrigacao",
        "iniciar_irrigacao",
    ],
    "desconhecida": list(CLASSES_DECISAO),
}

# Prioridade usada somente em empates numéricos. O comportamento conservador
# prioriza manter o estado atual antes de recomendar uma intervenção.
ORDEM_DESEMPATE_ACOES = [
    "manter_irrigacao",
    "iniciar_irrigacao",
    "aumentar_irrigacao",
    "reduzir_irrigacao",
    "finalizar_irrigacao",
]

# -----------------------------------------------------------------------------
# Variáveis do contexto
# -----------------------------------------------------------------------------

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
    "prod": "Produtividade estimada",
}

VARIAVEIS_ADICIONAIS_SOFTWARE = {
    "cultura": "Cultura agrícola analisada",
}

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
    "cultura": "cultura",
}

# -----------------------------------------------------------------------------
# Regras e pesos do ARG
# -----------------------------------------------------------------------------

REGRAS_ARG = {
    "r1": "Avalia a precipitação recente ou acumulada",
    "r2": "Avalia a disponibilidade de água no solo",
    "r3": "Avalia a umidade do solo",
    "r4": "Avalia o estágio fenológico e o coeficiente de cultura",
    "r5": (
        "Avalia a evapotranspiração e a tendência de redução "
        "da água disponível"
    ),
    "r6": "Avalia a ocorrência de estresse hídrico",
    "r7": "Avalia os efeitos da irrigação aplicada anteriormente",
    "r8": (
        "Avalia a tendência histórica da condição hídrica "
        "da unidade de manejo"
    ),
}

PESOS_REGRAS_ARG = {
    "wr1": 0.12,
    "wr2": 0.16,
    "wr3": 0.16,
    "wr4": 0.14,
    "wr5": 0.14,
    "wr6": 0.14,
    "wr7": 0.07,
    "wr8": 0.07,
}

# -----------------------------------------------------------------------------
# Pesos e limiares do AIEC e AMDH
# -----------------------------------------------------------------------------

PESOS_AIEC = {
    "Eclim": 0.18,
    "Ehid": 0.24,
    "Efen": 0.16,
    "Egeo": 0.10,
    "Eprod": 0.12,
    "Ehist": 0.20,
}

PESOS_AMDH = {
    "whc": 0.40,
    "warg": 0.30,
    "waps": 0.30,
}

LIMIARES_AMDH = {
    "alpha": 1.5,
    "beta": 2.3,
    "gamma": 2.3,
    "delta": 3.3,
    "confianca_minima": 0.60,
    "completude_minima": 0.70,
    "conflito_maximo": 0.45,
}

# -----------------------------------------------------------------------------
# Supervisão humana e rastreabilidade
# -----------------------------------------------------------------------------

POLITICA_SUPERVISAO = {
    "execucao_automatica_irrigacao": False,
    "decisao_final_humana": True,
    "permitir_aceitar": True,
    "permitir_modificar": True,
    "permitir_rejeitar": True,
}

CAMPOS_RASTREABILIDADE = [
    "modo_execucao",
    "agentes_executados",
    "evidencias_utilizadas",
    "pesos_utilizados",
    "confianca",
    "completude",
    "indice_conflito",
    "revisao_humana_requerida",
    "justificativa",
]

# -----------------------------------------------------------------------------
# DSSAT e avaliação experimental
# -----------------------------------------------------------------------------

BENCHMARKS = {
    "DSSAT": (
        "Benchmark externo de simulação agronômica usado para "
        "comparação experimental; não integra a arquitetura interna "
        "do Hydros."
    )
}

COLUNAS_COMPARACAO_DSSAT = [
    "data",
    "cenario_id",
    "decisao_dssat",
    "decisao_hydros_instantaneo",
    "decisao_hydros_historico",
    "irrigacao_dssat_mm",
    "irrigacao_hydros_instantaneo_mm",
    "irrigacao_hydros_historico_mm",
    "umidade_solo",
    "estresse_hidrico",
]

# -----------------------------------------------------------------------------
# Tecnologias e algoritmos
# -----------------------------------------------------------------------------

TECNOLOGIAS_METODOS = {
    "DSSAT": "Decision Support System for Agrotechnology Transfer",
    "IoT": "Internet das Coisas",
    "IA": "Inteligência Artificial",
    "Agentic AI": "Inteligência Artificial Agêntica",
    "ML": "Machine Learning ou Aprendizado de Máquina",
    "Random Forest": (
        "Algoritmo supervisionado utilizado inicialmente pelo APS"
    ),
}

ALGORITMOS_APS = {
    "random_forest": "Random Forest",
    "gradient_boosting": "Gradient Boosting",
    "decision_tree": "Decision Tree",
}

# Compatibilidade com o Agente Preditivo Supervisionado
ALGORITMOS_APS = {
    "random_forest": "Random Forest",
    "gradient_boosting": "Gradient Boosting",
    "decision_tree": "Decision Tree",
}

ALGORITMO_APS_PADRAO = "random_forest"
