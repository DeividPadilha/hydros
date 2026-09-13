# Reproducibility Protocol

This repository preserves two distinct experimental generations of Hydros:

1. IEEE MetroAgriFor 2026
2. Current journal manuscript submitted first to Computers and Electronics in Agriculture

The artifacts of each generation are stored separately and must not be mixed.

---

# 1. IEEE MetroAgriFor 2026

Paper:

**Hydros: A Multi-Agent Model for Explainable Irrigation Decision Support Based on Context Histories**

Experimental artifacts:

```text
experiments/metroagrifor_2026/
├── experiment_01/
└── experiment_02/
```

## Experiment I

The reproducible package is stored in:

```text
experiments/metroagrifor_2026/experiment_01/
Hydros_Experimento_01_Historico_vs_SemHistorico.zip
```

This experiment corresponds to the Historical vs. Instantaneous temporal-memory evaluation reported in the MetroAgriFor paper.

## Experiment II

The reproducible package is stored in:

```text
experiments/metroagrifor_2026/experiment_02/
Hydros_MetroAgriFor_2026_Experiment_02_Artifacts.zip
```

The package contains the DSSAT pilot used in the paper.

Main execution:

```powershell
python run_dssat_comparison.py
python diagnostico_resultados.py
python gerar_resultados_artigo.py
```

This experiment used 256 daily observations and was not a closed-loop evaluation.

---

# 2. Current Journal Manuscript

Manuscript:

**Hydros: An Agentic AI Architecture Using Context Histories for Agricultural Water Management**

Current target journal:

**Computers and Electronics in Agriculture**

Experimental artifacts:

```text
experiments/current_journal_2026/
├── experiment_01/
└── experiment_02/
```

## Experiment I: Contribution of Context Histories

The verified and reproducible package is stored in:

```text
experiments/current_journal_2026/experiment_01/
Hydros_Experimento_01B_Verificado_Reproduzivel.zip
```

Inside the package, the main reproduction script is:

```powershell
python codigo/experimento_01b_reproducivel.py
```

The package contains the data, predictions, metrics, official result summary, and SHA-256 integrity manifest associated with the experiment.

## Experiment II: Closed-Loop DSSAT Evaluation

The final holdout package is stored in:

```text
experiments/current_journal_2026/experiment_02/
Hydros_Experimento_02B_Holdout_Final_UFGA8501_CRLF_Corrigido.zip
```

The final holdout report is stored in the same directory:

```text
RELATORIO_FINAL_EXPERIMENTO_02B_HOLDOUT_UFGA8501.md
```

The final holdout execution is:

```powershell
python run_holdout_final_exp02b.py --dssat-root "C:\DSSAT48"
```

Development scenarios:

```text
UFGA7801
UFGA8401
```

Final holdout:

```text
UFGA8501
```

The Hydros configuration was frozen before opening UFGA8501. The final holdout must not be used for post-hoc recalibration.

---

# 3. Software Validation

The consolidated implementation passed:

```text
52/52 automated Pytest tests
```

Earlier totals such as 8/8, 25/25, 41/41, or 50/50 correspond to previous development checkpoints and are not the current validation total.

---

# 4. Preservation Rule

Results from different experimental generations must not be combined.

The MetroAgriFor artifacts must remain preserved because they correspond to a separate publication and an earlier experimental stage.

The current journal artifacts correspond to the later and expanded evaluation.

Future changes that modify parameters, rules, models, or experimental policies after the opening of UFGA8501 must be treated as a new experimental version and require a new independent holdout.

---

# Protocolo de Reprodutibilidade

Este repositório preserva duas gerações experimentais distintas do Hydros:

1. IEEE MetroAgriFor 2026
2. Manuscrito atual submetido inicialmente ao Computers and Electronics in Agriculture

Os artefatos de cada geração são armazenados separadamente e não devem ser misturados.

---

# 1. IEEE MetroAgriFor 2026

Artigo:

**Hydros: A Multi-Agent Model for Explainable Irrigation Decision Support Based on Context Histories**

Artefatos experimentais:

```text
experiments/metroagrifor_2026/
├── experiment_01/
└── experiment_02/
```

## Experimento I

O pacote reproduzível está armazenado em:

```text
experiments/metroagrifor_2026/experiment_01/
Hydros_Experimento_01_Historico_vs_SemHistorico.zip
```

Esse experimento corresponde à avaliação Histórico vs. Instantâneo reportada no artigo do MetroAgriFor.

## Experimento II

O pacote reproduzível está armazenado em:

```text
experiments/metroagrifor_2026/experiment_02/
Hydros_MetroAgriFor_2026_Experiment_02_Artifacts.zip
```

Execução principal:

```powershell
python run_dssat_comparison.py
python diagnostico_resultados.py
python gerar_resultados_artigo.py
```

Esse experimento utilizou 256 observações diárias e não operou em ciclo fechado.

---

# 2. Manuscrito Atual

Manuscrito:

**Hydros: An Agentic AI Architecture Using Context Histories for Agricultural Water Management**

Periódico alvo atual:

**Computers and Electronics in Agriculture**

Artefatos experimentais:

```text
experiments/current_journal_2026/
├── experiment_01/
└── experiment_02/
```

## Experimento I: Contribuição dos Históricos de Contextos

O pacote verificado e reproduzível está armazenado em:

```text
experiments/current_journal_2026/experiment_01/
Hydros_Experimento_01B_Verificado_Reproduzivel.zip
```

Dentro do pacote, o script principal é:

```powershell
python codigo/experimento_01b_reproducivel.py
```

O pacote contém dados, predições, métricas, resumo do resultado oficial e manifesto de integridade SHA-256.

## Experimento II: Avaliação DSSAT em Ciclo Fechado

O pacote do holdout final está armazenado em:

```text
experiments/current_journal_2026/experiment_02/
Hydros_Experimento_02B_Holdout_Final_UFGA8501_CRLF_Corrigido.zip
```

O relatório final está na mesma pasta:

```text
RELATORIO_FINAL_EXPERIMENTO_02B_HOLDOUT_UFGA8501.md
```

Execução do holdout final:

```powershell
python run_holdout_final_exp02b.py --dssat-root "C:\DSSAT48"
```

Cenários de desenvolvimento:

```text
UFGA7801
UFGA8401
```

Holdout final:

```text
UFGA8501
```

A configuração do Hydros foi congelada antes da abertura do UFGA8501. O resultado final não deve ser usado para recalibração posterior.

---

# 3. Validação de Software

A implementação consolidada passou em:

```text
52/52 testes automatizados com Pytest
```

Totais anteriores, como 8/8, 25/25, 41/41 ou 50/50, correspondem a checkpoints anteriores de desenvolvimento.

---

# 4. Regra de Preservação

Resultados de gerações experimentais diferentes não devem ser combinados.

Os artefatos do MetroAgriFor devem permanecer preservados porque correspondem a uma publicação distinta e a uma etapa experimental anterior.

Os artefatos do manuscrito atual correspondem à avaliação posterior e ampliada.

Qualquer alteração futura em parâmetros, regras, modelos ou políticas experimentais após a abertura do UFGA8501 deve ser tratada como nova versão experimental e utilizar um novo holdout independente.
