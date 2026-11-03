# Relatório de cobertura (v2, após revisão independente)

Auditoria `GCI-ADV-2026-11-03-01`. Denominador de cobertura inicial: **50 requisitos** congelados na matriz v1 (`requirements/requirements-matrix.v1.json`). A matriz v3 acrescenta **5 requisitos** (REQ-051..055) derivados das issues #173/#195 e apontados pela revisão independente, todos `nao_testado` nesta execução; v1 e v2 estão preservadas. Resultados sobre os 55: {"aprovado": 16, "falhou": 16, "aprovado_com_ressalva": 9, "inconclusivo": 2, "inexistente": 7, "nao_testado": 5}. Achados: 25 ({"Crítica": 0, "Alta": 7, "Média": 16, "Baixa": 2}; {"confirmado_por_reproducao": 17, "confirmado_por_inspecao_documental": 8}); cinco severidades foram rebaixadas de Alta para Média após a revisão independente (`findings/findings.json#revision`).

## 1. Estado das missões

| Missão | Estado | Observação |
|---|---|---|
| M1 Inventário | concluída | 50 REQ (v1), 25 P0 com resultado; +5 REQ na v3 não testados |
| M2 Séries/surpresa | concluída com bloqueios | primária S&P Global (RatingDog) bloqueada por HTTP 403; fixture **não cega**; sondas arquivadas em `fixtures/m2`, `evidence/m2` |
| M3 Causalidade | concluída com bloqueios | preços bloqueados; GACC não consultada; 3 páginas 403; 1 alegação não verificada; SRC-M3-01 corrigido |
| M4 Quant | concluída | 7 REQ inexistentes por design; sondas arquivadas em `fixtures/m4`, `evidence/m4` |
| M5 Compressão | concluída | cadeia real H07 r2 rastreada; 13 sondas no auditor #211 reexecutadas (`evidence/m5/fidelity_211_probes.rerun.out`) |
| M6 Documento | concluída | 4 testes no log HIG; sondas no documento por seções reexecutadas (`evidence/m6/`) |
| M7 Revisores | concluída com limitação de executor | sem modelo de outro fornecedor; revisão independente por `claude-opus-5-5` (mesmo fornecedor), `final/independent-review.md` |

## 2. Resultado por missão (um REQ pode pertencer a mais de uma missão)

| Missão | Resultados |
|---|---|
| M1 | {'inexistente': 1, 'aprovado': 1} |
| M2 | {'aprovado': 2, 'falhou': 2, 'aprovado_com_ressalva': 1, 'inconclusivo': 1, 'nao_testado': 1} |
| M3 | {'aprovado': 2, 'inexistente': 1, 'falhou': 1} |
| M4 | {'aprovado': 2, 'falhou': 1, 'aprovado_com_ressalva': 3, 'inexistente': 6, 'nao_testado': 4} |
| M5 | {'aprovado_com_ressalva': 1, 'falhou': 7, 'aprovado': 4, 'inconclusivo': 1} |
| M6 | {'aprovado': 5, 'aprovado_com_ressalva': 2, 'falhou': 2} |
| M7 | {'falhou': 6, 'aprovado_com_ressalva': 4, 'aprovado': 4, 'nao_testado': 2} |

## 3. Matriz resumida (v3)

