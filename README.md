# Hydros

Hydros é um protótipo computacional de apoio à decisão hídrica em agricultura digital.

O objetivo do Hydros é analisar históricos de contextos agrícolas associados a unidades de manejo, representadas como talhões, e gerar recomendações relacionadas ao manejo da irrigação.

O modelo utiliza agentes inteligentes, regras agronômicas, aprendizado de máquina supervisionado e um motor de decisão híbrido.

## Status do projeto

Status atual:

Protótipo funcional em desenvolvimento.

O núcleo do modelo Hydros já está implementado e testado com dados sintéticos iniciais.

## Fluxo geral do modelo

O fluxo principal implementado é:

H(Ui) -> C(t) -> Agentes especializados -> AIEC -> ARG -> APS -> AMDH -> D(Ui)

Onde:

- H(Ui): histórico de contexto da unidade de manejo Ui;
- C(t): contexto agrícola observado no instante t;
- AIEC: Agente Integrador de Evidências Contextuais;
- ARG: Agente de Regras Agronômicas;
- APS: Agente Preditivo Supervisionado;
- AMDH: Agente Motor de Decisão Híbrido;
- D(Ui): decisão final de manejo hídrico.

## Estrutura do contexto agrícola

Cada contexto agrícola C(t) representa um registro temporal do talhão.

As variáveis principais são:

- loc: localização geográfica;
- solo: tipo de solo;
- p: precipitação;
- temp: temperatura média;
- gd: graus-dia ou soma térmica;
- et: evapotranspiração;
- kc: coeficiente de cultura;
- us: umidade do solo;
- ad: água disponível no solo;
- irr: irrigação aplicada;
- ef: estágio fenológico;
- eh: estresse hídrico;
- prod: produtividade estimada.

No CSV, essas variáveis são representadas por nomes descritivos:

- loc
- solo
- precipitacao
- temperatura
- graus_dia
- evapotranspiracao
- coeficiente_cultura
- umidade_solo
- agua_disponivel
- irrigacao_aplicada
- estagio_fenologico
- estresse_hidrico
- produtividade

O software também utiliza a coluna cultura, pois a cultura agrícola analisada influencia a interpretação do contexto.

## Agentes especializados

O Hydros possui os seguintes agentes especializados:

- Aclim: Agente Climático;
- Ahid: Agente Hídrico;
- Afen: Agente Fenológico;
- Ageo: Agente Geográfico;
- Aprod: Agente Produtivo;
- Ahist: Agente Histórico-Contextual.

As evidências geradas são:

- Eclim: evidência climática;
- Ehid: evidência hídrica;
- Efen: evidência fenológica;
- Egeo: evidência geográfica;
- Eprod: evidência produtiva;
- Ehist: evidência histórico-contextual.

## AIEC

O AIEC integra as evidências produzidas pelos agentes especializados.

Entrada:

E = {Eclim, Ehid, Efen, Egeo, Eprod, Ehist}

Saída:

Ehc

A evidência Ehc representa a evidência contextual consolidada.

## ARG

O ARG é o Agente de Regras Agronômicas.

Ele aplica o conjunto de regras R sobre o vetor de atributos Xt e gera a evidência agronômica Earg.

Regras implementadas:

- r1: precipitação recente ou acumulada;
- r2: disponibilidade de água no solo;
- r3: umidade do solo;
- r4: estágio fenológico e coeficiente de cultura;
- r5: evapotranspiração e tendência de redução da água disponível;
- r6: ocorrência de estresse hídrico;
- r7: efeitos da irrigação aplicada anteriormente;
- r8: tendência histórica da condição hídrica.

Saída:

Earg

## APS

O APS é o Agente Preditivo Supervisionado.

Ele utiliza aprendizado de máquina supervisionado para gerar a evidência preditiva Eaps.

O modelo inicial utilizado é Random Forest.

Entrada:

Xt = F(H(Ui))

Saída:

Eaps

