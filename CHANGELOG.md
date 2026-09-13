# Changelog

## Atualização experimental e de reprodutibilidade — 2026-09-13

- organização dos artefatos científicos em duas gerações experimentais distintas:
  - IEEE MetroAgriFor 2026;
  - manuscrito atual direcionado inicialmente ao *Computers and Electronics in Agriculture*;
- preservação dos resultados e pacotes do MetroAgriFor sem sobrescrever a geração experimental anterior;
- inclusão dos artefatos do Experimento I do MetroAgriFor:
  - `experiments/metroagrifor_2026/experiment_01/`;
- inclusão dos artefatos do Experimento II do MetroAgriFor:
  - `experiments/metroagrifor_2026/experiment_02/`;
- inclusão do pacote reproduzível do Experimento I do manuscrito atual:
  - `Hydros_Experimento_01B_Verificado_Reproduzivel.zip`;
- inclusão do pacote final do Experimento II em ciclo fechado:
  - `Hydros_Experimento_02B_Holdout_Final_UFGA8501_CRLF_Corrigido.zip`;
- inclusão do relatório oficial do holdout UFGA8501;
- documentação da separação entre os resultados do MetroAgriFor e os resultados do manuscrito atual;
- atualização do `README.md`, `REPRODUCIBILITY.md` e `STATUS_HYDROS.md`;
- consolidação da validação automatizada em 52/52 testes com Pytest;
- registro do Experimento I atual com 108 trajetórias de soja, 6.480 contextos brutos e 6.048 amostras elegíveis;
- registro do ganho de macro F1 com Histórico de Contextos para Random Forest, Gradient Boosting e Decision Tree;
- registro do Experimento II em ciclo fechado com cenários de desenvolvimento UFGA7801 e UFGA8401 e holdout final UFGA8501;
- registro do holdout final com redução de 37,79% na irrigação bruta, retenção de produtividade de 97,74% e aumento do estresse hídrico;
- preservação explícita da regra de não recalibrar o Hydros a partir do holdout UFGA8501;
- atualização da documentação da HydrosOnto para 500 axiomas, 31 classes, 25 propriedades de objeto, 12 propriedades de dados e 44 indivíduos;
- registro da consistência lógica da HydrosOnto verificada com HermiT.

## 0.3.0-agentic — 2026-07-23

- contratos padronizados de evidência, decisão e execução;
- rastreabilidade integral;
- completude e qualidade calculadas a partir dos dados;
- exclusão de evidências desativadas no modo Instantâneo;
- AMDH com escores por ação e seleção por `argmax`;
- estado explícito da irrigação;
- HydrosOnto em Turtle e backend semântico leve;
- integração semântica ao ARG;
- segurança de domínio do APS;
- versionamento e hash do modelo preditivo;
- análise contrafactual da influência do APS;
- revisão humana baseada em risco;
- persistência integral e fechamento seguro do SQLite;
- interface para Histórico, Instantâneo e comparação;
- aceite, modificação e rejeição pelo usuário;
- comparação DSSAT atualizada;
- diagnóstico de classes não existentes na referência;
- geração de tabelas, figuras e síntese para o artigo;
- auditoria e congelamento reproduzível da versão.

## 0.2.0

- múltiplos algoritmos supervisionados no APS;
- primeiros testes funcionais e interface inicial.

## 0.1.0

- fluxo inicial de agentes e decisão híbrida.
