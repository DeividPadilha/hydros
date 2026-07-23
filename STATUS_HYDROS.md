# Status do Hydros — versão 0.3.0-agentic

## Estado geral

O núcleo do protótipo está funcional e alinhado à arquitetura da proposta de
tese para uma avaliação preliminar.

## Implementado

- representação da unidade de manejo e do histórico de contexto;
- modos Histórico e Instantâneo;
- seis agentes especializados;
- integração contextual pelo AIEC;
- regras agronômicas pelo ARG;
- inferências semânticas rastreáveis da HydrosOnto;
- APS com identificação de domínio, versão e hash do modelo;
- governança contrafactual da influência do APS;
- AMDH com escore individual para cinco ações e seleção por `argmax`;
- estado explícito da irrigação;
- confiança, completude, qualidade e conflito;
- revisão humana baseada em risco;
- persistência integral da execução;
- aceite, modificação e rejeição pelo usuário;
- interface Streamlit;
- adaptador DSSAT;
- comparação Histórico × Instantâneo;
- diagnóstico científico;
- tabelas e figuras para o artigo;
- testes funcionais e scripts de reprodutibilidade.

## Testes aprovados

```text
test_hydros_model_flow.py
test_hydros_modes.py
test_hydros_algorithms.py
test_hydros_scenarios.py
test_dssat_adapter.py
test_hydros_traceability.py
test_hydros_evidence_quality.py
test_hydros_action_scores.py
test_hydros_ontology.py
test_hydros_aps_safety.py
test_hydros_aps_governance.py
test_hydros_persistence.py
test_hydros_interface.py
test_hydros_article_outputs.py
```

## Resultado experimental congelado

### Multiclasse

| Métrica | Histórico | Instantâneo |
|---|---:|---:|
| Acurácia | 0,9609 | 0,9531 |
| Acurácia balanceada | 0,6757 | 0,4980 |
| MCC | 0,4408 | -0,0066 |
| F1 macro | 0,2960 | 0,1952 |
| Kappa de Cohen | 0,4281 | -0,0036 |

### Intensificação da irrigação

| Métrica | Histórico | Instantâneo |
|---|---:|---:|
| Verdadeiros positivos | 4 | 0 |
| Falsos positivos | 1 | 0 |
| Falsos negativos | 7 | 11 |
| Precisão | 0,8000 | 0,0000 |
| Recall | 0,3636 | 0,0000 |
| F1 | 0,5000 | 0,0000 |
| Acurácia balanceada | 0,6798 | 0,5000 |
| MCC | 0,5269 | 0,0000 |

### Governança

| Indicador | Histórico | Instantâneo |
|---|---:|---:|
| Confiança média | 0,3477 | 0,3516 |
| Conflito médio | 0,5195 | 0,3372 |
| Revisão humana | 0,1289 | 0,0039 |
| Compatibilidade média do APS | 0,5288 | 0,5169 |
| Peso efetivo médio do APS | 0,3007 | 0,3236 |
| Dependência material do APS | 0,1094 | 0,0039 |

Foram observadas seis divergências entre os modos, sendo quatro favoráveis ao
Histórico e duas favoráveis ao Instantâneo segundo a referência experimental.

## O que não está concluído

- retreinamento científico do APS com trajetórias independentes;
- geração de cenários DSSAT suficientes para as cinco ações;
- análise de sensibilidade dos pesos e limiares;
- avaliação em malha fechada de água, estresse e produtividade;
- validação com especialistas;
- teste de aceitação com usuários;
- extensão da HydrosOnto para outras culturas e operações.

## Classificação correta da versão

Esta versão é:

> protótipo funcional e rastreável, adequado para apresentação arquitetural e
> análise experimental preliminar.

Esta versão não é:

> sistema agronomicamente validado para uso operacional em propriedades rurais.