| REQ | P | Missão | Status inicial | Resultado | Achados | Motivo |
|---|---|---|---|---|---|---|
| REQ-001 | P0 | M2/M4 | implementado_e_testado_na_main | **aprovado** | — | PIT conservador (upper_bound) no store; as_of nas entregas; sem banco para exercitar coleta real |
| REQ-002 | P0 | M4 | implementado_e_testado_na_main | **falhou** | F-08 | calibration_ref textual não resolvido; léxico de LLM contornável; trigger aceita probabilidade com source livr |
| REQ-003 | P1 | M4 | implementado_e_testado_na_main | **aprovado** | — | guardas HOLDOUT_YEARS e recusas em CLI por inspeção; não exercitado |
| REQ-004 | P1 | M6 | implementado_e_testado_na_main | **aprovado** | — | máquina de estados impõe state_changed explícito (inspeção + testes existentes) |
| REQ-005 | P1 | M6 | implementado_e_testado_na_main | **aprovado** | — | supersedes preservado (inspeção) |
| REQ-006 | P1 | M6 | implementado_e_testado_na_main | **aprovado_com_ressalva** | F-22 | edição/remoção no meio detectada; truncamento e rechain não; head não fixado |
| REQ-007 | P0 | M7 | implementado_e_testado_na_main | **falhou** | F-04, F-06 | snapshot transporta conclusões; isolamento por nome/hash exato |
| REQ-008 | P1 | M5/M7 | implementado_e_testado_na_main | **aprovado_com_ressalva** | F-03 | validador correto; post_event perdido a jusante |
| REQ-009 | P0 | M5 | implementado_e_testado_na_main | **falhou** | F-02, F-03, F-21 | companies[] perde 6 de 9 campos; post_event perdido; circularidade não marcada |
| REQ-010 | P0 | M5 | implementado_sem_testes_suficientes | **falhou** | F-02 | 81% das claims fora da ficha; Radar note=null |
| REQ-011 | P0 | M5/M7 | implementado_sem_testes_suficientes | **falhou** | F-07 | conflito com facts.episodes não detectado |
| REQ-012 | P0 | M5 | inexistente | **falhou** | F-01 | nenhum controle sobre o resumo livre; contraexemplo omitido no caso real |
| REQ-013 | P0 | M7 | presente_apenas_em_PR | **falhou** | F-05, F-13 | sem identidade estrutural; mesma família em toda a cadeia; normalizador contornável |
| REQ-014 | P1 | M7 | implementado_sem_testes_suficientes | **falhou** | F-24 | orçamento não medido |
| REQ-015 | P1 | M4/M7 | implementado_e_testado_na_main | **aprovado_com_ressalva** | F-20 | gate ready só com atestados; avisos não bloqueiam |
| REQ-016 | P1 | M4 | implementado_e_testado_na_main | **aprovado_com_ressalva** | F-08 | chaves de ordem recusadas; percentual subjetivo em note aceito |
| REQ-017 | P1 | M3/M6 | implementado_e_testado_na_main | **aprovado** | — | inspeção do replay commitado; não reexecutado |
| REQ-018 | P1 | M3 | implementado_e_testado_na_main | **aprovado** | — | inspeção; avaliação rotulada minúscula e não cega declarada pelo repositório |
| REQ-019 | P0 | M7 | presente_apenas_em_PR | **aprovado_com_ressalva** | F-14 | item crítico não removível (teste existente); exclusão com revisor string aceita |
| REQ-020 | P0 | M7 | presente_apenas_em_PR | **aprovado_com_ressalva** | F-14 | ponteiros nao_lido/pós-corte recusados; ponteiro de outra claim aceito |
| REQ-021 | P0 | M7 | presente_apenas_em_PR | **falhou** | F-13, F-14 | variantes de grafia e mesmo fornecedor aceitos em D4; ack por string em D1–D3 |
| REQ-022 | P1 | M7 | presente_apenas_em_PR | **aprovado** | — | inspeção + testes do PR |
| REQ-023 | P0 | M5/M7 | presente_apenas_em_PR | **aprovado** | — | controle positivo: citação sem relação recusada pelo board |
| REQ-024 | P0 | M5/M6 | presente_apenas_em_PR | **falhou** | F-15 | contrária sai do conjunto ativo por retract+append |
| REQ-025 | P0 | M2 | presente_apenas_em_PR | **falhou** | F-10 | identidade = string do chamador |
| REQ-026 | P0 | M2 | presente_apenas_em_PR | **falhou** | F-11, F-19 | regras corretas, mas inoperantes via store; provedor divergente registrável mas não exigido |
| REQ-027 | P1 | M2 | presente_apenas_em_PR | **aprovado_com_ressalva** | F-10 | revisão correta; identidade fraca gera revisão espúria |
| REQ-028 | P1 | M2 | presente_apenas_em_PR | **aprovado** | — | inspeção |
| REQ-029 | P0 | M5/M7 | presente_apenas_em_PR | **aprovado** | — | inspeção: assemble_decisions força needs_review sem retrieval; não sondado |
| REQ-030 | P1 | M5 | presente_apenas_em_PR | **aprovado** | — | inspeção + testes |
| REQ-031 | P0 | M5 | presente_apenas_em_PR | **falhou** | F-12, F-23 | 8 de 11 defeitos passam com auditor leniente |
| REQ-032 | P0 | M5/M7 | presente_apenas_em_PR | **falhou** | F-13 | mesmo normalizador contornável |
| REQ-033 | P1 | M5 | presente_apenas_em_PR | **aprovado** | — | inspeção do gate que recalcula decisão; testes test_b1_* |
| REQ-034 | P0 | M6 | presente_apenas_em_PR | **aprovado** | — | CAS, idempotência estrita, hash isolado |
| REQ-035 | P0 | M6 | presente_apenas_em_PR | **aprovado** | — | stale/blocked propagados; seções não tocadas inalteradas |
| REQ-036 | P0 | M6 | presente_apenas_em_PR | **falhou** | F-15 | variante retract+append |
| REQ-037 | P1 | M6 | presente_apenas_em_PR | **aprovado_com_ressalva** | F-16 | gate opcional por padrão; sem marca por claim |
| REQ-038 | P1 | M5 | presente_apenas_em_PR | **inconclusivo** | — | sem benchmark com modelo real (declarado no PR); não sondado |
| REQ-039 | P0 | M3 | somente_especificado | **inexistente** | F-17, F-18 | só issue |
| REQ-040 | P0 | M3 | implementado_sem_testes_suficientes | **falhou** | F-18 | sem decomposição; caso real mostra homônimo de evento não detectável |
| REQ-041 | P1 | M4 | somente_especificado | **inexistente** | F-17 |  |
| REQ-042 | P1 | M4 | somente_especificado | **inexistente** | F-17 |  |
| REQ-043 | P0 | M4 | somente_especificado | **inexistente** | F-09, F-17 | único controle existente (filtro lexical) contornável |
| REQ-044 | P1 | M4 | S_PR_PARCIAL | **aprovado_com_ressalva** | F-17 | FedWatch recusado como consenso; MNPI inexistente |
| REQ-045 | P1 | M4 | somente_especificado | **inexistente** | F-17 |  |
| REQ-046 | P1 | M4 | somente_especificado | **inexistente** | F-17 |  |
| REQ-047 | P1 | M1/M4 | somente_especificado | **inexistente** | F-25 | hub sem economics/ |
| REQ-048 | P1 | M1 | implementado_e_testado_na_main | **aprovado** | F-25 | validate hub ok; normas draft |
| REQ-049 | P1 | M7 | presente_apenas_em_PR | **aprovado** | — | inspeção do docstring e testes |
| REQ-050 | P0 | M2 | presente_apenas_em_PR | **inconclusivo** | F-19 | store acomoda 3 relógios + revisão; não distingue disponibilidade por público |
| REQ-051 | P1 | M4/M7 | descoberto_apos_congelamento | **nao_testado** | — | requisito identificado pela revisao independente apos o congelamento da v1; fora do orcamento desta execucao |
| REQ-052 | P1 | M4 | descoberto_apos_congelamento | **nao_testado** | — | requisito identificado pela revisao independente apos o congelamento da v1; fora do orcamento desta execucao |
| REQ-053 | P1 | M7 | descoberto_apos_congelamento | **nao_testado** | — | requisito identificado pela revisao independente apos o congelamento da v1; fora do orcamento desta execucao |
| REQ-054 | P1 | M4 | descoberto_apos_congelamento | **nao_testado** | — | requisito identificado pela revisao independente apos o congelamento da v1; fora do orcamento desta execucao |
| REQ-055 | P1 | M2/M4 | descoberto_apos_congelamento | **nao_testado** | — | requisito identificado pela revisao independente apos o congelamento da v1; fora do orcamento desta execucao |

