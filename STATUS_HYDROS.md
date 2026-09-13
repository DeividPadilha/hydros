# Hydros Status — 2026

This repository preserves two distinct experimental generations of Hydros associated with two different scientific manuscripts.

1. **IEEE MetroAgriFor 2026**
2. **Current journal manuscript**, submitted first to *Computers and Electronics in Agriculture*

Results from these generations must not be mixed.

---

# English

## 1. Current scientific status

Hydros is a functional and traceable research prototype for agricultural water-management decision support.

The current architecture uses context histories as temporal memory for each management unit and integrates:

- specialized contextual agents;
- the Contextual Evidence Integration Agent (AIEC);
- explicit agronomic rules through ARG;
- supervised predictive evidence through APS;
- semantic support and traceability through HydrosOnto;
- hybrid decision coordination through AMDH;
- five water-management actions;
- execution traceability and conflict recording;
- DSSAT integration for controlled experimental evaluation.

Hydros does not autonomously actuate irrigation infrastructure.

## 2. IEEE MetroAgriFor 2026 experimental generation

Paper:

**Hydros: A Multi-Agent Model for Explainable Irrigation Decision Support Based on Context Histories**

This experimental generation represents an earlier stage of Hydros.

### Experiment I

Normal test:

- Historical macro F1: **0.9235**
- Instantaneous macro F1: **0.8133**

External hotter-and-drier climate test:

- Historical macro F1: **0.9203**
- Instantaneous macro F1: **0.7856**

### Experiment II

The DSSAT pilot used:

- 256 daily observations;
- two crop simulations;
- 11 irrigation-intensification reference events.

Historical mode detected 4 of 11 intensification events, while Instantaneous mode detected none.

This experiment was **not closed loop**. Irrigation recommendations were not fed back into DSSAT.

The corresponding artifacts are preserved under:

```text
experiments/metroagrifor_2026/
```

## 3. Current journal experimental generation

Manuscript:

**Hydros: An Agentic AI Architecture Using Context Histories for Agricultural Water Management**

Current target journal:

**Computers and Electronics in Agriculture**

### Experiment I: Contribution of Context Histories

The evaluation used:

- 108 soybean trajectories;
- 60 daily periods per trajectory;
- 6,480 raw contexts;
- 6,048 eligible samples;
- 54 training trajectories;
- 18 validation trajectories;
- 18 normal-test trajectories;
- 18 external climate-test trajectories.

Normal test macro F1:

| Classifier | Historical | No History | Delta F1 | 95% CI |
|---|---:|---:|---:|---:|
| Random Forest | 0.8489 | 0.7781 | +0.0708 | [0.0416, 0.1262] |
| Gradient Boosting | 0.8884 | 0.8040 | +0.0844 | [0.0595, 0.1156] |
| Decision Tree | 0.8431 | 0.7782 | +0.0649 | [0.0299, 0.1001] |

External climate test macro F1:

| Classifier | Historical | No History |
|---|---:|---:|
| Random Forest | 0.8206 | 0.7772 |
| Gradient Boosting | 0.8800 | 0.7816 |
| Decision Tree | 0.8511 | 0.7512 |

### Experiment II: Closed-Loop DSSAT Evaluation

Development scenarios:

- UFGA7801
- UFGA8401

Final holdout:

- UFGA8501

Final holdout results:

| Indicator | Reference | Hydros |
|---|---:|---:|
| Gross irrigation | 217 mm | 135 mm |
| Effective irrigation | 163 mm | 101 mm |
| Yield | 3625 kg/ha | 3543 kg/ha |
| Yield retention | 100% | 97.74% |
| Irrigation water productivity | 22.24 kg/ha/mm | 35.08 kg/ha/mm |
| Days with water stress | 0 | 6 |
| Accumulated stress | 0.518 | 2.673 |
| Drainage | 330 mm | 320 mm |

Main result:

