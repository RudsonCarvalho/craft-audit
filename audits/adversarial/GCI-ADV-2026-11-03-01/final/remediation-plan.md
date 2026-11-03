# Plano de remediação — menor conjunto de correções para os riscos mais relevantes

Regra do protocolo: nenhuma correção de código antes do registro dos achados e da aprovação. Este plano é proposta; nada foi alterado nos repositórios auditados. Ordem por razão impacto/esforço. Cada item cita os achados (`findings/findings.json`) e os requisitos que destrava.

## Lote 1 — fecha os caminhos de conclusão errada já demonstrados na `main` (esforço pequeno, risco alto)

| # | Correção | Achados | REQ | Onde |
|---|---|---|---|---|
| 1 | **Carregar `post_event`, `subject` e os 9 campos de `companies[]` no payload de evidência e na nota** (`plan_reconciliation`); projetar `post_event` na ficha e no Radar como marcador visível | F-03, F-02 | REQ-008, 009 | `investigation_reconcile.py`, `hypothesis_dossier.apply_to_card`, `radar/queries.py` |
| 2 | **Resumo da rodada gerado por template a partir das claims** (contagens por postura, lista de contraexemplos = claims `against`/`neutral` com números fora do padrão), e o texto livre do líder só como campo adicional rotulado `lider_comment`; PROJECT-STATE passa a citar `entry_id`/`head` da rodada | F-01, F-22 | REQ-012, 006 | `investigation_reconcile.round_note`, `hypothesis_cli`, handoff |
| 3 | **Snapshot do revisor em modo D1 puro**: remover `triggers[].date_note/source_refs` adicionados por rodadas, `inference.alternative_explanations`, `gaps`, `next_step_d3`, `risk`, `assessment.qualitative_confidence` posterior à criação e `state`; derivar do log até a entrada de criação (`seq 1`) | F-04 | REQ-007 | `investigation_task_io.create_task` (snapshot a partir de `replay(entries[:1])` + ficha D1) |
| 4 | **Isolamento por conteúdo**: hash de **todas** as entregas (tarefas/ e dossies/) e de notas `lider_*`, mais similaridade de texto ≥ 0,8 contra elas; recusar materiais que citem `hipoteses/` ou `log/` | F-06 | REQ-007 | `investigation_task_io` |
| 5 | **Conflito evidência × fatos da ficha**: comparar claims novas com `facts.episodes`, `hypothesis.claim` e `triggers` (datas, direção, tickers) e listar em `conflicts` com `needs_human_review` | F-07 | REQ-011 | `investigation_reconcile._conflicts` |
| 6 | **Radar**: expor `summary`, `conflicts`, `human_review_reasons`, `recommended_states`, `refutation_tests`, `companies` das notas; rótulo "N claims não projetadas (neutral)" na ficha | F-02 | REQ-010 | `radar/queries.py:dossier,changes`, `apply_to_card` |
| 7 | **`calibration_ref` e `scenario_probability_source` resolvem para artefato versionado** (caminho existente no repositório ou `claim_id` do board com `tipo_epistemico=validated_result`); recusar texto livre | F-08 | REQ-002 | `decision_gate._check_dimension`, `trigger_ontology.validate_trigger` |

## Lote 2 — pré-condições para mesclar a pilha #206–#212 (esforço médio)

| # | Correção | Achados | REQ |
|---|---|---|---|
| 8 | **Tabela explícita `model_id → (fornecedor, família, classe)`** versionada, com recusa de id não mapeado em D3/D4 e exigência de **fornecedor** distinto para revisor/auditor/árbitro; registrar `model_id` estruturado também em `status.jsonl` e deliverables da `main`; alinhar com OPS-REVIEWER-001 do hub | F-05, F-13 | REQ-013, 021, 032 |
| 9 | **Autoridades autenticadas**: `autorizado_por`/`revisado_por` com assinatura ou token emitido pelo orquestrador humano (não string); ack de mesmo modelo registrado no decision record e proibido também em D3 | F-14, F-20 | REQ-019, 021, 015 |
| 10 | **Identidade de série composta** (`publisher`, `methodology_id`, `series_code`, `unit`, `adjustment`) obrigatória no `SeriesCapture`; `record_capture` recusa `dataset_id` diferente para o mesmo `series_id` em vez de gravar revisão; permitir `available_precision` comprovada quando a fonte traz horário | F-10, F-11, F-19 | REQ-025, 026, 027 |
| 11 | **Fidelidade #211**: validadores determinísticos para entidade (nomes próprios/tickers/SIF do original devem reaparecer), direção relativa entre dois números citados (`abaixo/acima` ∧ a<b), classe de unidade `pontos`/`índice`, separador decimal pt-BR (`1,106` ≠ `1.106`), rótulo de série (publisher) e qualificadores universais (`todas/sempre/nenhum`) como suspeita obrigatória; auditor semântico de **outro fornecedor** obrigatório para `pass` | F-12 | REQ-031 |
| 12 | **#212**: herdar contrárias por `board_claim_id` **e** por similaridade de texto (≥ 0,8) com claims retratadas/substituídas da mesma seção; `require_fidelity_gate=True` por padrão para documentos ligados a HIG; status por claim `aprovada_auditada` vs `aprovada_sem_gate` | F-15, F-16 | REQ-024, 036, 037 |

## Lote 3 — lacunas de capacidade (não há atalho: implementar conforme issues, com testes adversariais primeiro)

| # | Capacidade | Achados | REQ |
|---|---|---|---|
| 13 | Identidade de evento (atores, SIF/CNPJ, datas, motivo) e registro de causas concorrentes antes de qualquer `inference` causal; teste com o homônimo mar/2025 × mai/2026 desta auditoria (`evidence/m3-sources/`) | F-18 | REQ-039, 040 |
| 14 | Motor de cenários com `probability_not_assessable`, calibração e baselines (#219–#222), só depois de 7 e 8 | F-17, F-09 | REQ-043, 045, 046 |
| 15 | Medição real de orçamento (chamadas/tokens) por tarefa e por revisão | F-24 | REQ-014 |

## Controles que funcionaram e devem ser mantidos

Log encadeado com detecção de edição/remoção interna; `calibrated_probability` nulo na ficha; `as_of` com `post_event` na validação da entrega; recusa de chaves de ordem em todos os contratos; `kind` do consenso (FedWatch ≠ consenso); board recusando citação sem relação com a claim; CAS/idempotência/tombstones e propagação `stale` no documento por seções; gate de fidelidade que recalcula a decisão; `no_match` e `discovery_suggestion` em vez de hipótese automática; `abster`/`inconclusive`/`not_assessable` como saídas válidas.

## Fixtures desta auditoria reutilizáveis como testes de regressão (dados sintéticos; incorporar só em branch própria e PR revisável)

`fixtures/m5/fidelity_211_probes.json` (13 casos), `fixtures/m5/trace_h07_round2.py` (traço de perda), `fixtures/m2/pmi_fixture_open.json` (homônimos e surpresa × variação), sondas de `evidence/m6_*`, `evidence/m7_*` (reproduzíveis a partir dos comandos descritos nos relatórios).
