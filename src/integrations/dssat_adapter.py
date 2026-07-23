"""Adaptador de dados do DSSAT para o formato de entrada do Hydros.

O DSSAT permanece externo à arquitetura do Hydros. Este módulo carrega,
valida e padroniza os resultados simulados para permitir a comparação
experimental com os modos histórico e instantâneo.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd


class DSSATAdapter:
    """Carrega, valida e normaliza resultados exportados do DSSAT."""

    COLUNAS_ENTRADA_OBRIGATORIAS = [
        "data",
        "talhao",
        "loc",
        "solo",
        "cultura",
        "precipitacao",
        "temperatura",
        "graus_dia",
        "evapotranspiracao",
        "coeficiente_cultura",
        "umidade_solo",
        "agua_disponivel",
        "irrigacao_aplicada",
        "estagio_fenologico",
        "estresse_hidrico",
        "produtividade",
    ]

    COLUNAS_CONTEXTO = [
        "data",
        "talhao",
        "loc",
        "solo",
        "cultura",
        "precipitacao",
        "temperatura",
        "graus_dia",
        "evapotranspiracao",
        "coeficiente_cultura",
        "umidade_solo",
        "agua_disponivel",
        "irrigacao_aplicada",
        "irrigacao_ativa",
        "origem_estado_irrigacao",
        "estagio_fenologico",
        "estresse_hidrico",
        "produtividade",
    ]

    COLUNAS_NUMERICAS_ORIGINAIS = [
        "precipitacao",
        "temperatura",
        "graus_dia",
        "evapotranspiracao",
        "coeficiente_cultura",
        "umidade_solo",
        "agua_disponivel",
        "irrigacao_aplicada",
        "estresse_hidrico",
        "produtividade",
    ]

    ALIASES_DECISAO = {
        "iniciar": "iniciar_irrigacao",
        "iniciar_irrigacao": "iniciar_irrigacao",
        "manter": "manter_irrigacao",
        "manter_irrigacao": "manter_irrigacao",
        "aumentar": "aumentar_irrigacao",
        "aumentar_irrigacao": "aumentar_irrigacao",
        "reduzir": "reduzir_irrigacao",
        "reduzir_irrigacao": "reduzir_irrigacao",
        "finalizar": "finalizar_irrigacao",
        "finalizar_irrigacao": "finalizar_irrigacao",
    }

    def carregar_csv(self, caminho: str | Path) -> pd.DataFrame:
        """Lê um CSV do DSSAT e devolve um DataFrame normalizado."""

        caminho = Path(caminho)
        if not caminho.exists():
            raise FileNotFoundError(f"Arquivo DSSAT não encontrado: {caminho}")

        df = pd.read_csv(caminho)
        return self.normalizar(df)

    def normalizar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Padroniza datas, unidades, decisões e identificadores."""

        if not isinstance(df, pd.DataFrame):
            raise TypeError("Os dados do DSSAT devem ser um DataFrame.")

        if df.empty:
            raise ValueError("O arquivo DSSAT está vazio.")

        dados = df.copy()
        dados.columns = [str(coluna).strip() for coluna in dados.columns]

        faltantes = [
            coluna
            for coluna in self.COLUNAS_ENTRADA_OBRIGATORIAS
            if coluna not in dados.columns
        ]
        if faltantes:
            raise ValueError(
                "O arquivo DSSAT não possui as colunas obrigatórias: "
                + ", ".join(faltantes)
            )

        dados["data"] = pd.to_datetime(
            dados["data"],
            dayfirst=True,
            errors="coerce",
        )
        if dados["data"].isna().any():
            linhas = dados.index[dados["data"].isna()].tolist()[:10]
            raise ValueError(
                "Existem datas inválidas no arquivo DSSAT. "
                f"Linhas: {linhas}"
            )

        for coluna in self.COLUNAS_NUMERICAS_ORIGINAIS:
            dados[coluna] = pd.to_numeric(dados[coluna], errors="coerce")

        numericos_invalidos = [
            coluna
            for coluna in self.COLUNAS_NUMERICAS_ORIGINAIS
            if dados[coluna].isna().any()
        ]
        if numericos_invalidos:
            raise ValueError(
                "Existem valores numéricos inválidos nas colunas: "
                + ", ".join(numericos_invalidos)
            )

        self._validar_valores_nao_negativos(dados)
        dados = self._normalizar_unidades_para_hydros(dados)
        dados = self._adicionar_estado_irrigacao(dados)
        dados = self._normalizar_decisoes(dados)
        dados = self._criar_identificadores(dados)

        dados = dados.sort_values(
            ["dssat_run", "data"],
            kind="stable",
        ).reset_index(drop=True)

        # O Hydros atual utiliza datas textuais no formato ano/mês/dia.
        dados["data"] = dados["data"].dt.strftime("%Y/%m/%d")

        return dados

    def _normalizar_unidades_para_hydros(
        self,
        dados: pd.DataFrame,
    ) -> pd.DataFrame:
        """Converte variáveis do DSSAT para a escala usada pelo Hydros."""

        resultado = dados.copy()

        # Mantém os valores originais para rastreabilidade experimental.
        resultado["umidade_solo_dssat_original"] = resultado["umidade_solo"]
        resultado["estresse_hidrico_dssat_original"] = resultado[
            "estresse_hidrico"
        ]

        # O arquivo DSSAT representa umidade volumétrica como fração (0 a 1),
        # enquanto as regras atuais do Hydros trabalham em percentual (0 a 100).
        if resultado["umidade_solo"].max() <= 1.5:
            resultado["umidade_solo"] = resultado["umidade_solo"] * 100.0

        resultado["umidade_solo"] = resultado["umidade_solo"].round(3)

        # O DSSAT fornece índice numérico de estresse entre 0 e 1. Os agentes
        # atuais do Hydros usam as categorias baixo, moderado, alto e critico.
        resultado["estresse_hidrico"] = resultado[
            "estresse_hidrico_dssat_original"
        ].apply(self._classificar_estresse_hidrico)

        return resultado

    @staticmethod
    def _adicionar_estado_irrigacao(
        dados: pd.DataFrame,
    ) -> pd.DataFrame:
        """Explicita o estado usado no intervalo diário da simulação.

        O DSSAT informa a lâmina aplicada em cada data. Para o experimento
        atual, considera-se ativa a irrigação no intervalo em que a lâmina
        é maior que zero. A origem da inferência permanece registrada para
        não confundir esse indicador com o estado físico de uma válvula.
        """

        resultado = dados.copy()
        resultado["irrigacao_ativa"] = (
            resultado["irrigacao_aplicada"] > 0.0
        )
        resultado["origem_estado_irrigacao"] = (
            "inferido_evento_diario_dssat"
        )
        return resultado

    def _normalizar_decisoes(self, dados: pd.DataFrame) -> pd.DataFrame:
        if "decisao_referencia" not in dados.columns:
            raise ValueError(
                "O arquivo DSSAT deve possuir a coluna decisao_referencia."
            )

        resultado = dados.copy()
        resultado["decisao_dssat"] = (
            resultado["decisao_referencia"]
            .astype(str)
            .str.strip()
            .str.lower()
            .map(self.ALIASES_DECISAO)
        )

        if resultado["decisao_dssat"].isna().any():
            valores = sorted(
                resultado.loc[
                    resultado["decisao_dssat"].isna(),
                    "decisao_referencia",
                ]
                .astype(str)
                .unique()
                .tolist()
            )
            raise ValueError(
                "Existem decisões DSSAT não reconhecidas: "
                + ", ".join(valores)
            )

        # Normalização operacional das classes. No arquivo de simulação,
        # alguns registros foram rotulados como aumentar_irrigacao mesmo
        # quando não havia irrigação aplicada no contexto atual. Nesse estado,
        # a ação operacional válida é iniciar_irrigacao. Esta conversão evita
        # comparar classes semanticamente incompatíveis.
        sem_irrigacao = resultado["irrigacao_aplicada"] <= 0
        aumento_sem_irrigacao = (
            sem_irrigacao
            & (resultado["decisao_dssat"] == "aumentar_irrigacao")
        )
        resultado.loc[
            aumento_sem_irrigacao,
            "decisao_dssat",
        ] = "iniciar_irrigacao"

        # Reduzir ou finalizar também exigem uma irrigação em curso. Caso
        # apareçam em cenários sem irrigação, a condição operacional é manter.
        acao_invalida_sem_irrigacao = (
            sem_irrigacao
            & resultado["decisao_dssat"].isin(
                ["reduzir_irrigacao", "finalizar_irrigacao"]
            )
        )
        resultado.loc[
            acao_invalida_sem_irrigacao,
            "decisao_dssat",
        ] = "manter_irrigacao"

        return resultado

    @staticmethod
    def _criar_identificadores(dados: pd.DataFrame) -> pd.DataFrame:
        resultado = dados.copy()

        if "dssat_run" not in resultado.columns:
            resultado["dssat_run"] = 1

        if "cenario" not in resultado.columns:
            resultado["cenario"] = "cenario_dssat"

        resultado["cenario_id"] = (
            resultado["cenario"].astype(str)
            + "_run_"
            + resultado["dssat_run"].astype(str)
        )

        return resultado

    @staticmethod
    def _classificar_estresse_hidrico(valor: float) -> str:
        """Converte o índice DSSAT de 0 a 1 nas classes do Hydros."""

        valor = max(0.0, min(1.0, float(valor)))

        if valor < 0.25:
            return "baixo"
        if valor < 0.50:
            return "moderado"
        if valor < 0.75:
            return "alto"
        return "critico"

    @staticmethod
    def _validar_valores_nao_negativos(dados: pd.DataFrame) -> None:
        colunas = [
            "precipitacao",
            "evapotranspiracao",
            "coeficiente_cultura",
            "umidade_solo",
            "agua_disponivel",
            "irrigacao_aplicada",
            "estresse_hidrico",
            "produtividade",
        ]

        invalidas = [
            coluna
            for coluna in colunas
            if (dados[coluna] < 0).any()
        ]
        if invalidas:
            raise ValueError(
                "Existem valores negativos inválidos nas colunas: "
                + ", ".join(invalidas)
            )

    def separar_execucoes(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Separa o conjunto normalizado por cenário e execução DSSAT."""

        if "cenario_id" not in df.columns:
            df = self.normalizar(df)

        return {
            str(cenario_id): grupo.reset_index(drop=True)
            for cenario_id, grupo in df.groupby("cenario_id", sort=False)
        }

    def contexto_hydros(self, df: pd.DataFrame) -> pd.DataFrame:
        """Retorna somente as colunas aceitas pelos agentes atuais."""

        faltantes = [
            coluna
            for coluna in self.COLUNAS_CONTEXTO
            if coluna not in df.columns
        ]
        if faltantes:
            raise ValueError(
                "Dados ainda não normalizados. Colunas ausentes: "
                + ", ".join(faltantes)
            )

        return df[self.COLUNAS_CONTEXTO].copy()