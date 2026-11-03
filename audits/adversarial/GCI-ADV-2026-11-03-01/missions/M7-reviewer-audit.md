# M7 — Revisores e independência de validação

Prioridade máxima após M1. Pergunta: cada revisor usa o contrato original, evidências recuperáveis e critérios predefinidos? Onde cabem falsas aprovações, falsas reprovações, erros compartilhados e omissões não detectadas? Objetos: (A) rodada 2 real de H07 em `main` (`investigation_task*.py`, `docs/descoberta/tarefas/H07-*`); (B) IEC do PR #214 (`iec_contracts.py`, `iec_run.py`, `model_identity.py`); (C) auditor de fidelidade do PR #215 (independência); (D) papéis do PR #209 (`role_challenge.py`); (E) as "revisões independentes" anexadas aos PRs. Saídas: `evidence/m7_isolation_and_gate_probes.txt`.

## 0. Dependências declaradas entre auditor e sistema auditado

| Dimensão | Situação |
|---|---|
| Modelo | Esta auditoria roda num modelo Anthropic (sessão configurada `claude-fable-5-1`). Os atores da rodada 2 de H07 são `fund-sonnet-r2`, `dados-sonnet-r2`, `revisor-sonnet-r2` (família Claude); o líder `gci-lider` e `claude-hig-p1-1` são Claude; as cinco revisões independentes dos PRs #210/#214/#215/#216/#209 declaram "Claude Opus 5.5". **Mesmo fornecedor em toda a cadeia, inclusive este auditor.** Erro compartilhado é possível e não pode ser excluído por esta auditoria. |
| Prompts/resumos | Nenhum prompt do GCI foi reutilizado; `PROJECT-STATE.md` foi tratado como artefato auditado, não como fonte. |
| Infraestrutura | Clone fresco em contêiner; sem acesso ao banco `catalyst_trial`, VPS ou scratchpads das sessões anteriores. |
| Executor alternativo | Não disponível nesta sessão para M7; a revisão independente da seção 9 do protocolo é feita por um subagente de **modelo diferente, mesmo fornecedor**, declarado em `final/independent-review.md`. |

## A. Rodada 2 de H07 (`main`)

### A.1 O revisor recebeu só "ficha inicial e evidência primária"?

`REVIEWER_STRIPPED_FIELDS = (dossier, revisions, evidence_for, evidence_against)`. O snapshot entregue ao revisor (`tarefas/H07-rev-7acb9d7691/card_snapshot.json`, 35 KB) **mantém**: `triggers[0].date_note` = "MP 579 assinada em 2012-09-11; publicação no DOU de 2012-09-12 ... (dossiê H07, dados_eventos.json)"; `inference.alternative_explanations` escrita pelo líder ("Queda de mercado...; rumores antes do ato; outros fatores"); `gaps`, `next_step_d3`, `risk`; `assessment.qualitative_confidence: media` e `state: investigating` (ambos resultado da rodada 1); `d1_baseline`. O revisor citou o snapshot: claim c9 "Conteúdo da MP 579 (assinada 11/09/2012, DOU 12/09/2012 **segundo a ficha**)" com fonte `card_snapshot.json triggers[T1].date_note`. Suas 5 explicações alternativas sobrepõem as 3 do líder.

**F-04 (Alta; inspeção documental).** A independência do revisor é formal: o snapshot "congelado" transporta conclusões da rodada anterior pelo gatilho, pela inferência do líder e pela confiança já rebaixada. REQ-007 falhou.

### A.2 Isolamento de materiais

| Material oferecido ao revisor | Resultado de `create_task` |
|---|---|
| cópia byte a byte de `tarefas/H07-dados-*/deliverable.json` com nome neutro | recusado (`IsolationError: idêntico a entrega de outro papel`) |
| mesma cópia **+ 1 byte** | **criado** (`H07-rev-f966a4a249`) |
| nota do líder com nome neutro (`materiais/contexto.md`) | **criado** |
| cópia byte a byte da entrega da **rodada 1** (`dossies/H07/dados_eventos.json`) | **criado** (o hash só cobre `tarefas/`) |