Arquivos principais:

- src/services/feature_extractor.py
- src/models/train_aps_model.py
- src/agents/aps_agent.py

## AMDH

O AMDH é o Agente Motor de Decisão Híbrido.

Ele integra:

- Ehc;
- Earg;
- Eaps.

A decisão final é representada como:

D(Ui) = φ(Ehc, Earg, Eaps)

Decisões possíveis:

- iniciar_irrigacao;
- manter_irrigacao;
- aumentar_irrigacao;
- reduzir_irrigacao;
- finalizar_irrigacao.

## Estrutura principal do projeto

hydros/
  app.py
  README.md
  STATUS_HYDROS.md
  DOCUMENTACAO_CODIGO_HYDROS.md
  requirements.txt
  data/
    historico_contexto_exemplo.csv
    historico_treinamento_aps.csv
  src/
    agents/
      aclim_agent.py
      ahid_agent.py
      afen_agent.py
      ageo_agent.py
      aprod_agent.py
      ahist_agent.py
      aiec_agent.py
      arg_agent.py
      aps_agent.py
      amdh_agent.py
    config/
      hydros_terms.py
    services/
      data_loader.py
      validator.py
      hydros_engine.py
      feature_extractor.py
    database/
      database.py
    models/
      generate_training_data.py
      train_aps_model.py

## Como instalar

Criar ambiente virtual:

python -m venv .venv-1

Ativar ambiente virtual no Windows PowerShell:

.\.venv-1\Scripts\Activate.ps1

Instalar dependências:

pip install -r requirements.txt

## Como treinar o APS

O modelo APS usa arquivos .pkl gerados localmente.

Para treinar:

python -m src.models.train_aps_model

## Como testar o fluxo do modelo

Executar:

python test_hydros_model_flow.py

Esse teste executa:

H(Ui) -> agentes especializados -> AIEC -> ARG -> APS -> AMDH -> D(Ui)

## Como rodar a interface

Executar:

streamlit run app.py

Depois, carregar o arquivo CSV de histórico de contexto.

## Bases de dados

O Hydros pode usar diferentes fontes de dados, desde que sejam convertidas para o formato de histórico de contexto agrícola.

Exemplos:

- dados sintéticos;
- dados simulados;
- bases públicas;
- sensores IoT;
- bases agrícolas históricas;
- cenários gerados futuramente pelo DSSAT.

O DSSAT será tratado como etapa futura e final da pesquisa, não como dependência obrigatória do protótipo atual.

## HydrosOnto

A HydrosOnto faz parte da proposta conceitual, mas não será implementada nesta etapa do protótipo.

Ela poderá ser desenvolvida em uma etapa futura.

## Pendências

Pendências atuais:

- melhorar explicação operacional do AMDH;
- atualizar a documentação técnica completa;
- criar cenários de teste;
- criar teste automático dos cenários;
- revisar requirements.txt;
- validar o protótipo com diferentes entradas;
- futuramente integrar bases externas e cenários DSSAT.

## Conclusão

O Hydros já possui o núcleo funcional do modelo computacional proposto.

O protótipo atual implementa histórico de contexto, agentes especializados, integração contextual, regras agronômicas, predição supervisionada e decisão híbrida.

## Seleção de algoritmo no APS

O Agente Preditivo Supervisionado (APS) foi implementado de forma parametrizável.

Por padrão, o Hydros utiliza Random Forest. Entretanto, a interface permite selecionar outros algoritmos supervisionados para comparação experimental.

Algoritmos disponíveis:

- Random Forest;
- Gradient Boosting;
- Decision Tree.

O fluxo conceitual permanece o mesmo:

Xt = F(H(Ui))
Eaps = M(Xt)

A diferença é que o modelo supervisionado M pode ser alterado pelo usuário na interface.

Para treinar todos os modelos APS:

python -m src.models.train_aps_model

Para testar os algoritmos:

python test_hydros_algorithms.py
