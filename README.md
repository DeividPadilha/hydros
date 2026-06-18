# Hydros

Hydros é um protótipo em Python para apoio à decisão hídrica em agricultura digital.

O sistema analisa históricos de contexto agrícola associados a unidades de manejo, representadas como talhões, e gera recomendações para o manejo da irrigação.

A decisão final pode indicar uma das seguintes ações:

```text
iniciar_irrigacao
manter_irrigacao
aumentar_irrigacao
reduzir_irrigacao
finalizar_irrigacao
```

## Objetivo

Desenvolver um modelo computacional de apoio à decisão hídrica baseado em históricos de contextos agrícolas, agentes inteligentes, regras agronômicas e aprendizado de máquina.

## Tecnologias utilizadas

```text
Python
Streamlit
Pandas
Plotly
Scikit-learn
Joblib
SQLite
```

## Estrutura do projeto

```text
hydros/
  app.py
  README.md
  requirements.txt
  DOCUMENTACAO_CODIGO_HYDROS.md
  data/
    historico_contexto_exemplo.csv
    historico_treinamento_acl.csv
  src/
    agents/
      agr_agent.py
      ahc_agent.py
      acl_agent.py
      amdh_agent.py
    database/
      database.py
    models/
      generate_training_data.py
      train_acl_model.py
      hydros_acl_model.pkl
      label_encoder.pkl
      cultura_encoder.pkl
      loc_encoder.pkl
      solo_encoder.pkl
      fenologico_encoder.pkl
    services/
      data_loader.py
      validator.py
      hydros_engine.py
```

## Histórico de contexto

O Hydros utiliza um histórico de contexto agrícola como entrada.

Cada registro do histórico representa o estado de uma unidade de manejo em determinado instante.

O padrão atual do CSV é:

```text
data
talhao
cultura
loc
solo
precipitacao
temperatura
graus_dia
evapotranspiracao
coeficiente_cultura
umidade_solo
agua_disponivel
irrigacao_aplicada
estagio_fenologico
estresse_hidrico
produtividade
```

## Significado das variáveis

```text
data: data do registro
talhao: unidade de manejo analisada
cultura: cultura agrícola utilizada
loc: localização da unidade de manejo
solo: tipo de solo
precipitacao: precipitação em milímetros
temperatura: temperatura média
graus_dia: soma térmica ou graus dia
evapotranspiracao: evapotranspiração
coeficiente_cultura: coeficiente de cultura
umidade_solo: umidade do solo
agua_disponivel: água disponível no solo
irrigacao_aplicada: irrigação aplicada
estagio_fenologico: estágio fenológico da cultura
estresse_hidrico: indicador de estresse hídrico
produtividade: produtividade estimada
```

## Componentes principais

## app.py

Interface principal do Hydros criada com Streamlit.

Responsável por:

```text
carregar CSV
validar dados
executar o HydrosEngine
mostrar dashboard
mostrar decisão final
mostrar evidências dos agentes
mostrar gráficos
salvar histórico no SQLite
```

## DataLoader

Arquivo:

```text
src/services/data_loader.py
```

Responsável por carregar o CSV enviado pelo usuário.

## CSVValidator

Arquivo:

```text
src/services/validator.py
```

Responsável por validar se o CSV possui as colunas obrigatórias e os formatos esperados.

## HydrosEngine

Arquivo:

```text
src/services/hydros_engine.py
```

Responsável por orquestrar a execução dos agentes.

## AGR

Arquivo:

```text
src/agents/agr_agent.py
```

Agente de Regras Agronômicas.

No material conceitual, corresponde ao ARG.

Responsável por aplicar regras agronômicas sobre o histórico recente do talhão.

## AHC

Arquivo:

```text
src/agents/ahc_agent.py
```

Agente Histórico de Contexto.

Responsável por analisar contextos semelhantes e tendências históricas do talhão.

## ACL

Arquivo:

```text
src/agents/acl_agent.py
```

Agente Classificador.

No material conceitual, corresponde ao APS, Agente Preditivo Supervisionado.

Responsável por usar Random Forest para classificar a criticidade hídrica.

## AMDH

Arquivo:

```text
src/agents/amdh_agent.py
```

Agente Motor de Decisão Híbrido.

Responsável por integrar as evidências dos agentes e gerar a decisão final de manejo hídrico.

## Banco de dados

Arquivo:

```text
src/database/database.py
```

O Hydros usa SQLite para salvar o histórico das execuções.

Banco gerado:

```text
hydros.db
```

## Instalação

Criar ambiente virtual:

```bash
python -m venv .venv
```

Ativar ambiente virtual no Windows:

```bash
.venv\Scripts\Activate
```

Instalar dependências:

```bash
pip install -r requirements.txt
```

## Executar o Hydros

```bash
streamlit run app.py
```

## Gerar base sintética

```bash
python src\models\generate_training_data.py
```

## Treinar o modelo Random Forest

```bash
python src\models\train_acl_model.py
```

## Fluxo de execução

```text
CSV
↓
DataLoader
↓
CSVValidator
↓
HydrosEngine
↓
AGR
AHC
ACL
↓
AMDH
↓
Dashboard
↓
SQLite
```

## Estado atual

O Hydros está em fase de protótipo funcional.

Já implementado:

```text
upload de CSV
validação do histórico de contexto
interface Streamlit
dashboard visual
gráficos
AGR
AHC
ACL como implementação inicial do APS
AMDH
SQLite
histórico de execuções
Random Forest treinado
explicabilidade inicial
```

## Próximos passos

```text
criar AIEC
melhorar AHC
melhorar regras agronômicas
calcular atributos históricos para o APS
adaptar saídas do DSSAT
atualizar documentação científica
preparar repositório GitHub
```

## Observação

O código ainda utiliza alguns nomes da versão inicial do protótipo, como ACL e AGR.

Na proposta conceitual:

```text
ACL representa o APS
AGR representa o ARG
```

Essa decisão foi mantida temporariamente para evitar quebras no software durante a evolução do modelo.