**F-06 (Média; reprodução).** O isolamento é por nome de caminho e hash exato das entregas da pasta `tarefas/`; renomeação com alteração trivial ou a rodada anterior passam. REQ-007 falhou também neste ponto.

### A.3 Identidade e orçamento

Nenhum campo estruturado registra modelo/classe do executor; só o `actor` textual. As três tarefas foram criadas 14:04:31–14:04:38Z e entregues 14:06:49–14:07:27Z (**≤ 3 min** para orçamentos de 30–45 min e 30–60 chamadas); nenhuma contagem de chamadas/tokens é gravada. O handoff afirma que "a do revisor foi recusada uma vez por campo trocado": `status.jsonl` do revisor tem só `created → submitted → accepted`.

**F-05 (Alta; inspeção).** Sem identidade estrutural de modelo, a norma do hub OPS-REVIEWER-001 (revisor não é modelo pequeno) e a revisão cruzada de outro fornecedor são inverificáveis; a rodada usou a mesma família em todos os papéis. **F-24 (Média).** Orçamento declarativo, não medido; afirmação de handoff sem rastro (REQ-014).

### A.4 Falsas aprovações e omissões

- A entrega do revisor foi aceita com `inconclusive: true` e `needs_human_review: false`; a nota consolidada marcou `needs_human_review` só por regra geral ("rodada inconclusiva").
- `post_event` da claim de imprensa pós-evento não sobrevive ao `plan_reconciliation` (payload sem o campo): alegação pós-evento vira `evidence_for` (**F-03**).
- O conflito entre a claim `against` do revisor (sem queda de ELET3 até 31/10) e `facts.episodes` (episódio ELET3 18/10→17/12, −48,5%) não é detectado: `_conflicts` só cruza `for`×`against` entre entregas por `subject` ou Jaccard ≥ 0,6 (**F-07**).
- A claim `for` do revisor é reação de preço dos ativos **selecionados por terem caído** (CSV fornecido pelo líder); entra na ficha como `fact` a favor (**F-21**, Média).
- `gate_check(validation_ready)` com `timestamps_checked`/`independence_checked` verdadeiros → `ready=True` apesar de avisos de revisão humana pendente, recomendação `inconclusive` do revisor e 41 evidências não verificadas (**F-20**, Média).

## B. IEC (PR #214)

| Sonda | Resultado |
|---|---|
| D4, produtor `model-A`, revisor `Model-A ` / `model-a-v2` / `gpt-4o` vs `gpt-4o-2024-11-20` | `REVIEW-MESMO-MODELO` (correto) |
| D4, produtor `claude-sonnet-4-5`, revisor **`Claude Sonnet 4.5`** | **ACEITO** (`normalize_model_id` → `claudesonnet4` ≠ `claudesonnet`) |
| D4, produtor `claude-sonnet-4-5`, revisor `claude-opus-4-1` (mesmo fornecedor) | **ACEITO** |
| D3, `same_model_acks` com `autorizado_por` = `orquestrador`, `humano`, `humano-rudson`, `Orquestrador ` | **missão aceita** com revisor = produtor em todos os checks |
| ack por `autorizado_por` = produtor | recusado (correto) |
| `pass` em `FONTE-LIDA` com ponteiro `nao_lido` / posterior ao corte | recusado (correto) |
| `pass` em `FONTE-LIDA` com ponteiro de **outra claim** (span verificado) | **ACEITO** (relevância não verificada; documentado) |
| exclusão de check revisada por `revisado_por="gci-lider (modo humano)"`, `revisor_papel="humano"` | **ACEITA** |

**F-13 (Alta; reprodução).** A independência por família de modelo cai com grafia ("Claude Sonnet 4.5") e não modela fornecedor (Sonnet×Opus); o mesmo normalizador serve a #211 (auditor de fidelidade) e #208 (árbitro). **F-14 (Média; reprodução).** Identidades de autoridade (`humano`, `orquestrador`, `revisor_papel`) são strings não autenticadas; o orquestrador (LLM) pode autorizar autorrevisão em D1–D3. Documentado como "trust model de escritor honesto", mas o protocolo pede revisor por papel com contrato original e evidências recuperáveis: a parte "recuperáveis" existe (ponteiros do board); a parte "revisor distinto" não é verificável.

