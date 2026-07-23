# Síntese experimental do Hydros

## Configuração

A avaliação preliminar utilizou **256 observações**, provenientes de **2 execuções DSSAT**. A referência contém 245 observações de `manter_irrigacao` e 11 de `iniciar_irrigacao`, caracterizando forte desbalanceamento e cobertura de apenas duas das cinco ações previstas pelo Hydros.

## Detecção de intensificação da irrigação

| Métrica | Hydros Histórico | Hydros Instantâneo |
|---|---:|---:|
| Precisão | 0.8000 | 0.0000 |
| Recall | 0.3636 | 0.0000 |
| F1 | 0.5000 | 0.0000 |
| Acurácia balanceada | 0.6798 | 0.5000 |
| MCC | 0.5269 | 0.0000 |

O Hydros Histórico identificou 4 eventos positivos, enquanto o Hydros Instantâneo não identificou eventos de intensificação. O resultado indica contribuição preliminar da memória temporal, mas o recall histórico de 0.3636 mostra que parte relevante dos eventos ainda não foi detectada.

## Divergências entre os modos

Foram observadas **6 divergências** (2.34% das observações). Em 4 casos, o modo Histórico concordou com a referência e o Instantâneo divergiu. Em 2 casos ocorreu o inverso. Portanto, a vantagem do histórico não é uniforme e deve ser discutida caso a caso.

## Governança e APS

A confiança média foi 0.3477 no modo Histórico e 0.3516 no Instantâneo. A taxa de revisão humana especial foi 12.89% e 0.39%, respectivamente. A compatibilidade média do APS com o domínio de avaliação permaneceu próxima de 0,5, confirmando que o modelo preditivo legado opera parcialmente fora do domínio de treinamento. Por isso, o peso efetivo do APS foi reduzido e sua contribuição deve ser apresentada como experimental.

## Limitações obrigatórias para o artigo

1. O DSSAT funciona como **benchmark de simulação**, não como verdade agronômica absoluta.
2. A referência contém somente `manter_irrigacao` e `iniciar_irrigacao`; portanto, não valida plenamente as cinco ações do Hydros.
3. Foram registradas 3 predições de ações sem ocorrência correspondente na referência. Elas devem ser analisadas como casos exploratórios, não simplesmente como classes validadas.
4. O conjunto possui somente duas execuções e forte desbalanceamento. A acurácia isolada não é suficiente; F1, acurácia balanceada, MCC e análise dos casos divergentes são prioritários.
5. Os resultados não demonstram ainda redução efetiva do consumo de água, do estresse hídrico ou aumento de produtividade, pois as recomendações não foram realimentadas no DSSAT em malha fechada.
6. O APS atual é legado e requer retreinamento com separação por trajetória, safra ou cenário independente antes de sustentar conclusões preditivas gerais.

## Interpretação defensável

Os resultados oferecem **evidência preliminar de prova de conceito** de que o histórico de contexto pode alterar decisões e recuperar eventos de necessidade de irrigação não identificados pela configuração instantânea. A conclusão deve permanecer restrita ao conjunto simulado analisado e não deve ser apresentada como validação agronômica definitiva.
