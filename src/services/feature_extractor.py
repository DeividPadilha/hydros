"""
Extrator de atributos do Hydros.

Este arquivo implementa a função F(H(Ui)) do modelo Hydros.

No modelo:
Xt = F(H(Ui))

Ou seja:
o vetor de entrada Xt usado pelo APS é extraído a partir
do histórico de contexto da unidade de manejo.

Responsabilidade:
receber o histórico de contexto H(Ui)
e gerar atributos atuais e históricos para o modelo supervisionado.
"""

import pandas as pd


class FeatureExtractor:
    """
    Extrator de atributos históricos e contextuais do Hydros.
    """

    def __init__(self):
        """
        Inicializa o extrator.
        """

        # Janela temporal usada para gerar atributos históricos
        self.tamanho_janela = 5

    def extrair(self, df):
        """
        Extrai Xt a partir de H(Ui).

        Entrada:
        df = histórico de contexto H(Ui)

        Saída:
        DataFrame com uma linha representando Xt.
        """

        # Usa uma cópia para evitar alterar o DataFrame original
        historico = df.copy()

        # Seleciona a janela recente
        janela = historico.tail(self.tamanho_janela)

        # Seleciona o contexto atual C(t)
        contexto_atual = janela.iloc[-1]

        # Atributos atuais do contexto C(t)
        atributos = {
            "cultura": contexto_atual["cultura"],
            "loc": contexto_atual["loc"],
            "solo": contexto_atual["solo"],
            "estagio_fenologico": contexto_atual["estagio_fenologico"],

            "precipitacao": contexto_atual["precipitacao"],
            "temperatura": contexto_atual["temperatura"],
            "graus_dia": contexto_atual["graus_dia"],
            "evapotranspiracao": contexto_atual["evapotranspiracao"],
            "coeficiente_cultura": contexto_atual["coeficiente_cultura"],
            "umidade_solo": contexto_atual["umidade_solo"],
            "agua_disponivel": contexto_atual["agua_disponivel"],
            "irrigacao_aplicada": contexto_atual["irrigacao_aplicada"],
            "produtividade": contexto_atual["produtividade"]
        }

        # Atributos históricos da janela recente
        atributos_historicos = {
            "precipitacao_acumulada": janela["precipitacao"].sum(),
            "evapotranspiracao_acumulada": janela["evapotranspiracao"].sum(),
            "irrigacao_acumulada": janela["irrigacao_aplicada"].sum(),

            "temperatura_media": janela["temperatura"].mean(),
            "graus_dia_medio": janela["graus_dia"].mean(),
            "coeficiente_cultura_medio": janela["coeficiente_cultura"].mean(),
            "umidade_solo_media": janela["umidade_solo"].mean(),
            "agua_disponivel_media": janela["agua_disponivel"].mean(),
            "produtividade_media": janela["produtividade"].mean(),

            "variacao_umidade_solo": self.calcular_variacao(
                janela,
                "umidade_solo"
            ),
            "variacao_agua_disponivel": self.calcular_variacao(
                janela,
                "agua_disponivel"
            ),
            "variacao_produtividade": self.calcular_variacao(
                janela,
                "produtividade"
            ),
            "variacao_evapotranspiracao": self.calcular_variacao(
                janela,
                "evapotranspiracao"
            ),

            "tendencia_umidade_solo": self.calcular_tendencia_numerica(
                janela,
                "umidade_solo"
            ),
            "tendencia_agua_disponivel": self.calcular_tendencia_numerica(
                janela,
                "agua_disponivel"
            ),
            "tendencia_produtividade": self.calcular_tendencia_numerica(
                janela,
                "produtividade"
            ),
            "tendencia_evapotranspiracao": self.calcular_tendencia_numerica(
                janela,
                "evapotranspiracao"
            )
        }

        # Junta atributos atuais e históricos
        atributos.update(
            atributos_historicos
        )

        # Retorna como DataFrame de uma linha
        return pd.DataFrame(
            [atributos]
        )

    def calcular_variacao(self, janela, coluna):
        """
        Calcula a variação entre o primeiro e o último valor da janela.
        """

        valor_inicial = janela[coluna].iloc[0]
        valor_final = janela[coluna].iloc[-1]

        return valor_final - valor_inicial

    def calcular_tendencia_numerica(self, janela, coluna):
        """
        Calcula tendência numérica.

        Retorno:
        -1 = queda
         0 = estável
         1 = aumento
        """

        variacao = self.calcular_variacao(
            janela,
            coluna
        )

        if variacao < 0:
            return -1

        if variacao > 0:
            return 1

        return 0
