"""Interface Streamlit do Hydros.

A interface permite executar o Hydros Histórico, o Hydros Instantâneo ou
comparar os dois modos, preservando a rastreabilidade integral e a decisão
final sob responsabilidade humana.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any, Dict, Mapping

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config.hydros_terms import VERSAO_ARQUITETURA
from src.database.database import Database
from src.services.hydros_engine import HydrosEngine
from src.services.interface_adapter import (
    ACTION_LABELS,
    MODE_LABELS,
    USER_STATUS_LABELS,
    build_analysis_key,
    build_comparison_rows,
    build_execution_view,
    compute_file_hash,
    persist_execution,
    register_user_evaluation,
)
from src.services.validator import CSVValidator


st.set_page_config(
    page_title="Hydros",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Estilo visual
# ---------------------------------------------------------------------------
# Evite seletores globais como "span", "div" ou "*" com cor branca.
# Eles também afetam os textos internos dos componentes do Streamlit,
# deixando texto branco sobre campos brancos.
st.markdown(
    """
    <style>
    :root {
        --hydros-bg-primary: #020f1f;
        --hydros-bg-secondary: #061f3d;
        --hydros-sidebar-primary: #020b16;
        --hydros-sidebar-secondary: #031a33;
        --hydros-card: #08294a;
        --hydros-card-soft: #0b355d;
        --hydros-border: #1e5f99;
        --hydros-text-primary: #ffffff;
        --hydros-text-secondary: #c7d7e8;
        --hydros-input-bg: #ffffff;
        --hydros-input-text: #0b1f33;
        --hydros-input-muted: #52677d;
        --hydros-focus: #ff4b4b;
    }

    /* Estrutura geral */
    .stApp {
        background:
            linear-gradient(
                135deg,
                var(--hydros-bg-primary),
                var(--hydros-bg-secondary)
            );
        color: var(--hydros-text-primary);
    }

    .block-container {
        padding-top: 1.6rem;
        max-width: 1250px;
    }

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                var(--hydros-sidebar-primary),
                var(--hydros-sidebar-secondary)
            );
        border-right: 1px solid var(--hydros-border);
    }

    /* Texto normal da aplicação e da barra lateral */
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp h5,
    .stApp h6,
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stMarkdownContainer"] li,
    .stApp [data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li {
        color: var(--hydros-text-primary) !important;
    }

    .stApp [data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: var(--hydros-text-secondary) !important;
    }

    /* Rótulos dos componentes */
    .stApp label,
    section[data-testid="stSidebar"] label,
    .stApp [data-testid="stWidgetLabel"] p,
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: var(--hydros-text-primary) !important;
        font-weight: 600;
    }

    /* Selectbox: campo fechado */
    div[data-baseweb="select"] > div {
        background-color: var(--hydros-input-bg) !important;
        border-color: #d7e1eb !important;
        color: var(--hydros-input-text) !important;
        min-height: 2.7rem;
    }

    div[data-baseweb="select"] > div:hover {
        border-color: var(--hydros-border) !important;
    }

    div[data-baseweb="select"] > div:focus-within {
        border-color: var(--hydros-focus) !important;
        box-shadow: 0 0 0 1px var(--hydros-focus) !important;
    }

    /* Todo texto e ícone interno do select */
    div[data-baseweb="select"] > div *,
    div[data-baseweb="select"] svg {
        color: var(--hydros-input-text) !important;
        fill: var(--hydros-input-text) !important;
        opacity: 1 !important;
    }

    /* Dropdown do selectbox, renderizado fora da sidebar */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    ul[role="listbox"],
    div[role="listbox"] {
        background-color: var(--hydros-input-bg) !important;
    }

    div[data-baseweb="popover"] *,
    ul[role="listbox"] *,
    div[role="listbox"] * {
        color: var(--hydros-input-text) !important;
        opacity: 1 !important;
    }

    li[role="option"],
    div[role="option"] {
        background-color: var(--hydros-input-bg) !important;
        color: var(--hydros-input-text) !important;
    }

    li[role="option"]:hover,
    div[role="option"]:hover,
    li[role="option"][aria-selected="true"],
    div[role="option"][aria-selected="true"] {
        background-color: #e8f1f8 !important;
        color: var(--hydros-input-text) !important;
    }

    /* Inputs e áreas de texto */
    input,
    textarea,
    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div {
        background-color: var(--hydros-input-bg) !important;
        color: var(--hydros-input-text) !important;
        border-color: #d7e1eb !important;
    }

    input::placeholder,
    textarea::placeholder {
        color: var(--hydros-input-muted) !important;
        opacity: 1 !important;
    }

    input:focus,
    textarea:focus,
    [data-baseweb="input"] > div:focus-within,
    [data-baseweb="textarea"] > div:focus-within {
        border-color: var(--hydros-focus) !important;
        box-shadow: 0 0 0 1px var(--hydros-focus) !important;
    }

    /* Arquivo carregado e área de upload */
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploaderDropzone"] {
        background-color: #f4f7fb !important;
        border-color: #d7e1eb !important;
    }

    [data-testid="stFileUploader"] section *,
    [data-testid="stFileUploaderDropzone"] *,
    [data-testid="stFileUploaderFile"] *,
    [data-testid="stFileUploaderFileName"],
    [data-testid="stFileUploader"] small {
        color: var(--hydros-input-text) !important;
        opacity: 1 !important;
    }

    [data-testid="stFileUploader"] button {
        background-color: #e8eef5 !important;
        color: var(--hydros-input-text) !important;
        border: 1px solid #c8d4df !important;
    }

    /* Código exibido com st.code */
    [data-testid="stCodeBlock"],
    [data-testid="stCodeBlock"] pre,
    [data-testid="stCodeBlock"] code,
    [data-testid="stCode"] {
        background-color: var(--hydros-card) !important;
        color: var(--hydros-text-primary) !important;
        border-color: var(--hydros-border) !important;
    }

    [data-testid="stCodeBlock"] * {
        color: var(--hydros-text-primary) !important;
        opacity: 1 !important;
    }

    /* Métricas e tabelas */
    [data-testid="stMetric"],
    [data-testid="stDataFrame"] {
        background-color: var(--hydros-card);
        border: 1px solid var(--hydros-border);
        border-radius: 12px;
        padding: 0.55rem;
    }

    [data-testid="stMetric"] *,
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {
        color: var(--hydros-text-primary) !important;
    }

    /* Abas */
    button[data-baseweb="tab"] {
        color: var(--hydros-text-secondary) !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--hydros-text-primary) !important;
        border-bottom-color: var(--hydros-focus) !important;
    }

    /* Botões */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }

    .stButton > button[kind="primary"] {
        background-color: var(--hydros-focus) !important;
        color: #ffffff !important;
        border-color: var(--hydros-focus) !important;
    }

    .stButton > button[kind="primary"] * {
        color: #ffffff !important;
    }

    /* Alertas e expansores */
    .stAlert {
        border-radius: 12px;
    }

    [data-testid="stExpander"] {
        background-color: rgba(8, 41, 74, 0.65);
        border: 1px solid var(--hydros-border);
        border-radius: 10px;
    }

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary * {
        color: var(--hydros-text-primary) !important;
    }

    /* Linha divisória da sidebar */
    section[data-testid="stSidebar"] hr {
        border-color: rgba(199, 215, 232, 0.18) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


ALGORITHM_OPTIONS = {
    "Random Forest": "random_forest",
    "Gradient Boosting": "gradient_boosting",
    "Decision Tree": "decision_tree",
}

MODE_OPTIONS = {
    "Hydros Histórico": "historico",
    "Hydros Instantâneo": "instantaneo",
    "Comparar os dois modos": "comparar",
}


def _pct(value: Any) -> str:
    try:
        return f"{float(value) * 100:.1f}%"
    except (TypeError, ValueError):
        return "0,0%"


def _action_message(action: str) -> None:
    label = ACTION_LABELS.get(action, action)
    if action == "finalizar_irrigacao":
        st.success(f"🟢 {label}")
    elif action == "reduzir_irrigacao":
        st.warning(f"🟡 {label}")
    elif action == "manter_irrigacao":
        st.info(f"🔵 {label}")
    elif action == "iniciar_irrigacao":
        st.warning(f"🟠 {label}")
    elif action == "aumentar_irrigacao":
        st.error(f"🔴 {label}")
    else:
        st.write(label)


def _evidence_rows(view: Mapping[str, Any]) -> pd.DataFrame:
    rows = []
    for key, payload in view.get("evidences", {}).items():
        if not isinstance(payload, Mapping):
            continue
        rows.append(
            {
                "Componente": payload.get("agent", key),
                "Evidência": payload.get("evidence_name", ""),
                "Nível interno": payload.get("internal_level", ""),
                "Condição semântica": payload.get("semantic_condition", ""),
                "Confiança": payload.get("confidence", 0.0),
                "Completude": payload.get("completeness", 0.0),
                "Qualidade": payload.get("quality", 0.0),
                "Ativa": payload.get("active", True),
            }
        )
    return pd.DataFrame(rows)


def _show_evaluation_form(
    database: Database,
    view: Mapping[str, Any],
    key_prefix: str,
) -> None:
    st.subheader("Avaliação humana da recomendação")
    st.caption(
        "O Hydros não aciona automaticamente a irrigação. A decisão operacional "
        "permanece sob responsabilidade do usuário."
    )

    status_label = st.selectbox(
        "Avaliação",
        list(USER_STATUS_LABELS.values())[1:],
        key=f"{key_prefix}_status",
    )
    reverse_status = {
        label: key for key, label in USER_STATUS_LABELS.items()
    }
    status = reverse_status[status_label]

    modified_action = None
    if status == "modificada":
        action_label = st.selectbox(
            "Ação definida pelo usuário",
            list(ACTION_LABELS.values()),
            key=f"{key_prefix}_action",
        )
        reverse_action = {
            label: key for key, label in ACTION_LABELS.items()
        }
        modified_action = reverse_action[action_label]

    justification = st.text_area(
        "Justificativa do usuário",
        key=f"{key_prefix}_justification",
        placeholder=(
            "Registre o motivo da aceitação, modificação ou rejeição."
        ),
    )

    if st.button(
        "Registrar avaliação",
        key=f"{key_prefix}_submit",
    ):
        updated = register_user_evaluation(
            database=database,
            execution_id=str(view["execution_id"]),
            status=status,
            modified_action=modified_action,
            justification=justification,
        )
        final_status = USER_STATUS_LABELS.get(
            updated["status_usuario"],
            updated["status_usuario"],
        )
        st.success(
            f"Avaliação registrada. Status final: {final_status}."
        )


def _show_execution(
    result: Mapping[str, Any],
    database: Database,
    key_prefix: str,
) -> None:
    view = build_execution_view(result)

    st.markdown(f"## {view['mode_label']}")
    summary_cols = st.columns(5)
    summary_cols[0].metric("Unidade de manejo", view["unit_id"])
    summary_cols[1].metric(
        "Contextos utilizados",
        view["used_contexts"],
    )
    summary_cols[2].metric(
        "Confiança",
        _pct(view["confidence"]),
    )
    summary_cols[3].metric(
        "Completude",
        _pct(view["completeness"]),
    )
    summary_cols[4].metric(
        "Conflito",
        _pct(view["conflict_index"]),
    )

    decision_cols = st.columns([1, 1, 1])
    with decision_cols[0]:
        st.metric("Decisão D(Uᵢ)", view["action_label"])
        _action_message(view["action"])
    with decision_cols[1]:
        st.metric(
            "Condição semântica",
            view["semantic_condition"],
        )
        st.metric(
            "Estado da irrigação",
            view["irrigation_state"],
        )
    with decision_cols[2]:
        review_text = (
            "Sim" if view["human_review_required"] else "Não"
        )
        st.metric("Revisão especial", review_text)
        st.metric("Domínio do APS", view["aps_domain_status"])

    if view["human_review_required"]:
        st.warning(
            "Revisão especial requerida: "
            + "; ".join(view["human_review_reasons"])
        )

    if view["governance_warnings"]:
        st.info(
            "Avisos de governança: "
            + "; ".join(view["governance_warnings"])
        )

    st.subheader("Explicação da decisão")
    st.info(
        view["rationale"]
        or "A execução não forneceu justificativa textual."
    )

    tabs = st.tabs(
        [
            "Evidências",
            "Regras e ontologia",
            "APS",
            "Escores das ações",
            "Rastreabilidade",
        ]
    )

    with tabs[0]:
        evidence_df = _evidence_rows(view)
        if evidence_df.empty:
            st.info("Nenhuma evidência foi registrada.")
        else:
            st.dataframe(
                evidence_df,
                use_container_width=True,
                hide_index=True,
            )

    with tabs[1]:
        st.write("Regras agronômicas acionadas")
        if view["agronomic_rules"]:
            for rule in view["agronomic_rules"]:
                st.write(f"✓ {rule}")
        else:
            st.write("Nenhuma regra agronômica registrada.")

        st.write("Inferências da HydrosOnto")
        if view["semantic_inferences"]:
            st.json(view["semantic_inferences"])
        else:
            st.write("Nenhuma inferência semântica registrada.")

    with tabs[2]:
        aps_cols = st.columns(4)
        aps_cols[0].metric("Algoritmo", view["aps_algorithm"])
        aps_cols[1].metric("Versão", view["aps_model_version"])
        aps_cols[2].metric(
            "Compatibilidade do domínio",
            _pct(view["aps_domain_compatibility"]),
        )
        aps_cols[3].metric(
            "Condição prevista",
            view["predictive_condition"],
        )

        st.write("Status científico")
        st.code(view["aps_scientific_status"])

        if view["aps_warnings"]:
            for warning in view["aps_warnings"]:
                st.warning(warning)

        st.write("Probabilidades")
        st.json(view["aps_probabilities"])

        st.write("Importância global dos atributos")
        st.json(view["aps_feature_importance"])

    with tabs[3]:
        scores = view["class_scores"]
        if scores:
            score_df = pd.DataFrame(
                [
                    {
                        "Ação": ACTION_LABELS.get(action, action),
                        "Escore S(d)": score,
                        "Bloqueada": (
                            action in view["blocked_actions"]
                        ),
                    }
                    for action, score in scores.items()
                ]
            ).sort_values(
                "Escore S(d)",
                ascending=False,
            )

            st.dataframe(
                score_df,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Escores por ação não informados.")

    with tabs[4]:
        st.write(
            "Identificador da execução: "
            f"`{view['execution_id']}`"
        )
        st.write(
            f"Arquitetura: `{view['architecture_version']}`"
        )
        st.write(
            f"Instante analisado: `{view['analysis_timestamp']}`"
        )
        st.write(
            f"Evidências registradas: `{view['evidence_count']}`"
        )
        st.json(view["trace"])

    _show_evaluation_form(
        database,
        view,
        key_prefix,
    )


def _show_context_charts(df: pd.DataFrame) -> None:
    st.subheader("Evolução do histórico de contexto")

    chart_specs = [
        (
            "umidade_solo",
            "Evolução da umidade do solo",
            "line",
        ),
        (
            "precipitacao",
            "Precipitação",
            "bar",
        ),
        (
            "evapotranspiracao",
            "Evapotranspiração",
            "line",
        ),
        (
            "temperatura",
            "Temperatura",
            "line",
        ),
        (
            "irrigacao_aplicada",
            "Irrigação aplicada",
            "bar",
        ),
        (
            "produtividade",
            "Produtividade estimada",
            "line",
        ),
    ]

    available = [
        (column, title, kind)
        for column, title, kind in chart_specs
        if column in df.columns
    ]

    for start in range(0, len(available), 2):
        columns = st.columns(2)
        specifications = available[start : start + 2]

        for target, specification in zip(columns, specifications):
            column, title, kind = specification
            with target:
                if kind == "bar":
                    chart = px.bar(
                        df,
                        x="data",
                        y=column,
                        title=title,
                    )
                else:
                    chart = px.line(
                        df,
                        x="data",
                        y=column,
                        title=title,
                    )

                chart.update_layout(
                    paper_bgcolor="#08294a",
                    plot_bgcolor="#08294a",
                    font_color="#ffffff",
                )
                st.plotly_chart(
                    chart,
                    use_container_width=True,
                )


st.title("💧 Hydros")
st.subheader(
    "Modelo inteligente de apoio ao gerenciamento hídrico"
)
st.caption(
    "Arquitetura híbrida orientada por princípios de Agentic AI, "
    "com memória temporal, agentes especializados, regras "
    "agronômicas, HydrosOnto, APS e supervisão humana."
)

with st.sidebar:
    st.title("Configuração")

    requested_mode_label = st.selectbox(
        "Modo de execução",
        list(MODE_OPTIONS.keys()),
    )
    requested_mode = MODE_OPTIONS[requested_mode_label]

    algorithm_label = st.selectbox(
        "Algoritmo do APS",
        list(ALGORITHM_OPTIONS.keys()),
    )
    algorithm = ALGORITHM_OPTIONS[algorithm_label]

    st.divider()

    st.write("Arquitetura")
    st.code(VERSAO_ARQUITETURA)

    st.write("Agentes")
    st.write("Aclim · Ahid · Afen · Ageo · Aprod · Ahist")
    st.write("AIEC · ARG · APS · AMDH")

    st.divider()

    st.warning(
        "O Hydros recomenda; não aciona automaticamente "
        "a irrigação."
    )

uploaded_file = st.file_uploader(
    "Carregue o histórico de contexto em CSV",
    type=["csv"],
)

if uploaded_file is None:
    st.info(
        "Aguardando o carregamento do histórico de contexto."
    )
    st.stop()

file_content = uploaded_file.getvalue()

try:
    dataframe = pd.read_csv(BytesIO(file_content))
except Exception as exc:
    st.error(f"Não foi possível ler o CSV: {exc}")
    st.stop()

validation = CSVValidator().validar(dataframe.copy())

if not validation["valido"]:
    st.error("O CSV não atende à estrutura mínima do Hydros.")
    for error in validation["erros"]:
        st.write(f"• {error}")
    st.stop()

file_hash = compute_file_hash(file_content)
analysis_key = build_analysis_key(
    file_hash,
    algorithm,
    requested_mode,
)

run_clicked = st.button(
    "Executar análise",
    type="primary",
)

if run_clicked:
    engine = HydrosEngine(
        algoritmo_aps=algorithm,
    )

    with st.spinner(
        "Executando agentes e integrando evidências..."
    ):
        if requested_mode == "comparar":
            results = {
                "historico": engine.executar(
                    dataframe.copy(),
                    modo_execucao="historico",
                ),
                "instantaneo": engine.executar(
                    dataframe.copy(),
                    modo_execucao="instantaneo",
                ),
            }
        else:
            results = {
                requested_mode: engine.executar(
                    dataframe.copy(),
                    modo_execucao=requested_mode,
                )
            }

    database = Database()
    execution_ids: Dict[str, str] = {}

    for mode, result in results.items():
        execution_ids[mode] = persist_execution(
            database,
            result,
        )

    st.session_state["hydros_analysis_key"] = analysis_key
    st.session_state["hydros_results"] = results
    st.session_state["hydros_execution_ids"] = execution_ids
    st.session_state["hydros_file_name"] = uploaded_file.name

if st.session_state.get("hydros_analysis_key") != analysis_key:
    st.info(
        "Clique em **Executar análise** para processar "
        "este arquivo e esta configuração."
    )
    st.stop()

results = st.session_state.get(
    "hydros_results",
    {},
)

if not results:
    st.info(
        "Nenhuma execução disponível para esta configuração."
    )
    st.stop()

database = Database()

st.success(
    "Análise concluída e registrada com rastreabilidade integral."
)

info_cols = st.columns(4)
info_cols[0].metric(
    "Arquivo",
    st.session_state.get(
        "hydros_file_name",
        uploaded_file.name,
    ),
)
info_cols[1].metric("Registros", len(dataframe))
info_cols[2].metric("Execuções geradas", len(results))
info_cols[3].metric("Versão", VERSAO_ARQUITETURA)

if len(results) == 2:
    st.subheader("Comparação Histórico × Instantâneo")

    comparison_df = pd.DataFrame(
        build_comparison_rows(results.values())
    )
    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True,
    )

    historical_action = build_execution_view(
        results["historico"]
    )["action"]
    instantaneous_action = build_execution_view(
        results["instantaneo"]
    )["action"]

    if historical_action == instantaneous_action:
        st.info(
            "Os modos produziram a mesma ação neste instante, "
            "com evidências e níveis de confiança próprios."
        )
    else:
        st.warning(
            "Os modos produziram ações diferentes; a contribuição "
            "do histórico deve ser examinada nas evidências."
        )

    historical_tab, instantaneous_tab = st.tabs(
        [
            MODE_LABELS["historico"],
            MODE_LABELS["instantaneo"],
        ]
    )

    with historical_tab:
        _show_execution(
            results["historico"],
            database,
            "historico",
        )

    with instantaneous_tab:
        _show_execution(
            results["instantaneo"],
            database,
            "instantaneo",
        )
else:
    only_mode, only_result = next(iter(results.items()))
    _show_execution(
        only_result,
        database,
        only_mode,
    )

with st.expander(
    "Histórico de contexto carregado",
    expanded=False,
):
    st.dataframe(
        dataframe,
        use_container_width=True,
    )
    _show_context_charts(dataframe)

with st.expander(
    "Execuções persistidas no banco",
    expanded=False,
):
    history_rows = database.listar_execucoes_detalhadas(
        limite=100
    )

    if history_rows:
        history_df = pd.DataFrame(
            [
                {
                    "Execução": row.get("execution_id"),
                    "Data": row.get("data_execucao"),
                    "Talhão": row.get("talhao"),
                    "Modo": row.get("modo_execucao"),
                    "Decisão original": row.get(
                        "decisao_original"
                    ),
                    "Decisão final": row.get(
                        "decisao_final"
                    ),
                    "Confiança": row.get("confianca"),
                    "Conflito": row.get("indice_conflito"),
                    "Avaliação humana": row.get(
                        "status_usuario"
                    ),
                }
                for row in history_rows
            ]
        )

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Nenhuma execução persistida.")
