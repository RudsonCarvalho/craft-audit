# Sumário executivo — Auditoria adversarial independente do GCI

Auditoria `GCI-ADV-2026-11-03-01` (protocolo v2). Snapshot: GCI `main` @ `7d49d051` (2026-10-31) e knowledge-hub `main` @ `66bdcb62` (2026-10-29); pilha de PRs "DO NOT MERGE YET" auditada como código em PR (SHAs em `manifest/audit-manifest.json`). Cada conclusão abaixo aponta para achados (`findings/findings.json`, índice em `final/findings-index.json`) e evidências. Este sumário não substitui os relatórios de missão; condições e limitações estão lá.

## 1. Resposta à pergunta de sucesso

**Em quais circunstâncias o GCI produz uma conclusão materialmente incorreta mesmo com especialistas, revisores e agregadores "concluídos"?** Com evidência reproduzida nesta auditoria, em cinco circunstâncias:

1. **Quando a conclusão é escrita em texto livre pelo líder.** Na rodada 2 real de H07 o resumo consolidado omitiu um contraexemplo candidato entregue pelo revisor (TBLE3 −12%, Tractebel, cuja não exposição a rodada 1 deixou como não verificada) e rotulou uma transmissora (Taesa) como distribuidora; o handoff repetiu a frase e acrescentou uma afirmação inverificável por desenho (recusas de entrega não são gravadas). O número está na ficha e no Radar; a distorção está no texto que o próximo líder lê. Nenhum controle existe sobre esse texto. (**F-01**, Média após revisão; `evidence/m5/trace_h07_round2.json`)
2. **Quando a informação está em claims `neutral`, em `companies[]`, em `post_event` ou nas notas.** A projeção para a ficha descarta 81% das claims da rodada (as neutras); o Radar mostra as 41 evidências, mas projeta o corpo das notas como `note: null` e não expõe `needs_human_review`, a recomendação `inconclusive`, conflitos nem testes de refutação; `companies[]` perde seis de nove campos; o marcador estruturado `post_event` desaparece (a ressalva sobrevive só no texto da evidência). (**F-02** Alta; **F-03** Média)
3. **Quando a evidência nova contradiz os fatos da própria ficha.** O detector de conflitos só cruza `for`×`against` entre entregas; a claim do revisor cujo escopo temporal (`as_of` 31/10, escolhido pelo líder) contradiz o episódio de nov–dez em `facts.episodes` entrou sem alerta. Reação de preço de ativos selecionados pelo resultado entrou como `fact` a favor. (**F-07, F-21**)
4. **Quando a independência do revisor é só formal.** O snapshot "congelado" transporta `date_note`, inferência do líder e confiança rebaixada da rodada anterior (ancoragem não demonstrada neste caso); o isolamento é por nome de arquivo e hash exato; nenhuma identidade de modelo é registrada; o normalizador de família de modelo da pilha de PRs aceita `Claude Sonnet 4.5` como distinto de `claude-sonnet-4-5` e Sonnet como distinto de Opus, inclusive em D4; toda a cadeia (especialistas, revisor, líder, revisores dos PRs, este auditor e o revisor independente desta auditoria) é da mesma família de fornecedor. (**F-13** Alta; **F-04, F-05, F-06, F-14** Média)
5. **Quando um número de outra série, outra direção ou outra entidade substitui o original dentro de uma compressão.** O store de séries aceita a troca NBS↔RatingDog como "revisão"; o auditor de fidelidade do PR #215 não levanta nenhuma suspeita pertinente para entidade trocada, dupla negação, direção da surpresa invertida, `1,106`→`1.106` milhão (falha da própria camada numérica) e qualificador inventado, e levanta a suspeita errada para `%`→`pontos` e série homônima; com auditor semântico leniente os 8 recebem `pass` e envelope de publicação; e `scenario_probability` aceita pontuação de LLM com `calibration_ref` textual. (**F-10, F-12, F-08**)

Nenhum achado foi classificado **Crítica**: em todos os casos reproduzidos resta rastro no log append-only (`hig-dossier`) ou no tombstone; a perda ocorre nas camadas de resumo, projeção e decisão, que é onde o operador lê. Após a revisão independente: **7 Alta** (F-02, F-07, F-08, F-10, F-12, F-13, F-15), **16 Média**, **2 Baixa**; 17 confirmados por reprodução e 8 por inspeção documental. Cinco achados foram rebaixados de Alta para Média porque os originais não sustentam o caminho de impacto alegado (F-01, F-03, F-04, F-05, F-18). Condição de reclassificação: F-12 combinado com F-13 passa a Crítica se a pilha de PRs for mesclada com um auditor semântico da mesma família do compressor.

## 2. Casos obrigatórios

