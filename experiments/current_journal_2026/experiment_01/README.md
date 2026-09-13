# Experiment I: Contribution of Context Histories

Experimental artifacts for the Historical vs. No History evaluation reported in:

**Hydros: An Agentic AI Architecture Using Context Histories for Agricultural Water Management**

## Dataset

- 108 soybean trajectories
- 60 daily periods per trajectory
- 6,480 raw contexts
- 6,048 eligible samples
- 54 training trajectories
- 18 validation trajectories
- 18 normal-test trajectories
- 18 external climate-test trajectories

## Normal test results

| Classifier | Historical | No History | Delta F1 | 95% CI |
|---|---:|---:|---:|---:|
| Random Forest | 0.8489 | 0.7781 | +0.0708 | [0.0416, 0.1262] |
| Gradient Boosting | 0.8884 | 0.8040 | +0.0844 | [0.0595, 0.1156] |
| Decision Tree | 0.8431 | 0.7782 | +0.0649 | [0.0299, 0.1001] |

## External climate test

| Classifier | Historical | No History |
|---|---:|---:|
| Random Forest | 0.8206 | 0.7772 |
| Gradient Boosting | 0.8800 | 0.7816 |
| Decision Tree | 0.8511 | 0.7512 |

The results show that temporal-memory features added discriminative information relative to the current context alone under the evaluated protocol.

## Artifact

The reproducible experimental package is stored in this directory as:

`Hydros_Experimento_01B_Verificado_Reproduzivel.zip`
