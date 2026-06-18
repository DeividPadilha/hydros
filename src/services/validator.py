"""
Validador do CSV do Hydros.

Este arquivo verifica se o histórico de contexto agrícola
está no padrão esperado pelo modelo Hydros.

O objetivo é garantir que o CSV possua as variáveis necessárias
para representar o contexto hídrico, climático, edáfico,
fenológico, geográfico e produtivo de uma unidade de manejo.
"""

import pandas as pd


class CSVValidator:
    """
    Classe responsável por validar o CSV de entrada do Hydros.
    """

    def __init__(self):
        """
        Define as colunas obrigatórias e as colunas numéricas
        esperadas no histórico de contexto.
        """

        # Colunas obrigatórias do novo padrão Hydros
        # Essas colunas representam o contexto agrícola completo
        self.colunas_obrigatorias = [
            "data",
            "talhao",
            "cultura",
            "loc",
            "solo",
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
            "produtividade"
        ]

        # Colunas que precisam conter valores numéricos
        self.colunas_numericas = [
            "precipitacao",
            "temperatura",
            "graus_dia",
            "evapotranspiracao",
            "coeficiente_cultura",
            "umidade_solo",
            "agua_disponivel",
            "irrigacao_aplicada",
            "produtividade"
        ]

        # Colunas textuais
        # Essas colunas são mantidas como texto
        self.colunas_textuais = [
            "data",
            "talhao",
            "cultura",
            "loc",
            "solo",
            "estagio_fenologico",
            "estresse_hidrico"
        ]

    def validar(self, df):
        """
        Valida o DataFrame carregado a partir do CSV.

        Retorna um dicionário com:
        valido: True ou False
        erros: lista de erros encontrados
        """

        # Lista onde serão armazenados os erros encontrados
        erros = []

        # Verifica se o CSV está vazio
        if df.empty:
            erros.append("O arquivo CSV está vazio.")

            return {
                "valido": False,
                "erros": erros
            }

        # Verifica se todas as colunas obrigatórias existem
        for coluna in self.colunas_obrigatorias:
            if coluna not in df.columns:
                erros.append(f"Coluna obrigatória ausente: {coluna}")

        # Se faltar coluna, não continua a validação
        # Isso evita erro ao tentar acessar uma coluna inexistente
        if erros:
            return {
                "valido": False,
                "erros": erros
            }

        # Verifica campos vazios nas colunas obrigatórias
        if df[self.colunas_obrigatorias].isnull().any().any():
            erros.append("Existem campos obrigatórios vazios.")

        # Valida se a coluna data pode ser interpretada como data
        try:
            pd.to_datetime(df["data"])
        except Exception:
            erros.append("A coluna data possui valores inválidos.")

        # Valida se as colunas numéricas possuem apenas números
        for coluna in self.colunas_numericas:
            try:
                df[coluna] = pd.to_numeric(df[coluna])
            except Exception:
                erros.append(f"A coluna {coluna} deve conter apenas números.")

        # Valida valores negativos em colunas que não devem ser negativas
        # Temperatura pode variar conforme região, mas no contexto agrícola usado aqui
        # vamos manter a validação simples e impedir valores negativos por enquanto
        for coluna in self.colunas_numericas:
            if coluna in df.columns and (df[coluna] < 0).any():
                erros.append(f"A coluna {coluna} possui valores negativos inválidos.")

        # Validação básica da coluna coeficiente_cultura
        # O Kc normalmente é um valor positivo
        if "coeficiente_cultura" in df.columns:
            if (df["coeficiente_cultura"] <= 0).any():
                erros.append("A coluna coeficiente_cultura deve possuir valores maiores que zero.")

        # Validação básica da coluna umidade_solo
        # Neste protótipo a umidade do solo é representada em percentual
        if "umidade_solo" in df.columns:
            if (df["umidade_solo"] > 100).any():
                erros.append("A coluna umidade_solo não pode ser maior que 100.")

        # Retorna o resultado final da validação
        return {
            "valido": len(erros) == 0,
            "erros": erros
        }