# Documentação Técnica do Código Hydros

## 1. Objetivo

O Hydros é um protótipo computacional para apoio à decisão hídrica em agricultura digital.

O software implementa o núcleo do modelo Hydros por meio de históricos de contexto agrícola, agentes inteligentes, regras agronômicas, aprendizado de máquina supervisionado e motor híbrido de decisão.

## 2. Fluxo principal

O fluxo implementado é:

H(Ui) -> C(t) -> agentes especializados -> AIEC -> ARG -> APS -> AMDH -> D(Ui)

Onde:

- H(Ui) representa o histórico de contexto da unidade de manejo.
- C(t) representa o contexto agrícola no instante t.
- AIEC integra as evidências contextuais.
- ARG aplica regras agronômicas.
- APS executa a predição supervisionada.
- AMDH gera a decisão final.
- D(Ui) representa a decisão de manejo hídrico.

## 3. Estrutura do contexto

Cada linha do CSV representa um contexto agrícola.

Colunas esperadas:

- data
- talhao
- cultura
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

## 4. Agentes especializados

O Hydros possui os seguintes agentes especializados:

- Aclim: Agente Climático.
- Ahid: Agente Hídrico.
- Afen: Agente Fenológico.
- Ageo: Agente Geográfico.
- Aprod: Agente Produtivo.
- Ahist: Agente Histórico-Contextual.

Evidências geradas:

- Eclim: evidência climática.
- Ehid: evidência hídrica.
- Efen: evidência fenológica.
- Egeo: evidência geográfica.
- Eprod: evidência produtiva.
- Ehist: evidência histórico-contextual.

## 5. AIEC

Arquivo:

src/agents/aiec_agent.py

O AIEC integra:

- Eclim
- Ehid
- Efen
- Egeo
- Eprod
- Ehist

Saída:

- Ehc

Ehc representa a evidência contextual consolidada.

## 6. ARG

Arquivo:

src/agents/arg_agent.py

O ARG aplica regras agronômicas e gera:

- Earg
- ScoreARG

Regras implementadas:

- r1: precipitação recente ou acumulada.
- r2: disponibilidade de água no solo.
- r3: umidade do solo.
- r4: estágio fenológico e coeficiente de cultura.
- r5: evapotranspiração e tendência de redução da água disponível.
- r6: ocorrência de estresse hídrico.
- r7: efeitos da irrigação aplicada anteriormente.
- r8: tendência histórica da condição hídrica.

## 7. APS

Arquivos:

- src/services/feature_extractor.py
- src/models/train_aps_model.py
- src/agents/aps_agent.py

O APS utiliza:

Xt = F(H(Ui))

O modelo inicial é Random Forest.

Saída:

- Eaps

Para treinar o modelo:

python -m src.models.train_aps_model

## 8. AMDH

Arquivo:

src/agents/amdh_agent.py

O AMDH integra:

- Ehc
- Earg
- Eaps

Fórmula conceitual:

D(Ui) = phi(Ehc, Earg, Eaps)

Score final:

Score = (whc * V(Ehc)) + (warg * V(Earg)) + (waps * V(Eaps))

Decisões possíveis:

- iniciar_irrigacao
- manter_irrigacao
- aumentar_irrigacao
- reduzir_irrigacao
- finalizar_irrigacao

## 9. Arquivo oficial de termos

Arquivo:

src/config/hydros_terms.py

Esse arquivo centraliza:

- agentes
- evidências
- variáveis
- fórmulas
- regras
- pesos
- limiares
- classes de decisão

## 10. Interface

Arquivo:

app.py

A interface usa Streamlit e permite:

- carregar CSV
- visualizar resumo da análise
- visualizar evidências dos agentes
- visualizar decisão final
- visualizar explicação
- visualizar gráficos do histórico
- salvar execuções no banco local

## 11. Banco de dados

Arquivo:

src/database/database.py

O banco armazena execuções realizadas pelo Hydros.

## 12. Dados

Arquivos principais:

- data/historico_contexto_exemplo.csv
- data/historico_treinamento_aps.csv

## 13. Teste principal

Arquivo:

test_hydros_model_flow.py

Para rodar:

python test_hydros_model_flow.py

Esse teste executa o fluxo completo do Hydros.

## 14. Fontes de dados

O Hydros pode usar diferentes fontes de dados, desde que sejam convertidas para o formato de histórico de contexto.

Exemplos:

- dados sintéticos
- dados simulados
- bases públicas
- sensores IoT
- bases agrícolas históricas
- cenários agrícolas futuros

A integração com DSSAT fica para uma etapa futura e final.

## 15. Ontologia

A HydrosOnto faz parte da proposta conceitual, mas não será implementada nesta etapa do protótipo.

## 16. Pendências

Pendências para finalizar o protótipo:

- melhorar a explicação operacional do AMDH
- criar cenários de teste
- criar teste automático dos cenários
- revisar requirements.txt
- rodar auditoria final
- validar execução no Streamlit

## 17. Conclusão

O Hydros já implementa o núcleo funcional do modelo computacional proposto.

O protótipo atual usa histórico de contexto, agentes especializados, integração contextual, regras agronômicas, predição supervisionada e decisão híbrida.
