# Hydros

**English version below. Versão em português mais abaixo.**

---

# English

## Overview

Hydros is an intelligent model for agricultural water management that uses **context histories as temporal memory** for each management unit. The current architecture follows Agentic AI principles and integrates specialized agents, explicit agronomic rules, supervised Machine Learning evidence, semantic support from HydrosOnto, and a hybrid decision engine.

Hydros supports five water-management actions:

- `start irrigation`
- `maintain irrigation`
- `increase irrigation`
- `reduce irrigation`
- `finish irrigation`

Hydros does not autonomously actuate irrigation infrastructure.

## Core architecture

The main processing components are:

- **Aclim**: climatic evidence
- **Ahid**: hydric evidence
- **Afen**: phenological evidence
- **Ageo**: geographic and soil-context evidence
- **Aprod**: productive evidence
- **Ahist**: historical-context evidence
- **AIEC**: contextual evidence integration
- **ARG**: agronomic rules
- **APS**: supervised predictive evidence
- **AMDH**: hybrid decision coordination

HydrosOnto provides semantic representation, verification, and traceability support. It does not replace AMDH and does not directly determine the irrigation action.

## Context representation

For each management unit \(U_i\), Hydros maintains an ordered context history:

\[
H(U_i)=\{C(t_1),C(t_2),...,C(t_n)\}
\]

The current context representation includes:

```text
loc
soil
crop
precipitation
temperature
growing degree days
evapotranspiration
crop coefficient
soil moisture
available water
applied irrigation
phenological stage
water stress
yield
```

## HydrosOnto

The current ontology implementation contains:

- 500 axioms
- 31 classes
- 25 object properties
- 12 data properties
- 44 individuals

Logical consistency was verified with the HermiT reasoner.

The ontology file is located at:

```text
ontology/hydros_onto.ttl
```

## Experimental evaluations

Hydros currently has two distinct experimental generations associated with different manuscripts. They are preserved separately to avoid mixing results from different stages of the research.

### 1. IEEE MetroAgriFor 2026 evaluation

Paper:

**Hydros: A Multi-Agent Model for Explainable Irrigation Decision Support Based on Context Histories**

This evaluation corresponds to an earlier stage of Hydros.

#### Experiment I

Historical mode outperformed Instantaneous mode in the synthetic trajectory evaluation.

| Evaluation | Historical | Instantaneous |
|---|---:|---:|
| Normal test macro F1 | 0.9235 | 0.8133 |
| Climate-shift macro F1 | 0.9203 | 0.7856 |

The normal-test macro F1 difference was approximately `+0.1102`, with a paired 95% confidence interval of `[0.0749, 0.1491]`.

Under the hotter and drier climate shift, the macro F1 gain was approximately `+0.1346`, with a 95% confidence interval of `[0.1027, 0.1650]`.

#### Experiment II

The DSSAT pilot used:

- 256 daily observations
- two crop simulations
- 11 irrigation-intensification reference events

Historical mode detected 4 of the 11 intensification events, while Instantaneous mode detected none.

This experiment did **not** operate in closed loop. Irrigation recommendations were not fed back into DSSAT, so this evaluation did not support conclusions about water savings, yield effects, or stress reduction.

### 2. Current journal evaluation

Target journal:

**Computers and Electronics in Agriculture**

Manuscript:

**Hydros: An Agentic AI Architecture Using Context Histories for Agricultural Water Management**

This is the current and expanded Hydros evaluation.

#### Experiment I: Contribution of context histories

The controlled evaluation used:

- 108 soybean trajectories
- 60 daily periods per trajectory
- 6,480 raw contexts
- 6,048 eligible samples after requiring a complete five-context window
- 54 training trajectories
- 18 validation trajectories
- 18 normal-test trajectories
- 18 external hotter-and-drier climate trajectories

##### Normal test set

| Classifier | Historical | No History | Delta F1 | 95% CI |
|---|---:|---:|---:|---:|
| Random Forest | 0.8489 | 0.7781 | +0.0708 | [0.0416, 0.1262] |
| Gradient Boosting | 0.8884 | 0.8040 | +0.0844 | [0.0595, 0.1156] |
| Decision Tree | 0.8431 | 0.7782 | +0.0649 | [0.0299, 0.1001] |

##### External climate test

| Classifier | Historical | No History |
|---|---:|---:|
| Random Forest | 0.8206 | 0.7772 |
| Gradient Boosting | 0.8800 | 0.7816 |
| Decision Tree | 0.8511 | 0.7512 |

These results show that temporal-memory features added discriminative information relative to the current context alone under the evaluated protocol.

