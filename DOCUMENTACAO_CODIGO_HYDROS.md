# Documentação do Código do Hydros

## 1. Visão geral

O Hydros é um protótipo em Python para apoio à decisão hídrica em agricultura digital.

O sistema analisa históricos de contexto agrícola associados a unidades de manejo, representadas como talhões, e gera uma recomendação relacionada ao manejo da irrigação.

A decisão final pode indicar:

```text
iniciar_irrigacao
manter_irrigacao
aumentar_irrigacao
reduzir_irrigacao
finalizar_irrigacao
```

O código foi organizado de forma modular para permitir evolução gradual do modelo, pois a proposta científica ainda poderá receber ajustes nas regras agronômicas, na matemática do motor híbrido, no uso do DSSAT e na estrutura dos agentes.

## 2. Estrutura geral do projeto

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

## 3. Padrão atual do histórico de contexto

O histórico de contexto é a entrada principal do Hydros.

Cada linha do CSV representa um contexto agrícola observado em determinado instante para uma unidade de manejo.

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

## 4. Significado das variáveis

```text
data: data do registro temporal
talhao: unidade de manejo analisada
cultura: cultura agrícola utilizada
loc: localização da unidade de manejo
solo: tipo de solo
precipitacao: precipitação observada ou acumulada
temperatura: temperatura média
graus_dia: soma térmica ou graus dia
evapotranspiracao: evapotranspiração
coeficiente_cultura: coeficiente de cultura
umidade_solo: umidade do solo
agua_disponivel: água disponível no solo
irrigacao_aplicada: lâmina de irrigação aplicada
estagio_fenologico: estágio fenológico da cultura
estresse_hidrico: indicador de estresse hídrico
produtividade: produtividade estimada
```

Essas variáveis foram definidas para aproximar o software da proposta conceitual do Hydros, que representa cada contexto agrícola como um conjunto de variáveis climáticas, hídricas, edáficas, fenológicas, geográficas e produtivas.

## 5. app.py

O arquivo `app.py` é a interface principal do Hydros.

Ele utiliza Streamlit para criar o dashboard local.

Responsabilidades principais:

```text
exibir título e interface do Hydros
permitir upload do CSV
chamar o DataLoader
chamar o CSVValidator
executar o HydrosEngine
mostrar a decisão final
mostrar a confiança
mostrar o risco previsto
mostrar evidências dos agentes
mostrar explicabilidade
mostrar histórico de execuções
mostrar gráficos do histórico
salvar a execução no SQLite
```

O `app.py` não deve concentrar a lógica científica do modelo. Ele deve apenas organizar a interação com o usuário e exibir os resultados calculados pelos demais componentes.

## 6. DataLoader

Arquivo:

```text
src/services/data_loader.py
```

Responsabilidade:

```text
carregar o arquivo CSV enviado pelo usuário
converter o CSV em DataFrame do Pandas
retornar o DataFrame para o app.py
```

O DataLoader mantém a leitura de dados separada da interface.

## 7. CSVValidator

Arquivo:

```text
src/services/validator.py
```

Responsabilidade:

```text
validar se o CSV está vazio
validar colunas obrigatórias
validar campos vazios
validar data
validar colunas numéricas
validar valores negativos
validar coeficiente de cultura
validar umidade do solo
```

O validador foi atualizado para aceitar o novo padrão do histórico de contexto do Hydros.

Colunas obrigatórias atuais:

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

Colunas numéricas atuais:

```text
precipitacao
temperatura
graus_dia
evapotranspiracao
coeficiente_cultura
umidade_solo
agua_disponivel
irrigacao_aplicada
produtividade
```

## 8. HydrosEngine

Arquivo:

```text
src/services/hydros_engine.py
```

Responsabilidade:

```text
receber o DataFrame validado
obter o contexto agrícola mais recente
executar o AGR
executar o AHC
executar o ACL
executar o AMDH
retornar todos os resultados para o app.py
```

O HydrosEngine funciona como orquestrador do processo de decisão.

Fluxo simplificado:

```text
DataFrame
↓
AGR
↓
AHC
↓
ACL
↓
AMDH
↓
resultado final
```

## 9. AGR

Arquivo:

```text
src/agents/agr_agent.py
```

Nome no código:

```text
AGR
```

Correspondência conceitual na proposta:

```text
ARG
Agente de Regras Agronômicas
```

Responsabilidade:

```text
analisar a janela recente do histórico de contexto
aplicar regras agronômicas
calcular score agronômico
gerar criticidade agronômica
gerar recomendação parcial
produzir evidência para o AMDH
```

Variáveis utilizadas atualmente:

```text
precipitacao
evapotranspiracao
umidade_solo
agua_disponivel
irrigacao_aplicada
estagio_fenologico
```

Saída principal:

```text
agente
criticidade
evidencia
score_agronomico
confianca
recomendacao
decisao
prioridade
regras_acionadas
motivo
```

Observação:

As regras atuais são provisórias. Elas deverão ser revisadas com base na literatura, nos cenários do DSSAT e em outras bases agrícolas.

## 10. AHC

Arquivo:

```text
src/agents/ahc_agent.py
```

Nome conceitual:

```text
Agente Histórico de Contexto
```

Responsabilidade:

```text
analisar o histórico do talhão
buscar contextos semelhantes
avaliar tendências recentes
identificar padrão histórico de criticidade
gerar evidência histórica
```

Variáveis usadas atualmente na comparação:

```text
temperatura
precipitacao
umidade_solo
evapotranspiracao
agua_disponivel
```

Saída principal:

```text
agente
criticidade
evidencia
contextos_similares
tendencia_contextos
tendencia_umidade
tendencia_agua_disponivel
score_historico
recomendacao
motivo
```

