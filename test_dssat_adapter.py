"""Teste rápido do adaptador DSSAT."""

from src.integrations.dssat_adapter import DSSATAdapter


def main():
    caminho = "data/hydros_soja_dssat_real_v2.csv"

    adapter = DSSATAdapter()
    dados = adapter.carregar_csv(caminho)
    execucoes = adapter.separar_execucoes(dados)

    print("\n=== ADAPTADOR DSSAT ===")
    print("Registros carregados:", len(dados))
    print("Execuções encontradas:", len(execucoes))
    print("Cenários:", list(execucoes.keys()))

    print("\nDecisões DSSAT normalizadas:")
    print(dados["decisao_dssat"].value_counts().to_string())

    primeiro_cenario = next(iter(execucoes))
    contexto = adapter.contexto_hydros(execucoes[primeiro_cenario])

    print("\nPrimeiro cenário:", primeiro_cenario)
    print("Contextos disponíveis:", len(contexto))
    print("Primeira data:", contexto.iloc[0]["data"])
    print("Última data:", contexto.iloc[-1]["data"])

    print("\nADAPTADOR DSSAT: OK")


if __name__ == "__main__":
    main()