# Status Atual do Software Hydros

## Status geral

O Hydros está atualmente como um protótipo funcional alinhado ao modelo computacional da tese.

O sistema já possui o fluxo principal:

H(Ui) -> C(t) -> agentes especializados -> AIEC -> ARG -> APS -> AMDH -> D(Ui)

## Componentes implementados

### Entrada de dados

- Upload de CSV pelo Streamlit.
- Validação das colunas obrigatórias.
- Representação do histórico de contexto H(Ui).
- Representação do contexto agrícola C(t).

### Agentes especializados

- Aclim -> Eclim
- Ahid -> Ehid
- Afen -> Efen
- Ageo -> Egeo
- Aprod -> Eprod
- Ahist -> Ehist

### Agente Integrador de Evidências Contextuais

- AIEC integra Eclim, Ehid, Efen, Egeo, Eprod e Ehist.
- Saída gerada: Ehc.

### Agente de Regras Agronômicas

- ARG aplica o conjunto de regras R.
- Regras implementadas: r1 até r8.
- Saída gerada: Earg.
- Escore calculado: ScoreARG.

### Agente Preditivo Supervisionado

- APS usa Random Forest.
- Entrada: Xt = F(H(Ui)).
- Saída gerada: Eaps.
- O modelo foi treinado com dados sintéticos iniciais.

### Agente Motor de Decisão Híbrido

- AMDH integra Ehc, Earg e Eaps.
- Calcula o Score final.
- Gera a decisão D(Ui).

Decisões possíveis:

- iniciar_irrigacao
- manter_irrigacao
- aumentar_irrigacao
- reduzir_irrigacao
- finalizar_irrigacao

## Interface

A interface Streamlit já apresenta:

- resumo da análise;
- decisão final;
- confiança;
- risco previsto;
- explicação da decisão;
- evidências dos agentes especializados;
- painel dos agentes principais;
- histórico de execuções;
- gráficos do histórico de contexto.

## Arquivos principais

- app.py
- src/services/hydros_engine.py
- src/services/feature_extractor.py
- src/config/hydros_terms.py
- src/agents/aclim_agent.py
- src/agents/ahid_agent.py
- src/agents/afen_agent.py
- src/agents/ageo_agent.py
- src/agents/aprod_agent.py
- src/agents/ahist_agent.py
- src/agents/aiec_agent.py
- src/agents/arg_agent.py
- src/agents/aps_agent.py
- src/agents/amdh_agent.py
- src/models/train_aps_model.py
- test_hydros_model_flow.py

## Pendências

O software ainda precisa de:

- melhorar a documentação técnica;
- calibrar pesos e limiares;
- melhorar a base sintética de treinamento;
- balancear melhor a classe critico no APS;
- integrar cenários DSSAT;
- documentar ou implementar a HydrosOnto;
- criar mais testes de funcionalidade;
- realizar avaliação com especialistas ou usuários.

## Conclusão

O Hydros já está funcional como protótipo computacional do modelo proposto.

Ele ainda não é uma versão final validada cientificamente, mas já implementa o núcleo do modelo Hydros.

## Validação final do protótipo

O protótipo funcional do Hydros foi validado com sucesso.

Testes executados:

- python -m compileall app.py src
- python test_hydros_model_flow.py
- python test_hydros_scenarios.py
- streamlit run app.py

Resultado:

- fluxo principal executado com sucesso;
- cenários funcionais aprovados;
- interface Streamlit executada;
- decisão final D(Ui) gerada corretamente;
- evidências Ehc, Earg e Eaps integradas pelo AMDH;
- documentação atualizada;
- termos antigos removidos da interface e da documentação.

Status final:

Protótipo funcional do Hydros finalizado.

## Atualização 0.2.0 - Seleção de algoritmo no APS

Foi adicionada ao Hydros a possibilidade de selecionar o algoritmo supervisionado utilizado pelo Agente Preditivo Supervisionado (APS).

Algoritmos disponíveis:

- Random Forest, mantido como algoritmo padrão;
- Gradient Boosting;
- Decision Tree.

