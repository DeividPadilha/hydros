# Documentação técnica do Hydros 0.3.0-agentic

## 1. Finalidade

O Hydros apoia recomendações hídricas para unidades de manejo agrícola. A
arquitetura utiliza históricos de contextos como memória temporal e combina
análise contextual, conhecimento agronômico, inferência semântica e aprendizado
de máquina.

## 2. Contrato do contexto

Um contexto agrícola representa o estado de uma unidade de manejo em um
instante ou janela temporal. O histórico é uma sequência cronológica desses
contextos.

As validações de entrada, completude e qualidade não devem ser confundidas:

- **completude:** proporção de variáveis esperadas que estão disponíveis;
- **qualidade:** consistência e plausibilidade dos valores;
- **criticidade:** gravidade da condição hídrica;
- **confiança:** suporte disponível para a evidência produzida.

## 3. Fluxo decisório

```text
Histórico H(Ui)
   ├── Aclim ── Eclim
   ├── Ahid  ── Ehid
   ├── Afen  ── Efen
   ├── Ageo  ── Egeo
   ├── Aprod ── Eprod
   └── Ahist ── Ehist
              ↓
             AIEC ── Ehc

Contexto + histórico ── ARG + HydrosOnto ── Earg
Contexto + histórico ── APS ── Eaps

Ehc + Earg + Eaps ── AMDH ── recomendação
```

No modo Instantâneo, o Ahist é registrado como desativado e não participa da
média nem do cálculo de conflito.

## 4. AIEC

Responsabilidades:

- integrar somente evidências ativas;
- ponderar evidências por qualidade e confiança;
- registrar completude;
- identificar divergências;
- produzir `Ehc`;
- relacionar a evidência aos agentes participantes.

A escala interna de criticidade possui quatro níveis:

```text
baixo
moderado
alto
critico
```

A condição semântica utilizada pela HydrosOnto possui três classes:

```text
adequada
atencao
critica
```

Mapeamento:

```text
baixo     -> adequada
moderado  -> atencao
alto      -> atencao
critico   -> critica
```

## 5. ARG e HydrosOnto

O ARG aplica regras agronômicas explícitas. A HydrosOnto fornece uma inferência
semântica rastreável com:

- classe inferida;
- condição semântica;
- fatos utilizados;
- regras semânticas acionadas;
- confiança;
- versão da ontologia.

A inferência semântica é integrada ao ramo agronômico. Ela não constitui um
quarto ramo independente no AMDH.

Arquivos:

```text
src/agents/arg_agent.py
src/ontology/hydros_onto.py
ontology/hydros_onto.ttl
```

## 6. APS

O APS registra:

- algoritmo solicitado e utilizado;
- versão e hash do modelo;
- classe prevista;
- confiança bruta;
- compatibilidade com o domínio;
- confiança ajustada;
- categorias desconhecidas;
- atributos fora da faixa de treinamento;
- importâncias globais dos atributos;
- avisos científicos.

Categorias desconhecidas são codificadas como `-1`. Elas não são substituídas
silenciosamente por uma categoria conhecida.

O modelo atual está marcado como:

```text
modelo_legado_requer_retreinamento_temporal
```

O treinamento científico deverá separar conjuntos por trajetórias independentes,
nunca por divisão aleatória de linhas consecutivas.

## 7. AMDH

O AMDH calcula um escore para cada ação:

```text
S(iniciar_irrigacao)
S(manter_irrigacao)
S(aumentar_irrigacao)
S(reduzir_irrigacao)
S(finalizar_irrigacao)
```

Ações incompatíveis com o estado operacional são bloqueadas. O resultado é:

\[
D(U_i)=\arg\max_{d \in \mathcal{D}_{válida}} S(d)
\]

O agente registra:

- estado e origem da informação de irrigação;
- ações bloqueadas;
- pesos efetivos;
- escores de todas as ações;
- decisão com e sem APS;
- influência material do APS;
- conflito;
- confiança final;
- motivos de revisão humana;
- explicação.

Quando o APS está fora do domínio, o AMDH realiza análise contrafactual. O mero
aviso de domínio não obriga revisão excepcional; a revisão ocorre quando a
influência do APS é material ou quando existem outros riscos relevantes.

## 8. Rastreabilidade

O contrato completo está em:

```text
src/core/contracts.py
```

Cada execução possui:

- identificador único;
- unidade de manejo e instante;
- modo de análise;
- janela histórica;
- versão da arquitetura;
- agentes acionados;
- evidências;
- regras;
- inferências semânticas;
- resultado preditivo;
- estado da irrigação;
- escores das ações;
- decisão;
- confiança, completude e conflito;
- revisão humana;
- resposta do usuário.

## 9. Persistência

O banco SQLite registra a execução completa e a avaliação humana. A conexão é
fechada deterministicamente para evitar bloqueio do arquivo no Windows.

Status humano:

```text
pendente
aceita
modificada
rejeitada
```

A modificação registra a decisão original e a decisão escolhida pelo usuário.

## 10. DSSAT

O adaptador converte as saídas disponíveis para o contrato do Hydros e conserva
a identificação da execução simulada.

O DSSAT deve ser descrito como benchmark de simulação. A ação de referência não
deve ser apresentada como verdade absoluta e precisa ser documentada
independentemente do ARG e do AMDH.

## 11. Métricas

Devido ao desbalanceamento, a acurácia isolada não é suficiente. As métricas
prioritárias são:

- F1 macro;
- acurácia balanceada;
- MCC;
- Kappa de Cohen;
- precisão, recall e F1 da intensificação;
- matriz de confusão;
- taxa de revisão humana;
- conflito;
- dependência material do APS.

## 12. Reprodutibilidade

Execução integral:

```powershell
python run_hydros_validation.py
```

Congelamento:

```powershell
python freeze_hydros_release.py
```

Os hashes SHA-256 do código e dos dados são registrados no relatório de
validação e no manifesto da versão congelada.
