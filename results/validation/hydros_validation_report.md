# Relatório de validação integral do Hydros

- Data UTC: `2026-07-23T17:50:12+00:00`
- Resultado: **OK**
- Python: `3.12.10 (tags/v3.12.10:0cc8128, Apr  8 2025, 12:21:36) [MSC v.1943 64 bit (AMD64)]`
- Plataforma: `Windows-11-10.0.26200-SP0`

## Testes funcionais

| Script | Status | Tempo (s) |
|---|---:|---:|
| `test_hydros_model_flow.py` | ok | 3.066 |
| `test_hydros_modes.py` | ok | 2.988 |
| `test_hydros_algorithms.py` | ok | 2.669 |
| `test_hydros_scenarios.py` | ok | 4.578 |
| `test_dssat_adapter.py` | ok | 0.943 |
| `test_hydros_traceability.py` | ok | 2.546 |
| `test_hydros_evidence_quality.py` | ok | 2.770 |
| `test_hydros_action_scores.py` | ok | 0.208 |
| `test_hydros_ontology.py` | ok | 2.638 |
| `test_hydros_aps_safety.py` | ok | 4.408 |
| `test_hydros_aps_governance.py` | ok | 0.214 |
| `test_hydros_persistence.py` | ok | 2.865 |
| `test_hydros_interface.py` | ok | 2.661 |
| `test_hydros_release_readiness.py` | ok | 0.177 |

## Pipeline experimental

| Script | Status | Tempo (s) |
|---|---:|---:|
| `run_dssat_comparison.py` | ok | 36.267 |
| `diagnostico_resultados.py` | ok | 2.588 |
| `test_hydros_article_outputs.py` | ok | 4.741 |

## Síntese

- Observações: **256**
- Execuções DSSAT: **2**
- Divergências entre modos: **6**

## Limitações

- DSSAT utilizado como benchmark de simulação.
- Somente duas execuções DSSAT no conjunto atual.
- Forte desbalanceamento entre classes.
- APS legado parcialmente fora do domínio nos cenários DSSAT.
- Ausência de avaliação em malha fechada.
- Resultados interpretados como prova de conceito.

## Artefatos

- `results\dssat_comparison\comparacao_detalhada.csv`: ok (141736 bytes)
- `results\dssat_comparison\metricas_resumo.csv`: ok (394 bytes)
- `results\dssat_comparison\matriz_confusao_historico.csv`: ok (308 bytes)
- `results\dssat_comparison\matriz_confusao_instantaneo.csv`: ok (309 bytes)
- `results\dssat_comparison\diagnostico\distribuicao_classes.csv`: ok (291 bytes)
- `results\dssat_comparison\diagnostico\metricas_multiclasse.csv`: ok (105 bytes)
- `results\dssat_comparison\diagnostico\metricas_binarias.csv`: ok (288 bytes)
- `results\dssat_comparison\diagnostico\comparacao_modos.csv`: ok (541 bytes)
- `results\dssat_comparison\artigo\table_main_metrics.csv`: ok (628 bytes)
- `results\dssat_comparison\artigo\table_divergent_cases.csv`: ok (2164 bytes)
- `results\dssat_comparison\artigo\table_reference_positive_events.csv`: ok (1891 bytes)
- `results\dssat_comparison\artigo\table_actions_without_reference_support.csv`: ok (511 bytes)
- `results\dssat_comparison\artigo\figure_metrics_comparison.png`: ok (109339 bytes)
- `results\dssat_comparison\artigo\figure_binary_confusion_matrix_historico.png`: ok (71958 bytes)
- `results\dssat_comparison\artigo\figure_binary_confusion_matrix_instantaneo.png`: ok (76427 bytes)
- `results\dssat_comparison\artigo\figure_reference_event_detection.png`: ok (95395 bytes)
- `results\dssat_comparison\artigo\figure_governance_indicators.png`: ok (166953 bytes)
- `results\dssat_comparison\artigo\experimental_results_summary.md`: ok (3146 bytes)

## SHA-256

- `src/config/hydros_terms.py`: `3469d4041553e65e4d03a6af09a7b79d8fc4c230b1e5c9183faed393c605d234`
- `src/core/contracts.py`: `0ef742024f5fdc2eb1494a4ab41591ad48981cf2e07ca6fb5bf42595a2274213`
- `src/services/hydros_engine.py`: `639e92c4b33bf51125d65d2ecaf58fc1bf8c29d8ee035f0a96806b2764249e19`
- `src/agents/aiec_agent.py`: `f587aa5d36ab280c7ed0f2ce93c4e91dab3800b5010139fa04c09df8f282abb8`
- `src/agents/arg_agent.py`: `93843d86015952693c05ad5a4fed3a29c1c87339de61d0311bda71472e2baaf2`
- `src/agents/aps_agent.py`: `3c0f62fa752d35a42d7f8aed04dfcba8beb8b8154adffd9da25571e182b3b92c`
- `src/agents/amdh_agent.py`: `ab85a44e72caf74f568db6a7b68e90128776dae2470f196e4ebf06b6ff5c3616`
- `src/ontology/hydros_onto.py`: `88dce002590e189883d4cebf9612663374f78b0fd64f794ee298b6b3e5c6b020`
- `ontology/hydros_onto.ttl`: `143fe1cb8854f21d378579278a291e6efba9bf12fdf27d43d7236f78f26592d1`
- `src/integrations/dssat_adapter.py`: `6b345203f815adda2da7de192e26d3a42ae406bd04245556de12fead9de1d550`
- `data/hydros_soja_dssat_real_v2.csv`: `c9ade44520105a2367fe96b1d42f0a875499fb5ad68206d6f6a3d3518921bbd2`