A alteração mantém a estrutura conceitual do modelo Hydros, pois o APS continua gerando a evidência Eaps a partir do vetor Xt extraído do histórico de contexto H(Ui).

Formalmente:

- Xt = F(H(Ui))
- Eaps = M(Xt)

Nesta versão, M pode ser instanciado por diferentes algoritmos supervisionados de classificação.

Testes realizados:

- treinamento dos três algoritmos;
- execução do fluxo principal do Hydros;
- execução dos cenários funcionais;
- execução do teste comparativo dos algoritmos APS;
- seleção do algoritmo pela interface Streamlit.

Resultado:

Todos os algoritmos APS executaram corretamente e produziram Eaps, permitindo ao AMDH gerar D(Ui).

## Atualização 0.2.0 - Seleção de algoritmo no APS

Foi adicionada ao Hydros a possibilidade de selecionar o algoritmo supervisionado utilizado pelo Agente Preditivo Supervisionado (APS).

Algoritmos disponíveis:

- Random Forest, mantido como algoritmo padrão;
- Gradient Boosting;
- Decision Tree.

A alteração mantém a estrutura conceitual do modelo Hydros, pois o APS continua gerando a evidência Eaps a partir do vetor Xt extraído do histórico de contexto H(Ui).

Formalmente:

- Xt = F(H(Ui))
- Eaps = M(Xt)

Nesta versão, M pode ser instanciado por diferentes algoritmos supervisionados de classificação.

Testes realizados:

- treinamento dos três algoritmos;
- execução do fluxo principal do Hydros;
- execução dos cenários funcionais;
- execução do teste comparativo dos algoritmos APS;
- seleção do algoritmo pela interface Streamlit.

Resultado:

Todos os algoritmos APS executaram corretamente e produziram Eaps, permitindo ao AMDH gerar D(Ui).

## Atualização 0.2.0 - Seleção de algoritmo no APS

Foi adicionada ao Hydros a possibilidade de selecionar o algoritmo supervisionado utilizado pelo Agente Preditivo Supervisionado (APS).

Algoritmos disponíveis:

- Random Forest, mantido como algoritmo padrão;
- Gradient Boosting;
- Decision Tree.

A alteração mantém a estrutura conceitual do modelo Hydros, pois o APS continua gerando a evidência Eaps a partir do vetor Xt extraído do histórico de contexto H(Ui).

Formalmente:

- Xt = F(H(Ui))
- Eaps = M(Xt)

Nesta versão, M pode ser instanciado por diferentes algoritmos supervisionados de classificação.

Testes realizados:

- treinamento dos três algoritmos;
- execução do fluxo principal do Hydros;
- execução dos cenários funcionais;
- execução do teste comparativo dos algoritmos APS;
- seleção do algoritmo pela interface Streamlit.

Resultado:

Todos os algoritmos APS executaram corretamente e produziram Eaps, permitindo ao AMDH gerar D(Ui).

## Atualização 0.2.0 - Seleção de algoritmo no APS

Foi adicionada ao Hydros a possibilidade de selecionar o algoritmo supervisionado utilizado pelo Agente Preditivo Supervisionado (APS).

Algoritmos disponíveis:

- Random Forest, mantido como algoritmo padrão;
- Gradient Boosting;
- Decision Tree.

A alteração mantém a estrutura conceitual do modelo Hydros, pois o APS continua gerando a evidência Eaps a partir do vetor Xt extraído do histórico de contexto H(Ui).

Formalmente:

- Xt = F(H(Ui))
- Eaps = M(Xt)

Nesta versão, M pode ser instanciado por diferentes algoritmos supervisionados de classificação.

Testes realizados:

- treinamento dos três algoritmos;
- execução do fluxo principal do Hydros;
- execução dos cenários funcionais;
- execução do teste comparativo dos algoritmos APS;
- seleção do algoritmo pela interface Streamlit.

Resultado:

Todos os algoritmos APS executaram corretamente e produziram Eaps, permitindo ao AMDH gerar D(Ui).

Status:

Hydros 0.2.0 validado.