Observação:

O AHC atual é uma versão inicial. Futuramente ele deverá considerar mais atributos históricos, como precipitação acumulada, evapotranspiração acumulada, variação de umidade, persistência de estresse hídrico e janelas temporais configuráveis.

## 11. ACL

Arquivo:

```text
src/agents/acl_agent.py
```

Nome no código:

```text
ACL
```

Correspondência conceitual na proposta:

```text
APS
Agente Preditivo Supervisionado
```

Responsabilidade:

```text
carregar o modelo Random Forest treinado
carregar os encoders
preparar o contexto agrícola atual
converter variáveis textuais em valores numéricos
classificar a criticidade hídrica
gerar evidência preditiva
```

Features usadas atualmente:

```text
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
produtividade
```

Arquivos carregados pelo ACL:

```text
src/models/hydros_acl_model.pkl
src/models/label_encoder.pkl
src/models/cultura_encoder.pkl
src/models/loc_encoder.pkl
src/models/solo_encoder.pkl
src/models/fenologico_encoder.pkl
```

Saída principal:

```text
agente
nome_arquivo
modelo
risco_previsto
criticidade
evidencia
confianca
features_usadas
motivo
```

Observação:

Apesar do nome ACL permanecer no código, esse componente representa a implementação inicial do APS descrito na proposta.

## 12. AMDH

Arquivo:

```text
src/agents/amdh_agent.py
```

Nome conceitual:

```text
Agente Motor de Decisão Híbrido
```

Responsabilidade:

```text
receber evidências dos agentes
converter criticidades em valores numéricos
aplicar pesos
calcular score híbrido
gerar decisão final
gerar explicação textual
```

No software atual, o AMDH recebe evidências de:

```text
AGR
AHC
ACL
```

Na proposta conceitual, o AMDH deverá receber:

```text
Ehc
Earg
Eaps
```

Mapeamento atual:

```text
AGR representa Earg
AHC representa uma evidência histórica inicial
ACL representa Eaps
```

Ponto futuro:

Criar o AIEC para gerar `Ehc`, evidência contextual consolidada.

## 13. Banco de dados SQLite

Arquivo:

```text
src/database/database.py
```

Banco gerado:

```text
hydros.db
```

Responsabilidade:

```text
criar tabela de execuções
salvar cada execução do Hydros
listar histórico de execuções
```

Campos salvos:

```text
data_execucao
talhao
decisao_final
confianca
risco_previsto
explicacao
```

O banco permite manter registro local das análises realizadas no dashboard.

## 14. generate_training_data.py

Arquivo:

```text
src/models/generate_training_data.py
```

Responsabilidade:

```text
gerar base sintética de treinamento
simular variáveis agrícolas
gerar estresse hídrico sintético
salvar historico_treinamento_acl.csv
```

A base sintética atual já segue o novo padrão do histórico de contexto.

Variáveis geradas:

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

Observação:

A regra usada para gerar `estresse_hidrico` ainda é provisória.

## 15. train_acl_model.py

Arquivo:

```text
src/models/train_acl_model.py
```

Responsabilidade:

```text
carregar base de treinamento
codificar variáveis textuais
definir features
definir alvo
treinar Random Forest
avaliar acurácia
salvar modelo treinado
salvar encoders
```

Features atuais do modelo:

```text
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
produtividade
```

Alvo:

```text
estresse_hidrico
```

Arquivos gerados:

```text
hydros_acl_model.pkl
label_encoder.pkl
cultura_encoder.pkl
loc_encoder.pkl
solo_encoder.pkl
fenologico_encoder.pkl
```

## 16. Fluxo geral do Hydros

```text
CSV de histórico de contexto
↓
DataLoader
↓
CSVValidator
↓
HydrosEngine
↓
AGR
↓
AHC
↓
ACL
↓
AMDH
↓
Decisão final
↓
Dashboard
↓
SQLite
```

## 17. Relação entre código atual e proposta conceitual

O código atual já possui uma implementação funcional simplificada do modelo Hydros.

Relação entre nomes do código e nomes conceituais:

```text
AGR no código representa ARG na proposta
ACL no código representa APS na proposta
AHC no código representa o agente histórico de contexto
AMDH no código representa o motor de decisão híbrido
```

Ainda falta implementar explicitamente:

```text
Agente Climático
Agente Hídrico
Agente Fenológico
Agente Geográfico
Agente Produtivo
Agente Integrador de Evidências Contextuais
```

## 18. Próximas evoluções planejadas

Próximos passos técnicos:

```text
criar AIEC
melhorar AHC
melhorar regras agronômicas
calcular atributos históricos para o APS
adaptar saída do DSSAT
melhorar banco de dados
separar melhor evidências e decisões
preparar repositório GitHub
```

Próximos passos científicos:

```text
validar regras com literatura
validar variáveis com DSSAT
definir janelas temporais
definir pesos do AMDH
definir limiares de decisão
definir cenários de avaliação
comparar decisões com cenários esperados
```

## 19. Status atual do software

Status atual:

```text
protótipo funcional
CSV ampliado
validador atualizado
base sintética atualizada
Random Forest treinado
ACL atualizado como implementação inicial do APS
dashboard funcionando
histórico local em SQLite
documentação inicial atualizada
```

## 20. Observação final

O Hydros ainda está em desenvolvimento. A versão atual deve ser entendida como um protótipo funcional para apoiar a evolução da proposta de tese.

A estrutura modular do código permite que novas regras, novos agentes, novos dados do DSSAT e novos mecanismos de decisão sejam incorporados sem reescrever todo o sistema.
