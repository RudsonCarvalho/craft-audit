# M1 — Inventário e matriz de cobertura

Auditoria `GCI-ADV-2026-11-03-01`. Snapshot congelado em `manifest/audit-manifest.json`: GCI `main` @ `7d49d051c4f2564fb6bc673069e66b72af61feba` (2026-10-31), knowledge-hub `main` @ `66bdcb62e55055bf4c4e320a61bbb9733c58b820` (2026-10-29). Matriz de requisitos congelada em `requirements/requirements-matrix.json` (versão 1, 50 requisitos, 25 P0). Esta missão bloqueia as demais.

## 1. Fato central do inventário

As 16 issues de referência (#173, #178, #183, #194, #195, #197, #206–#208, #211–#213, #219–#222) foram **todas criadas em 2026-11-03**, entre 11:53Z e 15:34Z, isto é, **depois** do commit congelado de `main` (2026-10-31). Todas estão abertas e nenhuma tem PR que a feche (`closed_by_pull_requests.total_count = 0`). Portanto, em `main`, elas são especificação e não funcionalidade.

Existe, porém, uma pilha de PRs abertos, todos intitulados **"DO NOT MERGE YET"**, criados em 2026-11-01 a 2026-11-03, que implementam parte das issues #206, #207, #208, #211 e #212 (e as issues anteriores #152–#171, #202/#203). Nenhum está em `main`. Eles foram buscados e auditados como **"presente apenas em PR"** com SHAs registrados no manifesto. Os PRs são encadeados (cada base é o branch anterior), de modo que o topo `feat/sintese-claims-208` @ `884388d8` contém: fontes S1–S3, e2e #156, piloto #165, store #168, piloto ITUB4 #171, blackboard #207, IEC #206, fidelidade #211, patches #212 e síntese #208. O ramo de fontes S4 (#161, séries/consenso/surpresa) e S1b (#163) estão em `integracao/consolidacao-167` @ `45e407e6`. O protótipo Explorador/Estrategista (#202/#203) está em `feat/agentes-prototipo-203` @ `10afbbcb`.

Issues sem qualquer código (nem em PR): **#178, #183, #194, #195, #197, #213 (parcial: só conceitos reutilizados), #219, #220 (parcial: catálogo de direitos em PR), #221, #222**; knowledge-hub **#26 e #27** (nenhum diretório `economics/` existe no hub).

## 2. Inventário por repositório

### 2.1 GCI `main` (524 arquivos; 294 .py; 36.158 linhas em `src/`)

Suíte: `1080 passed, 68 skipped` (os 68 exigem PostgreSQL, indisponível no contêiner de auditoria; a integração com banco **não foi comprovada nesta auditoria**). `ruff` não executado.

| Área | Componentes (src/catalyst) | Testes | Observação de inventário |
|---|---|---|---|
| Dossiê vivo HIG (ADR 004) | `research/hypothesis_card*.py`, `hypothesis_dossier*.py`, `hypothesis_index.py`, `hypothesis_register.py`, `hypothesis_cli.py` | `test_hypothesis_*` | Log JSONL encadeado por hash; projeção para ficha `.md`; `calibrated_probability` nulo. Implementado e testado. |
| Tarefas delegadas e revisor independente (#127) | `investigation_task.py`, `investigation_deliverable.py`, `investigation_reconcile.py`, `investigation_task_io.py`, `investigation_cli.py` | `test_investigation_task.py` | O repositório **não lança agentes**; a identidade do executor é só a string `actor` em `status.jsonl`; o orçamento (`budget`) é declarativo (só `deadline` por minutos é derivado). Rodada 2 real de H07 em `docs/descoberta/tarefas/H07-*`. |
| Gatilhos e ontologia (#125) | `trigger_ontology.py`, `trigger_catalog.py`, `policy_profile.py` | `test_trigger_ontology.py` | `scenario_probability` em gatilho aceita valor com qualquer `scenario_probability_source` textual (ver M4). |
| Casamento evento→hipótese (#126) | `event_normalize.py`, `event_matcher.py` | `test_event_matcher.py`, `test_event_matching_e2e.py` | Relevância, não causalidade; avaliação rotulada minúscula (5 pares, não cega). |
| Monitor e alertas (#128) | `monitor*.py`, `watch_policy.py` | `test_monitor.py` (25) | Replay commitado 2012-09-14; léxico de reversão heurístico. |
| Radar (#129, ADR 005) | `radar/queries.py`, `actions.py`, `api.py`, `server.py`, `radar.html` | `test_radar.py` (26), `test_radar_http.py` (5) | Dossiê expõe `notes` só como `{seq, at, actor, note_kind, note}`; o campo `summary` das notas de rodada não é exposto (ver M5). |
| Gate D4 e decisão humana (#130) | `decision_gate.py`, `decision_cli.py` | `test_decision_gate.py` | Validação de `scenario_probability` só exige `calibration_ref` textual não vazio e ausência de palavras "LLM/GPT/Claude..." (ver M4). |
| Descoberta D1 / M1 reverso / event-first / estudos | `extreme_*`, `event_first*`, `earnings_study`, `copom_study`, `election_*`, `seasonality_study`, `catalyst_batch`, `folds`, `splits`, `execution_cost`, `event_portfolio`, `risk`, `total_return` | numerosos | Holdout 2022–2025 guardado em código (`HOLDOUT_YEARS`); fora do escopo probatório desta auditoria (sem banco). |
| Fontes CVM/B3/PNCP/ANEEL/Copom | `sources/*` | numerosos (parte exige PostgreSQL) | Infraestrutura de dados; fora do foco das missões M2–M7. |

### 2.2 GCI — pilha de PRs (não mesclados)

| Worktree auditado | SHA | Suíte (PYTHONPATH=src) | Módulos novos relevantes |
|---|---|---|---|
| `feat/sintese-claims-208` (PRs #210, #214, #215, #216, #217, #218 e base #172/#169/#166/#162/#159/#158/#157) | `884388d8…` | `1785 passed, 69 skipped` | `evidence_board.py` (1708 l.), `iec_contracts.py` (973), `iec_run.py` (895), `compression_fidelity.py` (2133), `fidelity_gate.py`, `sectioned_doc*.py` (1895+), `synthesis*.py` (1169+), `model_identity.py`, `claims.py`, `agents.py`, `evidence*.py`, `catalog.py`, `document_fetch.py` |
| `integracao/consolidacao-167` (PR #170; inclui #161 S4 e #163 S1b) | `45e407e6…` | `1309 passed, 69 skipped` | `series_store.py`, `series_consensus.py`, `release_calendar.py`, `series_eia.py`, `series_cli.py`, `catalog.py` (direitos por uso) |
| `feat/agentes-prototipo-203` (PRs #205, #209) | `10afbbcb…` | `1531 passed, 69 skipped` | `roles.py`, `role_runtime.py`, `role_challenge.py`, `role_prompts/*.md` |
| `feat/sources-s4-series` (PR #161) | `c133cbfd…` | `1171 passed, 68 skipped` | idem S4 |
| `docs/skills-investigacao-profunda` (PR #160) | `06f51818…` | não executado (docs/skills) | 5 skills `.claude/skills/*` (perfis produtor/auditor) |

Cada PR da pilha #206–#212 traz um documento `revisao_independente_*.md`. **Todos declaram como revisor "Claude Opus 5.5"** (mesma família de fornecedor do implementador e deste auditor). As revisões reprovaram inicialmente e registram correções; a verificação de fechamento foi feita pelo mesmo revisor. Isso é insumo direto de M7.

### 2.3 knowledge-hub `main` (465 arquivos; 420 .md)

`scripts/validate.py --profile okf`: ok (215 conceitos, 12 skills). `--profile hub`: ok, com avisos "draft mandatory candidate is not enforceable" para todas as normas (todas `status: draft`). `unittest`: 56 OK. Conteúdo relevante para o GCI: `bundles/agent-operations/ops-001/norm-001-revisor-nao-pequeno.md` (OPS-REVIEWER-001: revisor não pode ser modelo de classe pequena), `bundles/glossary/revisao-cruzada.md` (revisor de **outro fornecedor**), `bundles/review/rev-001-pr-e-briefs.md` (ENG-REVIEW-001). Não existe nenhum bundle de conhecimento econômico (#26/#27), nem nada sobre PMIs, frigoríficos ou salvaguardas (grep vazio).

## 3. Classificação resumida (matriz v1, 50 requisitos)

| Classe | Qtde | Exemplos |
|---|---|---|
| implementado e testado na `main` | 14 | REQ-001, 002, 003, 004, 005, 006, 007, 008, 009, 015, 016, 017, 018, 048 |
| implementado sem testes suficientes | 4 | REQ-010 (fidelidade da projeção ficha/Radar), REQ-011 (conflito evidência × fatos da ficha), REQ-014 (orçamento medido), REQ-040 (decomposição causal) |
| presente apenas em PR | 23 | REQ-013, 019–038, 049, 050 |
| somente especificado | 7 | REQ-039, 041, 042, 043, 045, 046, 047 |
| parcial em PR | 1 | REQ-044 |
| inexistente (nenhum controle) | 1 | REQ-012 (fidelidade do resumo livre do líder) |

Denominador de cobertura inicial: **50**. Requisitos descobertos depois entram em versão 2 da matriz com origem e justificativa, sem apagar a v1.

## 4. Desvios de processo declarados

1. Duas sondas exploratórias (`decision_gate.validate_decision_record` e `model_identity.normalize_model_id`) foram executadas durante o inventário, antes do congelamento da matriz. Não alteraram a lista de requisitos; são re-registradas como testes em M4 e M7.
2. Não há controlador independente nesta sessão: nenhuma fixture pôde ser classificada como **cega**. Todas as fixtures são adversariais abertas, preparadas pelo próprio executor.
3. PostgreSQL indisponível: 68–69 testes de integração ignorados em todas as suítes; nenhuma afirmação desta auditoria depende deles.
4. As páginas de divulgação da S&P Global (`pmi.spglobal.com`) e duas páginas de imprensa responderam HTTP 403 ao fetcher; uma tentativa com outro agente de usuário foi bloqueada pela política da sessão e **não foi repetida**. A fonte primária RatingDog fica registrada como **bloqueada** e substituída por fontes secundárias datadas (RTHK, investinglive, MNI), conforme M2.

## 5. Orçamento proposto (antes da execução)

Ver `manifest/audit-manifest.json#budget`. Regra de parada aplicada: ao atingir 25 achados distintos, triagem dos P0 pendentes antes de ampliar.


## 6. Errata (v2, após revisão independente — `final/independent-review.md`)

- §2.2: "**Todos** declaram como revisor 'Claude Opus 5.5'" está impreciso: quatro das seis revisões (#206, #207, #211, #209) declaram "Claude Opus 5.5"; a de #212 diz "Claude (Opus)" e a de #208, "Claude (sessão independente)". A conclusão (mesma família de fornecedor) não muda.
- §1: este relatório não resume o texto das issues de referência; a revisão independente leu #173 e #195 e apontou cinco classes de requisito ausentes, acrescentadas como REQ-051..055 na matriz v3 (`nao_testado`). O denominador de cobertura inicial continua 50.
