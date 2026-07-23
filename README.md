# Hydros 0.3.0-agentic

O Hydros é um protótipo computacional de apoio ao gerenciamento hídrico em
agricultura digital. A unidade de análise é a unidade de manejo agrícola,
representada no protótipo por um talhão associado a um histórico temporal de
contextos.

A contribuição investigada é o uso do histórico de contexto como memória
temporal do processo decisório. O protótipo compara duas configurações:

- **Hydros Histórico:** utiliza o contexto atual e os registros anteriores;
- **Hydros Instantâneo:** utiliza somente o contexto do instante analisado.

## Arquitetura implementada

O objetivo global é decomposto em três ramos:

1. **Contextual:** Aclim, Ahid, Afen, Ageo, Aprod e Ahist, coordenados pelo AIEC;
2. **Agronômico:** ARG, com regras explícitas e inferências da HydrosOnto;
3. **Preditivo:** APS, inicialmente baseado em Random Forest.

O AMDH integra `Ehc`, `Earg` e `Eaps`, verifica consistência, calcula escores
para as cinco ações e seleciona a maior ação operacionalmente válida:

\[
D(U_i)=\arg\max_{d\in\mathcal{D}}S(d)
\]

As ações são:

- `iniciar_irrigacao`;
- `manter_irrigacao`;
- `aumentar_irrigacao`;
- `reduzir_irrigacao`;
- `finalizar_irrigacao`.

O Hydros não aciona equipamentos. O usuário permanece responsável por aceitar,
modificar ou rejeitar a recomendação.

## Componentes principais

```text
src/
├── agents/
│   ├── aclim_agent.py
│   ├── ahid_agent.py
│   ├── afen_agent.py
│   ├── ageo_agent.py
│   ├── aprod_agent.py
│   ├── ahist_agent.py
│   ├── aiec_agent.py
│   ├── arg_agent.py
│   ├── aps_agent.py
│   └── amdh_agent.py
├── config/hydros_terms.py
├── core/
│   ├── contracts.py
│   ├── evidence_quality.py
│   └── irrigation_state.py
├── database/database.py
├── integrations/dssat_adapter.py
├── ontology/hydros_onto.py
├── services/
│   ├── feature_extractor.py
│   ├── hydros_engine.py
│   ├── interface_adapter.py
│   └── validator.py
└── models/
```

A ontologia formal está em:

```text
ontology/hydros_onto.ttl
```

## Variáveis do contexto

Cada contexto pode incluir:

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
irrigacao_ativa
estagio_fenologico
estresse_hidrico
produtividade
```

## Instalação

No PowerShell:

```powershell
python -m venv .venv-1
.\.venv-1\Scripts\Activate.ps1
pip install -r requirements.txt
```

O protótipo também funciona com o backend semântico leve quando `rdflib` não
está instalado. Para validar formalmente a sintaxe Turtle, mantenha `rdflib`
instalado.

## Execução da interface

```powershell
streamlit run app.py
```

A interface permite:

- executar os modos Histórico e Instantâneo;
- comparar as recomendações;
- visualizar evidências, regras, inferências e escores das ações;
- consultar confiança, completude e conflito;
- registrar aceite, modificação ou rejeição;
- persistir a execução completa.

## Comparação experimental

```powershell
python run_dssat_comparison.py
python diagnostico_resultados.py
python test_hydros_article_outputs.py
```

Os resultados são salvos em:

```text
results/dssat_comparison/
```

Os artefatos destinados ao artigo são salvos em:

```text
results/dssat_comparison/artigo/
```

## Validação integral

```powershell
python run_hydros_validation.py
```

O comando executa os testes funcionais, reproduz a comparação DSSAT, gera o
diagnóstico e valida os artefatos. Os relatórios são salvos em:

```text
results/validation/hydros_validation_report.json
results/validation/hydros_validation_report.md
```

## Congelamento da versão

Após a validação integral:

```powershell
python freeze_hydros_release.py
```

O script cria um ZIP reproduzível em `releases/`, contendo código, modelos,
dados experimentais, ontologia, testes, documentação e resultados, sem incluir
ambiente virtual, cache, banco local ou metadados Git.

## Resultados preliminares da versão atual

Base experimental:

- 256 observações;
- duas execuções DSSAT;
- 11 eventos positivos de referência;
- forte desbalanceamento de classes.

Na detecção binária de intensificação da irrigação:

| Métrica | Histórico | Instantâneo |
|---|---:|---:|
| Precisão | 0,8000 | 0,0000 |
| Recall | 0,3636 | 0,0000 |
| F1 | 0,5000 | 0,0000 |
| Acurácia balanceada | 0,6798 | 0,5000 |
| MCC | 0,5269 | 0,0000 |

O modo Histórico identificou quatro dos onze eventos positivos. O Instantâneo
não identificou eventos positivos. Foram observadas seis divergências entre os
modos: quatro favoráveis ao Histórico e duas favoráveis ao Instantâneo, tendo
como referência operacional o conjunto experimental construído a partir das
simulações.

## Limitações científicas

Os resultados atuais devem ser interpretados como prova de conceito:

- o DSSAT é benchmark de simulação, não verdade absoluta;
- há somente duas trajetórias simuladas;
- a referência atual não contém as cinco ações em quantidade suficiente;
- o APS utiliza modelo legado e apresenta incompatibilidade parcial de domínio;
- não existe avaliação em malha fechada do efeito das decisões sobre água,
  estresse e produtividade;
- não existe ainda validação agronômica definitiva nem teste de aceitação
  concluído.

O retreinamento do APS não deve ser realizado com divisão aleatória de registros
consecutivos. Treinamento, validação e teste devem ser separados por execução,
safra, unidade de manejo ou grupo independente de cenários.
