import streamlit as st
import pandas as pd
import plotly.express as px

from src.database.database import Database
from src.services.data_loader import DataLoader
from src.services.validator import CSVValidator
from src.services.hydros_engine import HydrosEngine


st.set_page_config(
    page_title="Hydros",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# Estilo visual do dashboard
# Para mudar a cor de fundo, altere bg-primary e bg-secondary
# Para mudar a cor dos cards, altere card
# Para mudar bordas e detalhes, altere border
st.markdown("""
<style>
    :root {
        /* CORES PRINCIPAIS */
        --bg-primary: #020f1f;
        --bg-secondary: #061f3d;
        --sidebar-bg: #020b16;
        --card: #08294a;
        --accent: #1e88e5;
        --accent-light: #38bdf8;
        --text-primary: #ffffff;
        --text-secondary: #c7d7e8;
        --border: #1e5f99;
        --success: #00e676;
    }

    .stApp {
        background: linear-gradient(135deg, var(--bg-primary), var(--bg-secondary));
        color: var(--text-primary);
    }

    header {
        background-color: var(--bg-primary) !important;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--sidebar-bg), #031a33);
        border-right: 1px solid var(--border);
    }

    section[data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
        opacity: 1 !important;
    }

    h1 {
        color: var(--text-primary);
        font-size: 3rem !important;
        font-weight: 800 !important;
    }

    h2, h3, label, p, div {
        color: var(--text-primary);
    }

    .block-container {
        padding-top: 2rem;
        max-width: 1150px;
    }

    [data-testid="stFileUploader"] {
        background-color: var(--card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.5rem;
        box-shadow: 0 6px 18px rgba(0,0,0,0.25);
    }

    [data-testid="stMetric"] {
        background-color: var(--card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.5rem;
        box-shadow: 0 6px 18px rgba(0,0,0,0.25);
    }

    [data-testid="stDataFrame"] {
        background-color: var(--card);
        border-radius: 12px;
        padding: 0.4rem;
    }

    .stAlert {
        border-radius: 12px;
        border: 1px solid var(--border);
    }

    hr {
        border: 1px solid rgba(255,255,255,0.25);
    }

    button[kind="header"] {
        background-color: #38bdf8 !important;
        color: white !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)


st.title("💧 Hydros")
st.subheader("Sistema Inteligente de Apoio Ã  Decisão Hídrica")


# Sidebar lateral do Hydros
# Aqui ficam informações rápidas da ferramenta
with st.sidebar:
    st.title("Hydros")

    st.markdown("---")

    st.write("Status do Sistema")
    st.success("Online")

    st.markdown("---")

    st.write("Arquitetura")
    st.write("AGR")
    st.write("AHC")
    st.write("ACL")
    st.write("AMDH")

    st.markdown("---")

    st.write("Modelo APS")
    st.info("Random Forest")

    st.markdown("---")

    st.write("Versão")
    st.write("0.1.0")


arquivo = st.file_uploader(
    "Carregue o histórico de contexto em CSV",
    type=["csv"]
)


if arquivo is not None:
    # Carrega o CSV enviado pelo usuário
    loader = DataLoader()
    df = loader.carregar_csv(arquivo)

    # Valida a estrutura mínima do CSV
    validator = CSVValidator()
    validacao = validator.validar(df)

    if not validacao["valido"]:
        st.error("CSV inválido.")
        for erro in validacao["erros"]:
            st.write(erro)
        st.stop()

    # Executa o núcleo do Hydros
    # Aqui o HydrosEngine chama Aclim, Ahid, Afen, Ageo, Aprod, Ahist, AIEC, ARG, APS e AMDH
    engine = HydrosEngine()
    resultados = engine.executar(df)

    ultimo_contexto = resultados["ultimo_contexto"]
    resultado_agr = resultados["agr"]
    resultado_ahc = resultados["ahc"]
    resultado_acl = resultados["acl"]
    resultado_amdh = resultados["amdh"]

    # Variáveis oficiais do modelo Hydros
    resultado_aclim = resultados["aclim"]
    resultado_ahid = resultados["ahid"]
    resultado_afen = resultados["afen"]
    resultado_ageo = resultados["ageo"]
    resultado_aprod = resultados["aprod"]
    resultado_ahist = resultados["ahist"]
    resultado_aiec = resultados["aiec"]
    resultado_arg = resultados["arg"]
    resultado_aps = resultados["aps"]

    # Compatibilidade temporária com nomes antigos
    resultado_agr = resultado_arg
    resultado_ahc = resultado_ahist
    resultado_acl = resultado_aps

    # Variáveis oficiais do modelo Hydros
    resultado_aclim = resultados["aclim"]
    resultado_ahid = resultados["ahid"]
    resultado_afen = resultados["afen"]
    resultado_ageo = resultados["ageo"]
    resultado_aprod = resultados["aprod"]
    resultado_ahist = resultados["ahist"]
    resultado_aiec = resultados["aiec"]
    resultado_arg = resultados["arg"]
    resultado_aps = resultados["aps"]

    # Compatibilidade temporária com nomes antigos
    resultado_agr = resultado_arg
    resultado_ahc = resultado_ahist
    resultado_acl = resultado_aps

    # Cria conexão com SQLite
    db = Database()

    # Evita salvar a mesma análise várias vezes no refresh da página
    # Se um novo CSV for enviado, libera novo salvamento
    arquivo_atual = arquivo.name

    if "ultimo_arquivo" not in st.session_state:
        st.session_state.ultimo_arquivo = arquivo_atual
        st.session_state.execucao_salva = False

    elif st.session_state.ultimo_arquivo != arquivo_atual:
        st.session_state.ultimo_arquivo = arquivo_atual
        st.session_state.execucao_salva = False

    if not st.session_state.execucao_salva:
        db.salvar_execucao(
            talhao=ultimo_contexto["talhao"],
            decisao_final=resultado_amdh["decisao_final"],
            confianca=resultado_amdh["confianca"],
            risco_previsto=resultado_aps["risco_previsto"],
            explicacao=resultado_amdh["explicacao"]
        )

        st.session_state.execucao_salva = True

    st.success("Análise concluída com sucesso.")

    # Resumo da análise atual
    st.subheader("Resumo da Análise")

    col_info1, col_info2, col_info3 = st.columns(3)

    with col_info1:
        st.metric(
            "Arquivo CSV",
            arquivo.name
        )

    with col_info2:
        st.metric(
            "Total de Registros",
            len(df)
        )

    with col_info3:
        st.metric(
            "Talhão Atual",
            ultimo_contexto["talhao"]
        )

    # Métricas principais da decisão
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Decisão Final",
            resultado_amdh["decisao_final"]
        )

        # Semáforo visual da decisão do AMDH
        decisao = resultado_amdh["decisao_final"]

        if decisao == "finalizar_irrigacao":
            st.success("🟢 Finalizar Irrigação")

        elif decisao == "reduzir_irrigacao":
            st.warning("🟡 Reduzir Irrigação")

        elif decisao == "manter_irrigacao":
            st.info("🔵 Manter Irrigação")

        elif decisao == "iniciar_irrigacao":
            st.warning("ðŸŸ  Iniciar Irrigação")

        elif decisao == "aumentar_irrigacao":
            st.error("🔴 Aumentar Irrigação")

    with col2:
        st.metric(
            "Confiança",
            f"{resultado_amdh['confianca'] * 100:.0f}%"
        )

    with col3:
        st.metric(
            "Risco Previsto",
            resultado_aps["risco_previsto"]
        )

    st.subheader("Explicação da Decisão")
    st.info(resultado_amdh["explicacao"])

    # Painel técnico dos agentes
    st.subheader("Painel Técnico dos Agentes")

    col_agr, col_ahc, col_acl, col_amdh = st.columns(4)

    with col_agr:
        st.write("AGR")
        st.metric(
            "Criticidade",
            resultado_agr.get("criticidade", "não informado")
        )
        st.metric(
            "Score Agronômico",
            resultado_agr.get("score_agronomico", 0)
        )
        st.metric(
            "Confiança",
            f"{resultado_agr.get('confianca', 0) * 100:.0f}%"
        )

    with col_ahc:
        st.write("AHC")
        st.metric(
            "Criticidade",
            resultado_ahc.get("criticidade", "não informado")
        )
        st.metric(
            "Score Histórico",
            resultado_ahc.get("score_historico", 0)
        )
        st.metric(
            "Contextos Similares",
            resultado_ahc.get("contextos_similares", 0)
        )

    with col_acl:
        st.write("ACL")
        st.metric(
            "Risco Previsto",
            resultado_acl.get("risco_previsto", "não informado")
        )
        st.metric(
            "Confiança",
            f"{resultado_acl.get('confianca', 0) * 100:.0f}%"
        )
        st.metric(
            "Modelo",
            resultado_acl.get("modelo", "não informado")
        )

    with col_amdh:
        st.write("AMDH")
        st.metric(
            "Score Híbrido",
            resultado_amdh.get("score_hibrido", 0)
        )
        st.metric(
            "Confiança",
            f"{resultado_amdh.get('confianca', 0) * 100:.0f}%"
        )
        st.metric(
            "Decisão",
            resultado_amdh.get("decisao_final", "não informado")
        )

    # Explicabilidade dos agentes
    st.subheader("Explicabilidade dos Agentes")

    col_exp_agr, col_exp_ahc, col_exp_acl = st.columns(3)

    with col_exp_agr:
        st.write("AGR")
        st.write("Regras acionadas:")

        regras_agr = resultado_agr.get("regras_acionadas", [])

        if regras_agr:
            for regra in regras_agr:
                st.write(f"✓ {regra}")
        else:
            st.write("Nenhuma regra crítica acionada.")

        st.write("Motivo:")
        st.info(resultado_agr.get("motivo", "sem motivo informado"))

    with col_exp_ahc:
        st.write("AHC")

        st.write("Tendência dos contextos:")
        st.info(resultado_ahc.get("tendencia_contextos", "não informado"))

        st.write("Tendência da umidade:")
        st.info(resultado_ahc.get("tendencia_umidade", "não informado"))

        st.write("Tendência da água disponível:")
        st.info(resultado_ahc.get("tendencia_agua_disponivel", "não informado"))

    with col_exp_acl:
        st.write("ACL")

        st.write("Evidência:")
        st.info(resultado_acl.get("evidencia", "não informado"))

        st.write("Features usadas:")

        features_acl = resultado_acl.get("features_usadas", [])

        if features_acl:
            for feature in features_acl:
                st.write(f"✓ {feature}")
        else:
            st.write("Features não informadas.")

    # Histórico de execuções salvas no banco
    st.subheader("Histórico de Execuções")

    historico_execucoes = db.listar_execucoes()

    # Atualiza a sidebar com dados reais da análise atual
    with st.sidebar:
        st.markdown("---")
        st.write("Análise Atual")

        st.write("CSV carregado:")
        st.info(arquivo.name)

        st.write("Talhão atual:")
        st.info(ultimo_contexto["talhao"])

        st.write("Execuções salvas:")
        st.info(len(historico_execucoes))

        st.write("Status do APS:")
        st.success("Modelo carregado")

    if historico_execucoes:
        df_historico = pd.DataFrame(
            historico_execucoes,
            columns=[
                "Data da Execução",
                "Talhão",
                "Decisão Final",
                "Confiança",
                "Risco Previsto",
                "Explicação"
            ]
        )

        st.dataframe(
            df_historico,
            use_container_width=True
        )
    else:
        st.info("Nenhuma execução salva ainda.")

    # Exibe o histórico de contexto carregado
    st.subheader("Histórico de Contexto")
    st.dataframe(
        df,
        use_container_width=True
    )

    # Gráficos do histórico
    st.subheader("Análise Visual do Histórico")

    grafico_umidade = px.line(
        df,
        x="data",
        y="umidade_solo",
        title="Evolução da Umidade do Solo"
    )

    grafico_umidade.update_layout(
        paper_bgcolor="#08294a",
        plot_bgcolor="#08294a",
        font_color="#ffffff"
    )

    grafico_precipitacao = px.bar(
        df,
        x="data",
        y="precipitacao",
        title="Histórico de Precipitação"
    )

    grafico_precipitacao.update_layout(
        paper_bgcolor="#08294a",
        plot_bgcolor="#08294a",
        font_color="#ffffff"
    )

    grafico_et = px.line(
        df,
        x="data",
        y="evapotranspiracao",
        title="Evapotranspiração"
    )

    grafico_et.update_layout(
        paper_bgcolor="#08294a",
        plot_bgcolor="#08294a",
        font_color="#ffffff"
    )

    grafico_temperatura = px.line(
        df,
        x="data",
        y="temperatura",
        title="Evolução da Temperatura"
    )

    grafico_temperatura.update_layout(
        paper_bgcolor="#08294a",
        plot_bgcolor="#08294a",
        font_color="#ffffff"
    )

    grafico_irrigacao = px.bar(
        df,
        x="data",
        y="irrigacao_aplicada",
        title="Irrigação Aplicada"
    )

    grafico_irrigacao.update_layout(
        paper_bgcolor="#08294a",
        plot_bgcolor="#08294a",
        font_color="#ffffff"
    )

    grafico_produtividade = px.line(
        df,
        x="data",
        y="produtividade",
        title="Produtividade Estimada"
    )

    grafico_produtividade.update_layout(
        paper_bgcolor="#08294a",
        plot_bgcolor="#08294a",
        font_color="#ffffff"
    )

    grafico_relacao = px.scatter(
        df,
        x="umidade_solo",
        y="evapotranspiracao",
        title="Relação entre Umidade do Solo e Evapotranspiração",
        hover_data=["data", "talhao", "estresse_hidrico"]
    )

    grafico_relacao.update_layout(
        paper_bgcolor="#08294a",
        plot_bgcolor="#08294a",
        font_color="#ffffff"
    )

    st.plotly_chart(grafico_umidade, use_container_width=True)
    st.plotly_chart(grafico_precipitacao, use_container_width=True)
    st.plotly_chart(grafico_et, use_container_width=True)
    st.plotly_chart(grafico_temperatura, use_container_width=True)
    st.plotly_chart(grafico_irrigacao, use_container_width=True)
    st.plotly_chart(grafico_produtividade, use_container_width=True)
    st.plotly_chart(grafico_relacao, use_container_width=True)

else:
    st.info("Aguardando carregamento do CSV.")


