# Protocolo de reprodutibilidade

## Ambiente

Recomenda-se executar em um ambiente virtual limpo:

```powershell
python -m venv .venv-1
.\.venv-1\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Ordem de execução

```powershell
python run_hydros_validation.py
```

O script executa:

1. testes funcionais;
2. comparação DSSAT × Hydros;
3. diagnóstico das métricas;
4. geração e validação dos artefatos do artigo;
5. verificação dos arquivos obrigatórios;
6. registro das versões dos pacotes;
7. cálculo de hashes SHA-256;
8. geração dos relatórios JSON e Markdown.

## Saídas

```text
results/validation/hydros_validation_report.json
results/validation/hydros_validation_report.md
results/dssat_comparison/
results/dssat_comparison/artigo/
```

## Regra para o artigo

Os valores apresentados no manuscrito devem ser copiados dos CSVs produzidos
pela mesma execução registrada no relatório. Não devem ser combinados resultados
de versões diferentes do código.

## Congelamento

Após resultado `VALIDAÇÃO INTEGRAL: OK`:

```powershell
python freeze_hydros_release.py
```

O ZIP gerado deve ser arquivado junto aos materiais do artigo.