- **PMIs (M2).** Valores recuperados das fontes: NBS 50,3% (abr) e 50,0% (mai), publicados 2026-04-30 e 2026-05-31 às 09:30 de Pequim; RatingDog 52,2 (abr) e 51,8 (mai), por fontes secundárias datadas porque a S&P Global bloqueou o fetcher (403). O consenso de maio é **51,6 (Reuters) ou 51,4 (provedor não nomeado)**: a surpresa é +0,2 ou +0,4 e a variação mensal é −0,4. O exemplo da issue #194 só vale para um dos provedores. A fixture **não é cega** (sem controlador). (**F-10, F-11, F-19**; `missions/M2-series-audit.md`)
- **Frigoríficos (M3, F-18 Média após revisão).** O evento de 20–21/05/2026 (JBS Pontes e Lacerda SIF 51, PrimaFoods Araguari SIF 177, Vale Grande/Frialto Matupá SIF 4490; acetato de medroxiprogesterona) tem um **homônimo**: a nota oficial do MAPA hospedada sob `poder360.com.br/2026/05/` é a de **04/03/2025**, sobre outro motivo (vídeo-auditoria) e, segundo o Poder360, outro trio de plantas, reabilitadas um dia antes; o PDF em si não nomeia as plantas. Minerva (BEEF3) não é parte do evento. A cota (1,106 Mt, +55% acima) estava em 80% só em 21/07; a alegação "50% em maio" não foi verificada. Preços: **bloqueados**. O GCI atual devolve `no_match` e nenhuma identidade de evento ou decomposição causal existe. (**F-18**; `missions/M3-causality-audit.md`)

## 3. Riscos não confirmados (registrados, não demonstrados)

Síntese #208 (árbitro) só inspecionada; gate cumulativo IEC e checkpoints #213 não sondados; comportamento do auditor semântico real desconhecido (todos os benchmarks dos PRs usam stubs); integração PostgreSQL não exercitada (68–69 testes ignorados); estudos quantitativos e holdout só por inspeção de guardas.

## 4. Controles eficazes (manter)

Log encadeado detecta edição/remoção interna; `calibrated_probability` nulo na ficha; `as_of`/`post_event` na validação de entrega; chaves de ordem recusadas em todos os contratos; board recusa citação sem relação com a claim; CAS, idempotência estrita, tombstones e propagação `stale` no documento por seções; gate de fidelidade recalcula a decisão; `no_match`/`discovery_suggestion` em vez de hipótese automática; `abster`/`inconclusive`/`not_assessable` como saídas válidas; FedWatch recusado como consenso.

## 5. Menor conjunto de correções (detalhe em `final/remediation-plan.md`)

Lote 1 (sete mudanças pequenas na `main`): payload completo na reconciliação com `post_event`; resumo por template a partir das claims e `head` do log no handoff; snapshot do revisor em modo D1 puro; isolamento por conteúdo; conflito evidência×fatos; Radar expondo notas e rótulo de incompletude; `calibration_ref` resolvido. Lote 2 (antes de mesclar #206–#212): tabela explícita de fornecedor/família de modelo, autoridades autenticadas, identidade composta de série, validadores de entidade/direção/unidade no #211, herança de contrárias por similaridade e gate obrigatório no #212.

## 6. Cobertura e limites

50 requisitos congelados (25 P0; todos com resultado): 16 aprovados, 9 com ressalva, 16 falharam, 7 inexistentes, 2 inconclusivos; mais 5 requisitos (REQ-051..055, de #173/#195) acrescentados após a revisão independente e não testados (`final/coverage-report.md`). Dependências: mesmo fornecedor de modelo em toda a cadeia, inclusive este auditor; sem controlador independente para fixtures cegas; sem banco; três fontes bloqueadas. Nenhuma afirmação de confiabilidade absoluta ou cobertura completa.

## 7. Revisão independente

Avaliador: subagente `claude-opus-5-5` (mesmo fornecedor do auditor e dos agentes do GCI, e mesmo modelo de quatro revisões de PR criticadas; dependência declarada em `final/independent-review.md#2`). Recebeu os relatórios de missão, as evidências, as fixtures e os repositórios originais, não este sumário.

| Resultado | Achados |
|---|---|
| Concorda sem ressalva (reproduziu com sondas próprias) | F-08, F-10, F-13, F-15; Médias F-06, F-11, F-20 |
| Concorda com correção, severidade mantida | F-02 (Radar mostra 41 evidências; perda é do sinal de revisão humana), F-07 (conflito de escopo temporal), F-12 (camada determinística sem suspeita em 5 casos; F6 é falha numérica), F-14 (ack é comportamento projetado), F-22 (head está fixado em `H07_gate_check.json` e `status.jsonl`) |
| Concorda com correção, **rebaixado para Média** | F-01 (TBLE3 está na ficha; Tractebel não verificada; "recusada uma vez" é inverificável por desenho), F-03 (ressalva sobrevive no texto), F-04 (ancoragem não demonstrada), F-05 (4 de 6 revisões declaram Opus; normas do hub são draft), F-18 (PDF não nomeia plantas; impacto hipotético) |
| Diverge | nenhum |
| Não resolvido | fontes web de M2/M3 não re-buscadas; `validate_review` D4 não re-executado ponta a ponta; 14 issues não relidas; PostgreSQL |

Omissões do auditor aceitas e corrigidas: evidências de sondas não arquivadas (agora em `fixtures/m2,m4,m6,m7` e `evidence/m2,m4,m5,m6,m7`, reexecutadas com os mesmos resultados, e com uma observação nova: em D3 um ack por `orquestrador` fechou o run `ok` com revisor = produtor); IDs trocados entre relatórios (corrigidos antes da revisão terminar, mas lidos por ela na versão anterior); SRC-M3-01 atribuía ao PDF nomes que não estão nele; cinco classes de requisito de #173/#195 ausentes (REQ-051..055 na matriz v3). A revisão considera "0 Crítica" defensável hoje e condiciona a reclassificação de F-12/F-13 à mesclagem da pilha com auditor da mesma família. A revisão cruzada por outro fornecedor continua pendente e é a limitação principal desta auditoria.