- gross irrigation reduction: **37.79%**;
- effective irrigation reduction: **38.04%**;
- yield retention: **97.74%**;
- irrigation water productivity increased;
- drainage decreased;
- water stress increased.

This result is interpreted as a tradeoff between water reduction, yield preservation, and increased water stress, not as evidence of universal agronomic superiority.

The Hydros configuration was frozen before opening UFGA8501. The holdout must not be used for post-hoc recalibration.

The corresponding artifacts are preserved under:

```text
experiments/current_journal_2026/
```

## 4. HydrosOnto

The current ontology implementation contains:

- 500 axioms;
- 31 classes;
- 25 object properties;
- 12 data properties;
- 44 individuals.

Logical consistency was verified using HermiT.

HydrosOnto provides semantic representation, verification, and traceability support. It does not replace AMDH and does not directly determine the irrigation action.

## 5. Automated validation

The consolidated implementation passed:

```text
52/52 automated Pytest tests
```

Earlier totals such as 8/8, 25/25, 41/41, and 50/50 correspond to previous development checkpoints.

## 6. Current limitations

The current evidence remains based on controlled synthetic trajectories and DSSAT simulations.

The current closed-loop evaluation contains one final holdout scenario, UFGA8501.

Broader validation with additional independent DSSAT scenarios, soils, years, climate conditions, field data, and domain experts remains future work.

The execution record demonstrates traceability of the processing elements, but does not by itself constitute a complete human evaluation of explainability.

## 7. Correct classification of the current state

Hydros is currently:

> a functional, traceable research prototype with controlled experimental evidence for temporal-memory contribution and one closed-loop DSSAT holdout.

Hydros is not currently:

> an agronomically validated system for unrestricted operational use on commercial farms.

---

# Português

## 1. Situação científica atual

O Hydros é um protótipo de pesquisa funcional e rastreável para apoio à decisão em gerenciamento hídrico agrícola.

A arquitetura atual utiliza Históricos de Contextos como memória temporal para cada unidade de manejo e integra:

- agentes contextuais especializados;
- Agente de Integração de Evidências Contextuais (AIEC);
- regras agronômicas explícitas por meio do ARG;
- evidências preditivas supervisionadas por meio do APS;
- suporte semântico e rastreabilidade por meio da HydrosOnto;
- coordenação híbrida da decisão por meio do AMDH;
- cinco ações de manejo hídrico;
- rastreabilidade da execução e registro de conflitos;
- integração com DSSAT para avaliação experimental controlada.

O Hydros não aciona autonomamente a infraestrutura de irrigação.

## 2. Geração experimental IEEE MetroAgriFor 2026

Artigo:

**Hydros: A Multi-Agent Model for Explainable Irrigation Decision Support Based on Context Histories**

Essa geração experimental representa uma etapa anterior do Hydros.

### Experimento I

Teste normal:

- Macro F1 Histórico: **0,9235**
- Macro F1 Instantâneo: **0,8133**

Teste climático externo mais quente e seco:

- Macro F1 Histórico: **0,9203**
- Macro F1 Instantâneo: **0,7856**

### Experimento II

O piloto DSSAT utilizou:

- 256 observações diárias;
- duas simulações de cultura;
- 11 eventos de referência de intensificação de irrigação.

O modo Histórico detectou 4 dos 11 eventos de intensificação, enquanto o modo Instantâneo não detectou nenhum.

Esse experimento **não operava em ciclo fechado**. As recomendações de irrigação não eram realimentadas no DSSAT.

Os artefatos correspondentes estão preservados em:

```text
experiments/metroagrifor_2026/
```

## 3. Geração experimental do manuscrito atual

Manuscrito:

**Hydros: An Agentic AI Architecture Using Context Histories for Agricultural Water Management**

Periódico alvo atual:

**Computers and Electronics in Agriculture**

### Experimento I: Contribuição dos Históricos de Contextos

A avaliação utilizou:

