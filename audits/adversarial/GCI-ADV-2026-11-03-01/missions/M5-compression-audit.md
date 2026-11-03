# M5 — Compressão e perda de contexto

Prioridade máxima após M1. Pergunta: em que ponto da cadeia **documento original → extração → compressão → transferência entre agentes → consolidação** fatos, números, ressalvas, contradições, fontes e contraexemplos desaparecem, e se algum controle detecta isso. Dois objetos: (A) a cadeia real em `main` (rodada 2 de H07, 2026-10-31) e (B) o Compression Fidelity Auditor do PR #215 (#211).

## A. Cadeia real em `main` (H07, rodada 2)

Script: `fixtures/m5/trace_h07_round2.py`; saída: `evidence/m5/trace_h07_round2.json`. Comparação direta original × saída em cada transformação.

| Transformação | Original | Saída | Perda medida |
|---|---|---|---|
| Entrega do especialista → `validate_deliverable` | 32 claims (7 fund, 15 dados, 10 rev), 15 `companies[]`, 5 explicações alternativas, 4 testes de refutação, 16 perguntas | aceitas (14 avisos `pre_event=false`) | nenhuma |
| `plan_reconciliation` → payload de evidência no log | claim com `post_event`, `subject`, `companies[]` com 9 campos | payload com 11 campos **sem `post_event`**; `companies[]` na nota com **4 de 9 campos** (`exposure_basis`, `source_url_or_ref`, `source_public_date`, `evidence_class`, `exposed_assets`, `tickers` descartados) | **flag ex-post perdida; base e fonte da exposição perdidas** |
| log → ficha `.md` (`apply_to_card`) | 32 evidências (26 neutral, 4 against, 2 for) | `evidence_for` 6, `evidence_against` 9; **0 neutral**; `dossier` da ficha ainda descreve a rodada 1 | **26 de 32 claims (81%) não aparecem na ficha**; perguntas abertas, testes de refutação e explicações alternativas só no log |
| log → Radar `GET /api/hypotheses/H07` | nota `investigation_round` com `summary`, `conflicts`, `human_review_reasons`, `recommended_states`, `refutation_tests`, `companies` | `notes[]` projeta `{seq, at, actor, note_kind, note}` → **`note: null`**; `refutation`, `human_review_reasons`, `recommended_state`, `conflicts`, `exposure_share` ausentes do JSON; `next_questions` (26) e `alternative_explanations` presentes; evidências neutras presentes em `evidence.neutral` | **resumo da rodada e sinalizadores de revisão humana não chegam à interface** |
| log → Radar `changes?since=` | idem | nenhum texto de claim; `TBLE3`, `Rede Energia`, `needs_human_review` ausentes | o "o que mudou" não carrega conteúdo |
| nota do líder (`summary`) e `docs/PROJECT-STATE.md` | revisor: "TBLE3 −12,0%" (Tractebel, geradora **sem** concessões vincendas segundo a rodada 1), LIGT3 −6,8%, CLSC4 −6,4%, COCE5 −6,0% | "quedas... concentradas em geradoras/transmissoras (CESP, CTEEP, Cemig, AES Tietê) e **quase nulas em distribuidoras (Eletropaulo, EDP, Equatorial, Taesa; CPFL +10%)**, coerente com o mecanismo" | **contraexemplo TBLE3 omitido; Taesa (transmissora) rotulada distribuidora**; PROJECT-STATE repete "fortes em geradoras/transmissoras e quase nulas em distribuidoras" e acrescenta "a do revisor foi recusada uma vez por campo trocado" **sem nenhum evento `rejected` em `status.jsonl`** |

Também: a claim `for` do revisor ("maiores variações negativas... CESP6 −35,8%...") entra na ficha como `fact` a favor: é reação de preço dos **próprios ativos selecionados por terem caído** (seleção na variável dependente), fornecida pelo líder como material. Nenhum gate marca a circularidade.

**Achados**
- **F-01 (Alta; reprodução).** O resumo livre do líder elimina um contraexemplo e distorce um rótulo setorial; o handoff repete e acrescenta um fato sem rastro. Não existe controle (REQ-012 inexistente). Rastro fica no log (por isso Alta, não Crítica).
- **F-02 (Alta; reprodução).** Projeções (ficha, Radar) descartam 81% das claims da rodada e o corpo das notas; `companies[]` perde base/fonte/classe. Documentado em parte ("neutral fica só no log"), mas sem teste de fidelidade e sem rótulo de incompletude na saída (REQ-010 falhou).
- **F-03 (Alta; reprodução).** `post_event` não sobrevive à reconciliação: a alegação de imprensa pós-evento vira `evidence_for` sem o marcador que, pelo contrato, "nunca prova exposição ex ante" (REQ-008/009 falharam neste ponto).
- **F-07 (Alta; reprodução).** A claim `against` do revisor ("sem queda marcante de ELET3 após 14/09; 15–31/10 −6,5%") contradiz `facts.episodes` da ficha (episódio ELET3 2012-10-18→12-17, pico −48,5%) porque o `as_of` do revisor era 2012-10-31; `_conflicts` só compara `for`×`against` entre entregas por `subject`/Jaccard e **não** olha os fatos da ficha. Entrou na ficha como `evidence_against` sem conflito registrado (REQ-011 falhou).
- **F-21 (Média; inspeção).** Reação de preço de ativos selecionados pelo resultado registrada como `fact` a favor (circularidade sem gate).

## B. Compression Fidelity Auditor (PR #215, `compression_fidelity.py`, 2.133 linhas)

