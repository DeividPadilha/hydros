import pandas as pd


class DataLoader:
    def carregar_csv(self, arquivo):
        """
        Lê o arquivo CSV carregado no Streamlit.
        """
        return pd.read_csv(arquivo)