## C. Auditor de fidelidade (PR #215)

A independência usa o mesmo `normalize_model_id` (F-13). Com auditor leniente, 8 de 11 defeitos passam (M5, F-12). O gate recalcula a decisão e exige leitura registrada: controle eficaz contra o relatório forjado (B1 da revisão independente do PR), não re-sondado aqui; registrado como aprovado por inspeção do código e dos testes `test_b1_*`.

## D. Papéis Explorador/Estrategista (PR #209)

O revisor crítico da dupla usa a **mesma porta de modelo** que os papéis (I6 da revisão independente do PR; `role_challenge.py:506/565`). Filtros lexicais de probabilidade contornáveis (M4, F-09). O veto é "metodológico" e emitido pelo mesmo modelo que produziu as posições.

## E. As "revisões independentes" dos PRs

Cinco documentos, todos "Claude Opus 5.5, sem acesso à conclusão do implementador", todos com veredito inicial "Reprovado" e tabela de fechamento conferida pelo **mesmo revisor**. São revisões úteis (acharam B1/B2/B3 reais, inclusive o bypass de `model_id` que esta auditoria reencontrou em outra forma), mas: (i) mesma família do implementador; (ii) sondas "no scratchpad, não commitadas" → **não reproduzíveis** por terceiros; (iii) o fechamento é autoavaliado. REQ-013 falhou também para o processo de revisão de PR.

## F. Resultados por requisito (v2)

REQ-007 **falhou** (F-04, F-06); REQ-008 ressalva (F-03); REQ-009 **falhou** (F-21, F-03); REQ-011 **falhou** (F-07); REQ-013 **falhou** (F-05, F-13); REQ-014 **falhou** (F-24); REQ-015 ressalva (F-20); REQ-019 ressalva (F-14); REQ-020 ressalva (relevância do ponteiro); REQ-021 **falhou** (F-13, F-14); REQ-022 aprovado por inspeção; REQ-023 aprovado por inspeção + controle positivo (citação sem relação recusada); REQ-032 **falhou** (F-13); REQ-049 aprovado por inspeção.


## G. Errata (v2, após revisão independente)

- A.1 (F-04): a ancoragem do revisor **não está demonstrada** (ele contestou a ficha, deu duas claims `against` e recomendou `inconclusive`); a limitação está parcialmente declarada no PROJECT-STATE. **F-04 rebaixado para Média** (falha de desenho sem impacto mostrado).
- A.3 (F-05): quatro das seis revisões de PR declaram "Claude Opus 5.5"; as normas do hub são `draft`; Sonnet é "carro-chefe" no catálogo do hub, logo não há indício de violação de OPS-REVIEWER-001, só impossibilidade de verificar. **F-05 rebaixado para Média**; o caminho concreto de autorrevisão é F-13.
- A.4: `human_review_reasons` inclui "H07-fund pediu revisão humana", não só a regra geral.
- B (F-14): o ack por `orquestrador`/`humano*` é comportamento projetado (`ACK_AUTHORITIES`); a sonda mostra `run status=blocked`, logo a cobertura de ponta a ponta sem revisor distinto não está demonstrada.
- Sondas arquivadas: `fixtures/m7/iec_identity_probes.py` → `evidence/m7/iec_identity_probes.out`; `fixtures/m7/isolation_probes.py` → `evidence/m7/isolation_probes.out`.
- B (F-14), reexecução arquivada: com `autorizado_por='orquestrador'` o run D3 fechou **`status=ok`** com revisor = produtor em todos os checks (nenhuma segunda opinião sorteada para esse hash de missão); com `humano-rudson`, `blocked`. A cobertura completa sem revisor distinto é, portanto, alcançável em D3 por configuração.
