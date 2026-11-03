# M6 — Consolidação incremental e integridade documental

Objetos: (A) dossiê vivo HIG em `main` (`hypothesis_dossier.py`, log JSONL encadeado); (B) documento por seções e patches do PR #216 (`sectioned_doc.py`, ADR 010). Saídas: `evidence/m6_dossier_log_tamper.txt`, `evidence/m6_sectioned_doc_probes.txt`.

## A. Dossiê HIG (`main`)

| Teste | Resultado |
|---|---|
| T1 editar texto de evidência no meio do log (seq 37) sem recalcular hash | detectado (`ChainError`) |
| T2 apagar evidência `against` no meio (seq 44) | detectado |
| T3 **truncar a cauda** (apagar seq 42–52: claims do revisor e a nota da rodada) | **não detectado**; estado volta a `investigating` com contagens antigas e sem a nota `needs_human_review` |
| T4 inverter `stance` de uma evidência e **recalcular a cadeia** dali em diante | **não detectado** (sem âncora externa) |

Seções identificáveis: a ficha é um YAML monolítico regenerado do log (não há `section_id`/versão por seção); patches localizados não existem em `main`; concorrência via `flock` + `expected_prev_hash` (inspeção); histórico append-only com `supersedes` (inspeção, REQ-005 aprovado). O `head` do log é a única âncora e só vale se fixado fora do repositório (PR/handoff): o `PROJECT-STATE` não registra o head de H07.

**Achado F-22 (Média; reprodução).** Truncamento e reescrita com recálculo da cadeia são indetectáveis sem âncora externa; a limitação é documentada, mas nenhum artefato versionado fixa o `head` (REQ-006 aprovado com ressalva).

## B. Documento por seções (PR #216)

Harness `Doc`/`SyntheticBoard` de `tests/test_sectioned_doc_212.py`.

| Sonda | Resultado |
|---|---|
| Q1 claim contestada → `replace_claim` mesmo texto, mesma `board_claim_id`, só evidência favorável | continua **`contestada`** (B1 da revisão independente fechado) |
| Q1b idem com **nova** `board_claim_id` | continua `contestada` (herda contrárias da antecessora) |
| Q1c **`retract_claim` + `append_claim`** com o mesmo texto e nova `board_claim_id` (no board real basta alterar uma palavra para gerar novo id de conteúdo) | **`aprovada`**; a contrária fica só no tombstone da claim retratada; índice da seção mostra `contestadas = 0` |
| Q2 retratar `CA1` com conclusão `CC1` em outra seção dependente | `CC1` → `stale`; hash de `SA` muda, `SB`/`SC` inalterados (REQ-034/035 aprovados) |
| Q3 `idempotency_key` reutilizada com conteúdo diferente | `ContentConflict` (correto) |
| Q4 patch obsoleto em `SC` com `rebase: if_disjoint` após retratação concorrente em `SA` | aplicado (por desenho: seções disjuntas); conclusão permanece marcada |
| Q4b patch obsoleto que **reafirma** a conclusão dependente da claim retratada | `PatchInvalid: depends_on CA1 inexistente ou não ativa` (correto) |
| Q6 documento padrão (`require_fidelity_gate=False`) | todo patch grava `fidelity_gate: nao_executado` e as claims ficam **`aprovada`**; com `gate_required=True` a claim é recusada (`FidelityGateRejected`) |
| Q7 view Markdown | só um contador no topo ("Patches sem gate de fidelidade: N de N"); nenhuma marca por claim |

**Achados**
- **F-15 (Alta; reprodução).** Lavagem de contestação por `retract_claim` seguido de `append_claim` reformulada: a claim volta ao conjunto ativo como `aprovada` sem a contraevidência; a #208 decide sobre `aprovada`. O histórico preserva o tombstone (por isso Alta).
- **F-16 (Média; reprodução).** Sem `require_fidelity_gate`, `aprovada` não distingue claim auditada de não auditada; o consumidor (#208) não tem sinal por claim.

Controles eficazes: CAS por versão/hash, idempotência estrita, tombstones visíveis, propagação `stale`/`blocked` para conclusões dependentes, recusa de dependência inativa, isolamento de hash por seção.

## C. Resultados por requisito (v2)

REQ-004 aprovado (inspeção); REQ-005 aprovado; REQ-006 aprovado com ressalva (F-22); REQ-024 **falhou** no conjunto ativo (F-15); REQ-034 aprovado; REQ-035 aprovado; REQ-036 **falhou** (F-15, variante retract+append); REQ-037 ressalva (F-16).


## D. Errata (v2, após revisão independente)

- A: "head não fixado em artefato versionado" é **falso**: `c2476aef…` está em `docs/descoberta/decisoes/H07_gate_check.json` (`evidence_version`) e em `data.note_entry_id` dos três `status.jsonl`. A lacuna real é que nenhum código cruza essas âncoras com o log e elas vivem no mesmo repositório (F-22 corrigido).
- B: o log `evidence/m6_sectioned_doc_probes.txt` terminava em traceback e não continha Q3/Q7; a sonda completa está em `fixtures/m6/sectioned_doc_probes.py` com saída em `evidence/m6/sectioned_doc_probes.out`. Reforço de F-15: o **autor** retrata a claim sem envolvimento do revisor que a contestou; no board real o id é derivado do conteúdo, bastando mudar uma palavra.
