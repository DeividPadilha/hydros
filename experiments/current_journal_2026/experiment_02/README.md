# Experiment II: Closed-Loop DSSAT Evaluation

Experimental artifacts for the closed-loop evaluation reported in:

**Hydros: An Agentic AI Architecture Using Context Histories for Agricultural Water Management**

## Experimental protocol

Development scenarios:
- UFGA7801
- UFGA8401

Final holdout:
- UFGA8501

The Hydros configuration was frozen before opening the final holdout. No post-holdout recalibration was performed.

## Final holdout results

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

## Main outcomes

- Gross irrigation reduction: 37.79%
- Effective irrigation reduction: 38.04%
- Yield retention: 97.74%
- Irrigation water productivity increased from 22.24 to 35.08 kg/ha/mm
- Drainage decreased by 10 mm
- Water stress increased

The result represents a tradeoff between water reduction, yield preservation, and increased water stress. It is not presented as evidence of universal agronomic superiority.

## Artifacts

This directory contains:

- `Hydros_Experimento_02B_Holdout_Final_UFGA8501_CRLF_Corrigido.zip`
- `RELATORIO_FINAL_EXPERIMENTO_02B_HOLDOUT_UFGA8501.md`
