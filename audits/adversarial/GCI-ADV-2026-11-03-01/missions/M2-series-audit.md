# M2 — Identidade de séries e surpresa econômica

Caso obrigatório: PMIs chineses da NBS e RatingDog/S&P Global, abril e maio de 2026. Fontes em `evidence/m2-sources/sources.json`. Fixture aberta em `fixtures/m2/`. Código auditado: `series_store.py`, `series_consensus.py`, `release_calendar.py` (PR #161/#170, worktree `gci-pr-167`/`gci-pr-208`) e `compression_fidelity.py` (PR #215) para claims sobre PMI.

## 1. Valores recuperados das fontes (não do prompt)

| Série (identidade) | Período | Valor | Variação m/m | Publicação | Disponibilidade / revisão | Fonte |
|---|---|---|---|---|---|---|
| NBS/CFLP 制造业PMI (oficial; ~3.000 empresas; sazonalmente ajustado, segundo a NBS) | abr/2026 | **50,3%** | −0,1 pp | 2026-04-30 09:30 (Pequim) | release em inglês com data 2026-05-01 09:30 e URL `20260506` (SRC-M2-03); nenhuma revisão observada | SRC-M2-01 (primária, lida) |
| NBS/CFLP 制造业PMI | mai/2026 | **50,0%** | −0,3 pp | 2026-05-31 09:30 (Pequim; domingo) | — | SRC-M2-02 (primária, lida) |
| S&P Global **RatingDog** China General Manufacturing PMI (painel ~650 empresas, compilado pela S&P Global) | abr/2026 | **52,2** | +1,4 (ante 50,8) | 2026-04-30 ~01:45 GMT | coleta 9–22/abr (só por fonte secundária) | SRC-M2-05 **bloqueada (HTTP 403)**; SRC-M2-08 (MNI) |
| S&P Global RatingDog | mai/2026 | **51,8** | −0,4 (ante 52,2) | 2026-06-01 ~01:45 GMT (embargo) | coleta 12–20/mai (secundária) | SRC-M2-04 **bloqueada (HTTP 403)**; SRC-M2-06 (RTHK), SRC-M2-07 (investinglive) |
| Consenso para RatingDog mai/2026 | mai/2026 | **51,6** (Reuters poll) **ou 51,4** (provedor não nomeado) | — | antes de 2026-06-01 (cutoff não publicado) | dois provedores divergem | SRC-M2-06 vs SRC-M2-07/09 |

Leituras: (a) os valores citados no texto da issue #194 (NBS 50,0 ante 50,3; RatingDog 51,8 ante 52,2) **conferem** com as fontes; (b) a "surpresa +0,4" da issue só vale para o consenso 51,4 de provedor não nomeado: contra o Reuters poll (51,6) a surpresa é **+0,2**. A variação mensal (−0,4) e a surpresa (+0,2/+0,4) têm sinais opostos: é o caso de inversão de interpretação pedido em #183; (c) a fonte primária RatingDog não pôde ser lida nesta sessão (403); tudo sobre RatingDog está em grau **secundário datado**; (d) a NBS publica em chinês às 09:30 e a versão em inglês carrega data posterior: disponibilidade para um público não é a mesma coisa que publicação; (e) o NBS PMI é publicado pelo Centro de Pesquisa de Serviços da NBS com a CFLP, e o RatingDog é compilado pela S&P Global com patrocínio RatingDog: são **duas séries**, com painéis, metodologias e datas distintas, não uma revisão da outra. A afirmação de que o índice RatingDog é o sucessor do antigo índice patrocinado pela Caixin é conhecimento prévio do auditor e **não foi verificada em fonte nesta sessão**.

## 2. Testes executados

### 2.1 Fixture aberta (não cega)

`fixtures/m2/pmi_fixture_open.json` tem 8 observações; o gabarito (`.key.json`) está no mesmo diretório e foi escrito pelo próprio executor. **Não houve controlador independente; o ensaio não é cego** (limitação declarada no manifesto). Erros plantados: O5 (valor NBS 50,0 rotulado RatingDog) e O8 (variação mensal −0,4 rotulada surpresa).

### 2.2 Store de séries (PR #161) — troca de série homônima

Script no histórico de evidências (`evidence/` → saída reproduzida em `missions/M2`): duas capturas com o mesmo `series_id` escolhido pelo chamador (`china_pmi_manufacturing`), uma da NBS (50,3/50,0) e outra da RatingDog (52,2/51,8), com `dataset_id` e `source_url` diferentes.

| Observação | Resultado |
|---|---|
| `record_capture` da RatingDog após a NBS | `revised=2`: o store gravou 52,2 e 51,8 como **revisões** dos valores NBS (`revision_of` apontando para a vintage NBS) |
| `as_of(2026-06-02)` para 2026-05 | devolve **51,8 (pmi.spglobal.com)**, com `revision_of` da NBS |
| `first_release` para 2026-05 | devolve 50,0 (NBS) |
| Identidade da série | só `series_id`, `unit`, `definition` (texto livre); `dataset_id`, `source_url` e publisher **não** entram na identidade nem geram erro |

**Achado F-10 (Alta; confirmado por reprodução):** a identidade estatística exigida em #194/#207 (publisher, metodologia, amostra, ajuste, vintage) não existe no modelo de dados; a troca de série homônima vira "revisão" silenciosa, e o valor "mais recente" passa a ser o de outra instituição.

### 2.3 Surpresa (PR #161) — fail-closed inoperante

`surprise()` exige `available_precision != "upper_bound"`, mas `record_capture` grava **sempre** `available_precision="upper_bound"` (linha 234 de `series_store.py`); nenhum caminho de produção (`series_eia.py`, `series_cli.py`) grava `exact`/`day`. O comando `catalyst series surprise` usa `store.first_release`, logo devolve `not_assessable` ("publicação do realizado inicial não comprovada") para **qualquer** dado carregado pelo próprio store. Os testes que mostram `assessed` constroem `SeriesObservation` à mão.

**Achado F-11 (Média; confirmado por reprodução + inspeção):** a capacidade "surpresa fail-closed" anunciada no PR #161 é inalcançável de ponta a ponta; o resultado é honesto (`null`), mas um leitor do PR concluiria que a surpresa está implementada. Controles positivos observados: FedWatch recusado como consenso (`kind`), consenso capturado após a divulgação recusado, unidade/definição divergentes recusadas, `contract` de licença obrigatório; o campo `provider` existe no `ConsensusSnapshot` (bom: permite registrar 51,4 e 51,6 como objetos distintos).

### 2.4 Auditor de fidelidade (PR #215) sobre claims de PMI

Sondas F4, F5, F7, F10 de `fixtures/m5/fidelity_211_probes.json` (auditor semântico leniente):

| Sonda | Artefato | Decisão | Gate |
|---|---|---|---|
| F10 | NBS 50,0% rotulado "PMI RatingDog" | **pass** | permitido |
| F4 | "51,8 **abaixo** do consenso Reuters de 51,6" (sinal invertido, números iguais) | **pass** | permitido |
| F5 | "surpresa negativa de **0,4**" (variação m/m rotulada surpresa) | fail (`numero_ausente_no_original`) | recusado |
| F7 | "50,0 **pontos**" para original "50,0%" | **pass** (suspeita `negacao_perdida` descartada pelo auditor leniente) | permitido |

O validador determinístico só pega a troca quando ela introduz um **número novo**; nome da série, direção da surpresa e classe de unidade `%`→`pontos` passam.

## 3. Resultados por requisito (matriz v2)

| REQ | Resultado | Evidência |
|---|---|---|
| REQ-025 identidade estatística | **falhou** (F-10) | `series_store.py`; sonda 2.2 |
| REQ-026 surpresa só com consenso nomeado ex ante | **falhou** parcialmente (F-11: inoperante via store; regras corretas em isolamento) | `series_consensus.py`; sonda 2.3 |
| REQ-027 vintages/revisão | aprovado com ressalva (revisão correta, mas identidade fraca permite "revisão" espúria) | sonda 2.2 |
| REQ-028 agenda vs publicação | aprovado por inspeção (`scheduled_at` ≠ `published_at`, versionado) | `release_calendar.py` |
| REQ-050 quatro datas | **inconclusivo**: o store acomoda `published_at`, `available_at`, `captured_at` e revisão, mas não distingue disponibilidade por público/idioma (caso NBS inglês) nem registra fuso de origem além do UTC | sonda 2.2; SRC-M2-03 |
| REQ-001 PIT | aprovado por inspeção (upper_bound conservador) | idem |

## 4. Limitações

Primária RatingDog bloqueada; consenso de provedor não nomeado; fixture não cega; nenhum acesso a Bloomberg/Refinitiv; os horários "01:45 GMT" vêm de agregadores.


## 5. Errata (v2, após revisão independente)

- §2.2: o script da sonda do store e sua saída não estavam arquivados; agora estão em `fixtures/m2/store_homonym_probe.py` e `evidence/m2/store_homonym_probe.out` (reexecutados; mesmo resultado). A revisão independente reproduziu a troca de série de forma autônoma.
- §2.4: em F7 e F10 a camada determinística levanta a suspeita `negacao_perdida`, que não é a do defeito plantado (o M5 dizia "nenhum" para F7; a tabela deste relatório está correta).