Harness: `World`/`FakeModel` de `tests/test_fidelidade_211.py` com o auditor **leniente** (descarta toda suspeita, como permitido pela porta `SemanticAuditor`). Fixture e saídas: `fixtures/m5/fidelity_211_probes.json`. 13 casos (2 controles, 11 defeitos novos, fora da amostra do PR).

| Sonda | Defeito plantado | Determinístico | Decisão / gate |
|---|---|---|---|
| F0 | nenhum (controle) | — | pass / permitido |
| F1 | base de comparação 1T26→2T25 | `data_ausente_no_original` | fail / recusado |
| F2 | entidade Alfa→Beta, números iguais | nenhum | **pass / permitido** |
| F3 | dupla negação invertida | nenhum | **pass** (limitação documentada) |
| F4 | "51,8 abaixo do consenso de 51,6" (direção invertida) | nenhum | **pass / permitido** |
| F5 | variação mensal rotulada surpresa com número novo (0,4) | `numero_ausente_no_original` (crítica) | fail / recusado |
| F6 | "1,106 milhão" → "1.106 milhão" (×1000 em pt-BR) | nenhum: `scan_numbers` lê "1,106" como {1.106, 1106} | **pass / permitido** |
| F7 | "50,0%" → "50,0 pontos" | nenhum (`unit_class` só `pct`/`pp`/escala) | **pass / permitido** |
| F8 | ressalva "exceto na unidade Gama" removida | suspeita `ressalva_removida` | **pass** com auditor leniente |
| F9 | data 30/06/2026 → 2026-06-30 | `data_ausente_no_original` | fail (falso positivo documentado) |
| F10 | NBS rotulado RatingDog | nenhum | **pass / permitido** |
| F11 | "em todas as unidades" inventado | nenhum | **pass / permitido** |
| F12 | controle: claim sem a tarifa (não exigida) | — | pass |

Resultado: dos 11 defeitos, **2 barrados** (F1, F5), **8 passam pelo gate** (F2, F3, F4, F6, F7, F8, F10, F11), 1 falso positivo (F9). O gate de publicação depende integralmente do auditor semântico para entidade, direção, qualificadores, ressalvas e homônimos; e o auditor semântico aceito é qualquer modelo de "família" distinta pela normalização de `model_id` (ver M7, F-13).

**Achado F-12 (Alta; reprodução).** Os validadores determinísticos cobrem números/períodos/datas/escala, mas não entidade, direção, unidade `pontos`, separador de milhar pt-BR com vírgula, rótulo de série, nem qualificadores; com auditor leniente ou da mesma família, artefatos materialmente errados recebem `pass` e `publication_envelope`. O README do PR declara que as heurísticas "sinalizam suspeita" e que a cobertura 13/13 é "dentro da amostra"; esta auditoria confirma 8/11 fora da amostra.

Controles eficazes observados: `EvidenceBoard.add_evidence` recusou citação sem relação com a claim ("termos em comum: ['milhao','toneladas']; número da claim (2026) não está na citação"); manifest obriga contabilizar toda unidade; locator fora da missão/inexistente recusado; `check_publication` recalcula a decisão.

## C. Resultados por requisito (v2)

REQ-008 ressalva (post_event perdido a jusante); REQ-009 **falhou** (perda de campos em `companies[]`, `post_event`); REQ-010 **falhou** (F-02); REQ-011 **falhou** (F-07); REQ-012 **falhou/inexistente** (F-01); REQ-029/030 aprovados por inspeção (não sondados: `reduce_claims` determinístico; `assemble_decisions` força `needs_review` sem retrieval); REQ-031 **falhou** (F-12); REQ-032 ver M7 (F-13); REQ-033 aprovado por inspeção; REQ-038 inconclusivo (sem benchmark com modelo real, declarado pelo PR).


## D. Errata (v2, após revisão independente)

- A: "o contraexemplo só existe no log" é **falso**: TBLE3 −12,0% está na ficha (`H07.md:904`, `evidence_for[5]`) e no Radar. A não exposição da Tractebel é "não verificada" na rodada 1, logo TBLE3 é contraexemplo **candidato**. A frase "recusada uma vez" do PROJECT-STATE é inverificável por desenho (`submit_task` não grava recusas), não "sem rastro" por omissão. **F-01 rebaixado para Média.** Permanece a omissão no `summary` e o rótulo errado de Taesa.
- A (F-02): o Radar **não** descarta claims (41 evidências, inclusive 26 neutras); o descarte de 81% é da ficha `.md`. A perda material no Radar é o `summary`, `needs_human_review`, `recommended_states`, `conflicts`, `refutation_tests` e os campos de `companies[]`.
- A (F-03): o texto da evidência na ficha conserva "posterior ao as_of e não prova exposição ex ante"; a perda é do marcador estruturado. **F-03 rebaixado para Média.**
- A (F-07): é conflito de **escopo temporal** (as_of 2012-10-31 escolhido pelo líder) não sinalizado, não contradição factual direta; severidade mantida.
- A: a nota do líder registra em texto "Seleção retrospectiva… é circular" (F-21 corrigido: reconhecido em texto, não em estrutura).
- B: `fixtures/m5/fidelity_211_probes.json#results` agora traz decisão, gate, achados e suspeitas por caso (a versão anterior gravou só nomes); saída de reexecução em `evidence/m5/fidelity_211_probes.rerun.out`. Redação de F-12: o dado central é que em F2, F3, F4, F6 e F11 a camada determinística não levanta **nenhuma** suspeita pertinente, e F6 (×1000) é falha da camada numérica.