#### Experiment II: Closed-loop DSSAT evaluation

`UFGA7801` and `UFGA8401` were used during protocol development. After the configuration was frozen, `UFGA8501` was reserved as the final holdout.

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

Main outcomes:

- gross irrigation reduction: **37.79%**
- effective irrigation reduction: **38.04%**
- yield retention: **97.74%**
- irrigation water productivity increased from **22.24 to 35.08 kg/ha/mm**
- drainage decreased by **10 mm**
- water stress increased

The closed-loop result represents a tradeoff between water reduction, yield preservation, and increased water stress. It is not presented as evidence of universal agronomic superiority.

## Automated validation

The consolidated implementation passed:

```text
52/52 automated Pytest tests
```

Earlier totals such as 8/8, 25/25, 41/41, or 50/50 correspond to previous development checkpoints and are not the current validation total.

## Main repository structure

```text
src/
├── agents/
├── config/
├── core/
├── database/
├── integrations/
├── ontology/
├── services/
└── models/

ontology/
└── hydros_onto.ttl

test_*.py
results/
data/
```

## Installation

PowerShell:

```powershell
python -m venv .venv-1
.\.venv-1\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Interface

```powershell
streamlit run app.py
```

## Scientific status

The current evidence is based on controlled synthetic trajectories and DSSAT simulations. The closed-loop evaluation currently contains one final holdout scenario, `UFGA8501`. Broader validation with additional independent scenarios, soils, years, climates, field data, and domain experts remains future work.

---

# Português

## Visão geral

O Hydros é um modelo inteligente para gerenciamento hídrico agrícola que utiliza **Históricos de Contextos como memória temporal** para cada unidade de manejo. A arquitetura atual segue princípios de IA Agêntica e integra agentes especializados, regras agronômicas explícitas, evidências de Aprendizado de Máquina supervisionado, suporte semântico da HydrosOnto e um motor híbrido de decisão.

O Hydros trabalha com cinco ações de manejo hídrico:

- `iniciar irrigação`
- `manter irrigação`
- `aumentar irrigação`
- `reduzir irrigação`
- `finalizar irrigação`

O Hydros não aciona autonomamente a infraestrutura de irrigação.

## Arquitetura principal

Os principais componentes de processamento são:

- **Aclim**: evidência climática
- **Ahid**: evidência hídrica
- **Afen**: evidência fenológica
- **Ageo**: evidência geográfica e de contexto do solo
- **Aprod**: evidência produtiva
- **Ahist**: evidência histórica
- **AIEC**: integração das evidências contextuais
- **ARG**: regras agronômicas
- **APS**: evidência preditiva supervisionada
- **AMDH**: coordenação híbrida da decisão

A HydrosOnto fornece representação semântica, verificação e suporte à rastreabilidade. Ela não substitui o AMDH e não determina diretamente a ação de irrigação.

## Representação do contexto

Para cada unidade de manejo \(U_i\), o Hydros mantém um histórico ordenado de contextos:

\[
H(U_i)=\{C(t_1),C(t_2),...,C(t_n)\}
\]

A representação atual do contexto inclui:

```text
localização
solo
cultura
precipitação
temperatura
graus-dia
evapotranspiração
coeficiente de cultura
umidade do solo
água disponível
irrigação aplicada
estágio fenológico
estresse hídrico
produtividade
```

## HydrosOnto

A implementação atual da ontologia contém:

- 500 axiomas
- 31 classes
- 25 propriedades de objeto
- 12 propriedades de dados
- 44 indivíduos

A consistência lógica foi verificada com o raciocinador HermiT.

O arquivo da ontologia está em:

```text
ontology/hydros_onto.ttl
```

## Avaliações experimentais

O Hydros possui atualmente duas gerações experimentais distintas associadas a manuscritos diferentes. Elas são preservadas separadamente para evitar a mistura de resultados de diferentes etapas da pesquisa.

### 1. Avaliação IEEE MetroAgriFor 2026

Artigo:

**Hydros: A Multi-Agent Model for Explainable Irrigation Decision Support Based on Context Histories**

Essa avaliação corresponde a uma etapa anterior do Hydros.

#### Experimento I

O modo Histórico superou o modo Instantâneo na avaliação com trajetórias sintéticas.

| Avaliação | Histórico | Instantâneo |
|---|---:|---:|
| Macro F1 no teste normal | 0.9235 | 0.8133 |
| Macro F1 no teste climático | 0.9203 | 0.7856 |

A diferença de macro F1 no teste normal foi de aproximadamente `+0.1102`, com intervalo de confiança pareado de 95% de `[0.0749, 0.1491]`.

No cenário climático mais quente e seco, o ganho de macro F1 foi de aproximadamente `+0.1346`, com intervalo de confiança de 95% de `[0.1027, 0.1650]`.

#### Experimento II

O piloto com DSSAT utilizou:

- 256 observações diárias
- duas simulações de cultura
- 11 eventos de referência de intensificação de irrigação

O modo Histórico detectou 4 dos 11 eventos de intensificação, enquanto o modo Instantâneo não detectou nenhum.

Esse experimento **não** operava em ciclo fechado. As recomendações de irrigação não eram realimentadas no DSSAT e, portanto, essa avaliação não permitia concluir sobre economia de água, efeitos na produtividade ou redução de estresse.

### 2. Avaliação atual para periódico

Periódico alvo:

**Computers and Electronics in Agriculture**

Manuscrito:

**Hydros: An Agentic AI Architecture Using Context Histories for Agricultural Water Management**

Esta é a avaliação atual e ampliada do Hydros.

#### Experimento I: Contribuição dos Históricos de Contextos

A avaliação controlada utilizou:

- 108 trajetórias de soja
- 60 períodos diários por trajetória
- 6.480 contextos brutos
- 6.048 amostras elegíveis após exigir janela completa de cinco contextos
- 54 trajetórias de treinamento
- 18 trajetórias de validação
- 18 trajetórias de teste normal
- 18 trajetórias externas em cenário climático mais quente e seco

##### Teste normal

| Classificador | Histórico | Sem Histórico | Delta F1 | IC 95% |
|---|---:|---:|---:|---:|
| Random Forest | 0.8489 | 0.7781 | +0.0708 | [0.0416, 0.1262] |
| Gradient Boosting | 0.8884 | 0.8040 | +0.0844 | [0.0595, 0.1156] |
| Decision Tree | 0.8431 | 0.7782 | +0.0649 | [0.0299, 0.1001] |

##### Teste climático externo

| Classificador | Histórico | Sem Histórico |
|---|---:|---:|
| Random Forest | 0.8206 | 0.7772 |
| Gradient Boosting | 0.8800 | 0.7816 |
| Decision Tree | 0.8511 | 0.7512 |

Os resultados mostram que, no protocolo avaliado, os atributos derivados da memória temporal adicionaram informação discriminativa em relação ao contexto atual isolado.

#### Experimento II: Avaliação DSSAT em ciclo fechado

`UFGA7801` e `UFGA8401` foram utilizados durante o desenvolvimento do protocolo. Após o congelamento da configuração, `UFGA8501` foi reservado como holdout final.

| Indicador | Referência | Hydros |
|---|---:|---:|
| Irrigação bruta | 217 mm | 135 mm |
| Irrigação efetiva | 163 mm | 101 mm |
| Produtividade | 3625 kg/ha | 3543 kg/ha |
| Retenção de produtividade | 100% | 97.74% |
| Produtividade da água de irrigação | 22.24 kg/ha/mm | 35.08 kg/ha/mm |
| Dias com estresse hídrico | 0 | 6 |
| Estresse acumulado | 0.518 | 2.673 |
| Drenagem | 330 mm | 320 mm |

Principais resultados:

- redução da irrigação bruta: **37,79%**
- redução da irrigação efetiva: **38,04%**
- retenção de produtividade: **97,74%**
- produtividade da água de irrigação aumentou de **22,24 para 35,08 kg/ha/mm**
- drenagem reduziu **10 mm**
- o estresse hídrico aumentou

O resultado em ciclo fechado representa um compromisso entre redução de água, preservação da produtividade e aumento do estresse hídrico. Ele não é apresentado como evidência de superioridade agronômica universal.

## Validação automatizada

A implementação consolidada passou em:

```text
52/52 testes automatizados com Pytest
```

Totais anteriores, como 8/8, 25/25, 41/41 ou 50/50, correspondem a checkpoints anteriores de desenvolvimento e não representam o total atual.

## Estrutura principal do repositório

```text
src/
├── agents/
├── config/
├── core/
├── database/
├── integrations/
├── ontology/
├── services/
└── models/

ontology/
└── hydros_onto.ttl

test_*.py
results/
data/
```

## Instalação

No PowerShell:

```powershell
python -m venv .venv-1
.\.venv-1\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Interface

```powershell
streamlit run app.py
```

## Situação científica

As evidências atuais são baseadas em trajetórias sintéticas controladas e simulações DSSAT. A avaliação em ciclo fechado contém atualmente um holdout final, `UFGA8501`. Validações mais amplas com novos cenários independentes, solos, anos, condições climáticas, dados de campo e especialistas permanecem como trabalhos futuros.
