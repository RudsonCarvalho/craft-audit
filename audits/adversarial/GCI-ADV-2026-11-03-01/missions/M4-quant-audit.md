# M4 — Correlações e modelos probabilísticos

Escopo: janela/frequência/moeda/regimes/informação futura/fora da amostra; distinção entre probabilidade física, implícita, subjetiva, reação condicional e retorno esperado; reconhecimento de dados insuficientes. Código em `main` (`decision_gate.py`, `trigger_ontology.py`, `hypothesis_card.py`, `event_matcher.py`, guardas de holdout) e em PR (`roles.py` #209; `series_consensus.py` #161; `iec_contracts.py` #214). Nenhum motor de cenários/probabilidades existe (#219–#222 são só issues).

## 1. Inventário

| Capacidade | Estado | Observação |
|---|---|---|
| Motor de cenários condicionais, soma 1, conjuntas por caminho, `probability_not_assessable` (#219) | **inexistente** | só issue (2026-11-03) |
| Fontes de probabilidade implícita, quarentena MNPI (#220) | **inexistente**; só `catalog.py` (direitos por uso, PR #157/#163) e `series_consensus.KINDS` (FedWatch ≠ consenso) | parcial |
| Atualização dependente/bayesiana (#221), calibração/Brier (#222) | **inexistentes** | só issues |
| Regimes, correlações com janela/moeda/frequência (#183/#195/#197) | **inexistentes** | nenhum módulo de correlação macro em `src/` |
| Guardas contra probabilidade inventada | `calibrated_probability` nulo (ficha/log/decisão), `scenario_probability` em gatilho só com `scenario_probability_source`, chaves proibidas em papéis | existem, com furos (abaixo) |
| Holdout 2022–2025 | `HOLDOUT_YEARS` em `event_first.py` e `roles.py`; recusa em CLIs de estudo | inspeção; não exercitado sem banco |
| Dados insuficientes como saída válida | `inconclusive` em entregas, `not_estimable/unknown` nas 4 dimensões da decisão, `abster` nos papéis, `not_assessable` na surpresa | controles positivos |

## 2. Sondas (reproduzíveis; saídas em `evidence/m7_isolation_and_gate_probes.txt` e no histórico desta missão)

| ID | Sonda | Resultado |
|---|---|---|
| P-A | `validate_decision_record` com `scenario_probability.value=0.62`, `method="pontuação do agente Sonnet (escala 0-1) convertida em probabilidade"`, `calibration_ref="calibracao_v0"` | **ACEITO** |
| P-B | idem com `method="LLM score"` | rejeitado (lexicon `llm|gpt|claude|gemini|language model|modelo de linguagem|chatbot`) |
| P-C | `calibration_ref="docs/calibracao/nao_existe.json"` (caminho inexistente) | **ACEITO** (referência não é resolvida) |
| P-D | `status=not_estimable`, `note="o agente estima 60% de chance de corte de 50pb"` | **ACEITO** (percentual subjetivo sobrevive em texto livre) |
| P-E | ficha H07 com `assessment.calibrated_probability=0.6` | rejeitado (correto) |
| P-F | ficha H07 com `triggers[0].scenario_probability=0.6`, `scenario_probability_source="estimativa do agente Sonnet"` | **ACEITO** pelo validador da ficha |
| P-G | `roles.scan_forbidden` sobre textos: "probabilidade de 60%" / "60 percent probability" | barrados (`ROLE-CAPITAL`) |
| P-H | "probabilidade de 0,6", "6 chances em 10", "odds de 3 para 2", "provável (p=0,6)", "60% dos cenários", "60 por cento" | **PASSAM** |
| P-I | `gate_check(H07, validation_ready, {timestamps_checked: true, independence_checked: true})` | `ready=True` com 3 avisos (needs_human_review, revisor recomendou inconclusive, 41 evidências não verificadas): avisos não bloqueiam |

## 3. Achados

- **F-08 (Alta; reprodução).** A regra "nenhuma probabilidade de LLM vira número" é implementada por **léxico** e por um `calibration_ref` textual não resolvido. Um agente que escreva "pontuação do agente Sonnet" e `calibration_ref="calibracao_v0"` registra `scenario_probability=0,62` em decisão humana; o mesmo valor entra em `triggers[].scenario_probability` da ficha com `source` livre. O Radar exibe gatilhos. Impacto: probabilidade subjetiva não calibrada pode chegar ao registro de decisão e à ficha com aparência de dado.
- **F-09 (Média; reprodução).** O filtro de probabilidade nos papéis Explorador/Estrategista (PR #209) só pega "%" junto de "probab/chance". Decimais, odds, "6 em 10", "por cento" passam. O ADR 007 declara que o filtro é heurístico e que a admissibilidade é do revisor; o revisor é o mesmo modelo (ver M7).
- **F-20 (Média; reprodução).** O gate `validation_ready` fica `ready=True` só com dois atestados booleanos do operador, mesmo com `needs_human_review`, recomendação `inconclusive` do revisor e 100% das evidências não verificadas. Documentado como atestado; porém o código não exige que os avisos sejam reconhecidos.
- **F-17 (Média; inspeção documental).** Não há motor probabilístico, calibração, correlação com janela/moeda/frequência nem regimes. Toda alegação dessas classes nos documentos de PR (ex.: `role_prompts/estrategista.md` "surpresa versus curva") depende de texto do modelo; nenhum número pode ser verificado por código.

## 4. Controles eficazes observados

`calibrated_probability` nulo imposto em ficha, log e projeção; `solicitar_estudo` exige discussão de impacto e precificação; chaves de ordem recusadas em decisão/entrega/papéis; `kind` do consenso separa expectativa implícita de consenso de analistas; `abster`/`inconclusive`/`not_assessable` são saídas válidas em todos os contratos; `as_of` nas entregas bloqueia evidência futura sem `post_event`.

## 5. Resultados por requisito (v2)

REQ-002 **falhou** (F-08); REQ-003 aprovado por inspeção (não exercitado); REQ-015 aprovado com ressalva (F-21); REQ-016 aprovado (chaves) / ressalva (texto livre, P-D); REQ-041, 042, 043, 045, 046 **inexistentes** (REQ-043 com sonda P-H mostrando furo no único controle existente); REQ-044 parcial (FedWatch recusado; MNPI inexistente).


## 6. Errata (v2, após revisão independente)

- As sondas P-A..P-H não estavam arquivadas em `evidence/`; agora estão em `fixtures/m4/probability_guard_probes.py` e `evidence/m4/probability_guard_probes.out` (reexecutadas; mesmo resultado).
- F-08: nenhuma ficha real tem `scenario_probability` numérico e nenhuma decisão de H07 foi registrada; o risco é de capacidade.