- 108 trajetórias de soja;
- 60 períodos diários por trajetória;
- 6.480 contextos brutos;
- 6.048 amostras elegíveis;
- 54 trajetórias de treinamento;
- 18 trajetórias de validação;
- 18 trajetórias de teste normal;
- 18 trajetórias de teste climático externo.

Macro F1 no teste normal:

| Classificador | Histórico | Sem Histórico | Delta F1 | IC 95% |
|---|---:|---:|---:|---:|
| Random Forest | 0.8489 | 0.7781 | +0.0708 | [0.0416, 0.1262] |
| Gradient Boosting | 0.8884 | 0.8040 | +0.0844 | [0.0595, 0.1156] |
| Decision Tree | 0.8431 | 0.7782 | +0.0649 | [0.0299, 0.1001] |

Macro F1 no teste climático externo:

| Classificador | Histórico | Sem Histórico |
|---|---:|---:|
| Random Forest | 0.8206 | 0.7772 |
| Gradient Boosting | 0.8800 | 0.7816 |
| Decision Tree | 0.8511 | 0.7512 |

### Experimento II: Avaliação DSSAT em Ciclo Fechado

Cenários de desenvolvimento:

- UFGA7801
- UFGA8401

Holdout final:

- UFGA8501

Resultados finais do holdout:

| Indicador | Referência | Hydros |
|---|---:|---:|
| Irrigação bruta | 217 mm | 135 mm |
| Irrigação efetiva | 163 mm | 101 mm |
| Produtividade | 3625 kg/ha | 3543 kg/ha |
| Retenção de produtividade | 100% | 97,74% |
| Produtividade da água de irrigação | 22,24 kg/ha/mm | 35,08 kg/ha/mm |
| Dias com estresse hídrico | 0 | 6 |
| Estresse acumulado | 0,518 | 2,673 |
| Drenagem | 330 mm | 320 mm |

Resultado principal:

- redução da irrigação bruta: **37,79%**;
- redução da irrigação efetiva: **38,04%**;
- retenção de produtividade: **97,74%**;
- aumento da produtividade da água de irrigação;
- redução da drenagem;
- aumento do estresse hídrico.

Esse resultado é interpretado como um compromisso entre redução de água, preservação da produtividade e aumento do estresse hídrico, e não como evidência de superioridade agronômica universal.

A configuração do Hydros foi congelada antes da abertura do UFGA8501. O holdout não deve ser usado para recalibração posterior.

Os artefatos correspondentes estão preservados em:

```text
experiments/current_journal_2026/
```

## 4. HydrosOnto

A implementação atual da ontologia contém:

- 500 axiomas;
- 31 classes;
- 25 propriedades de objeto;
- 12 propriedades de dados;
- 44 indivíduos.

A consistência lógica foi verificada com o HermiT.

A HydrosOnto fornece representação semântica, verificação e suporte à rastreabilidade. Ela não substitui o AMDH e não determina diretamente a ação de irrigação.

## 5. Validação automatizada

A implementação consolidada passou em:

```text
52/52 testes automatizados com Pytest
```

Totais anteriores, como 8/8, 25/25, 41/41 e 50/50, correspondem a checkpoints anteriores de desenvolvimento.

## 6. Limitações atuais

As evidências atuais continuam baseadas em trajetórias sintéticas controladas e simulações DSSAT.

A avaliação atual em ciclo fechado contém um holdout final, o UFGA8501.

Validações mais amplas com novos cenários DSSAT independentes, solos, anos, condições climáticas, dados de campo e especialistas permanecem como trabalhos futuros.

O registro de execução demonstra rastreabilidade dos elementos de processamento, mas não constitui, por si só, uma avaliação humana completa da explicabilidade.

## 7. Classificação correta do estado atual

Atualmente, o Hydros é:

> um protótipo de pesquisa funcional e rastreável, com evidência experimental controlada sobre a contribuição da memória temporal e um holdout DSSAT em ciclo fechado.

Atualmente, o Hydros não é:

> um sistema agronomicamente validado para uso operacional irrestrito em propriedades rurais comerciais.