## 4. Itens bloqueados, inconclusivos e não testados

- **Bloqueado:** fonte primária RatingDog/S&P Global (403); cotações 2026; banco PostgreSQL `catalyst_trial` (68–69 testes de integração ignorados); aviso original da GACC.
- **Inconclusivo:** REQ-038 (sem benchmark com modelo real); REQ-050 (disponibilidade por público).
- **Não testado (descobertos após o congelamento):** REQ-051..055.
- **Aprovado só por inspeção:** REQ-003, 004, 005, 017, 018, 022, 028, 029, 030, 033, 049.

## 5. Regra de parada e revisão

25 achados distintos ao fim de M7; triagem dos P0 concluída; busca não ampliada. A revisão independente concordou com os 12 achados Alta no núcleo factual (4 sem ressalva, 8 com correção), divergiu de zero, rebaixou 5 para Média, apontou evidências não arquivadas (agora arquivadas e reexecutadas) e 5 classes de requisito ausentes (agora REQ-051..055). Condição de reclassificação registrada: F-12 + F-13 passam a Crítica se a pilha de PRs for mesclada com auditor semântico da mesma família.

## 6. O que esta cobertura NÃO afirma

Não afirma cobertura completa do GCI (estudos quantitativos, coletores e o motor de síntese #208 só inspecionados), nem independência estatística entre auditor, revisor independente e sistema (mesmo fornecedor de modelo).
