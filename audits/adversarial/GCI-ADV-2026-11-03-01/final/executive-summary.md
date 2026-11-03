# Sumário executivo — Auditoria adversarial independente do GCI

Auditoria `GCI-ADV-2026-11-03-01` (protocolo v2). Snapshot: GCI `main` @ `7d49d051` (2026-10-31) e knowledge-hub `main` @ `66bdcb62` (2026-10-29); pilha de PRs "DO NOT MERGE YET" auditada como código em PR (SHAs em `manifest/audit-manifest.json`). Cada conclusão abaixo aponta para achados (`findings/findings.json`, índice em `final/findings-index.json`) e evidências. Este sumário não substitui os relatórios de missão; condições e limitações estão lá.

## 1. Resposta à pergunta de sucesso

**Em quais circunstâncias o GCI produz uma conclusão materialmente incorreta mesmo com especialistas, revisores e agregadores "concluídos"?** Com evidência reproduzida nesta auditoria, em cinco circunstâncias:

1. **Quando a conclusão é escrita em texto livre pelo líder.** Na rodada 2 real de H07 o resumo consolidado omitiu o único contraexemplo setorial entregue (TBLE3 −12%, geradora sem concessões vincendas) e rotulou uma transmissora como distribuidora; o handoff repetiu a frase e acrescentou um fato sem rastro. Nenhum controle existe sobre esse texto. (**F-01**; `evidence/m5/trace_h07_round2.json`)
2. **Quando a informação está em claims `neutral`, em `companies[]`, em `post_event` ou nas notas.** A projeção para a ficha e para o Radar descarta 81% das claims da rodada, o corpo das notas (`note: null`), seis de nove campos de exposição e o marcador `post_event`, de modo que uma alegação de imprensa pós-evento aparece como evidência a favor. (**F-02, F-03**)
3. **Quando a evidência nova contradiz os fatos da própria ficha.** O detector de conflitos só cruza `for`×`against` entre entregas; a claim do revisor que contradiz `facts.episodes` entrou sem alerta. Reação de preço de ativos selecionados pelo resultado entrou como `fact` a favor. (**F-07, F-21**)
4. **Quando o "revisor independente" é o mesmo modelo lendo um snapshot que já contém as conclusões.** O snapshot "congelado" transporta `date_note`, inferência do líder e confiança rebaixada da rodada anterior; o isolamento é por nome de arquivo e hash exato; nenhuma identidade de modelo é registrada; toda a cadeia (especialistas, revisor, líder, revisores dos PRs e este auditor) é da mesma família de fornecedor. (**F-04, F-05, F-06, F-13**)
5. **Quando um número de outra série, outra direção ou outra entidade substitui o original dentro de uma compressão.** O store de séries aceita a troca NBS↔RatingDog como "revisão"; o auditor de fidelidade do PR #215 deixa passar 8 de 11 defeitos novos (entidade, direção da surpresa, `%`→`pontos`, `1,106`→`1.106` milhão, série homônima, qualificador inventado) quando o auditor semântico é leniente; e `scenario_probability` aceita pontuação de LLM com `calibration_ref` textual. (**F-10, F-12, F-08**)

Nenhum achado foi classificado **Crítica**: em todos os casos reproduzidos resta rastro no log append-only (`hig-dossier`) ou no tombstone; a perda ocorre nas camadas de resumo, projeção e decisão. É exatamente onde o operador lê. Doze achados são **Alta**, onze **Média**, dois **Baixa**; 17 confirmados por reprodução e 8 por inspeção documental.

## 2. Casos obrigatórios

- **PMIs (M2).** Valores recuperados das fontes: NBS 50,3% (abr) e 50,0% (mai), publicados 2026-04-30 e 2026-05-31 às 09:30 de Pequim; RatingDog 52,2 (abr) e 51,8 (mai), por fontes secundárias datadas porque a S&P Global bloqueou o fetcher (403). O consenso de maio é **51,6 (Reuters) ou 51,4 (provedor não nomeado)**: a surpresa é +0,2 ou +0,4 e a variação mensal é −0,4. O exemplo da issue #194 só vale para um dos provedores. A fixture **não é cega** (sem controlador). (**F-10, F-11, F-19**; `missions/M2-series-audit.md`)
- **Frigoríficos (M3).** O evento de 20–21/05/2026 (JBS Pontes e Lacerda SIF 51, PrimaFoods Araguari SIF 177, Vale Grande/Frialto Matupá SIF 4490; acetato de medroxiprogesterona) tem um **homônimo**: a nota oficial do MAPA hospedada sob `poder360.com.br/2026/05/` é a de **04/03/2025**, sobre outro trio e outro motivo, e as três plantas de 2025 foram reabilitadas um dia antes. Minerva (BEEF3) não é parte do evento. A cota (1,106 Mt, +55% acima) estava em 80% só em 21/07; a alegação "50% em maio" não foi verificada. Preços: **bloqueados**. O GCI atual devolve `no_match` e nenhuma identidade de evento ou decomposição causal existe. (**F-18**; `missions/M3-causality-audit.md`)

## 3. Riscos não confirmados (registrados, não demonstrados)

Síntese #208 (árbitro) só inspecionada; gate cumulativo IEC e checkpoints #213 não sondados; comportamento do auditor semântico real desconhecido (todos os benchmarks dos PRs usam stubs); integração PostgreSQL não exercitada (68–69 testes ignorados); estudos quantitativos e holdout só por inspeção de guardas.

## 4. Controles eficazes (manter)

Log encadeado detecta edição/remoção interna; `calibrated_probability` nulo na ficha; `as_of`/`post_event` na validação de entrega; chaves de ordem recusadas em todos os contratos; board recusa citação sem relação com a claim; CAS, idempotência estrita, tombstones e propagação `stale` no documento por seções; gate de fidelidade recalcula a decisão; `no_match`/`discovery_suggestion` em vez de hipótese automática; `abster`/`inconclusive`/`not_assessable` como saídas válidas; FedWatch recusado como consenso.

## 5. Menor conjunto de correções (detalhe em `final/remediation-plan.md`)

Lote 1 (sete mudanças pequenas na `main`): payload completo na reconciliação com `post_event`; resumo por template a partir das claims e `head` do log no handoff; snapshot do revisor em modo D1 puro; isolamento por conteúdo; conflito evidência×fatos; Radar expondo notas e rótulo de incompletude; `calibration_ref` resolvido. Lote 2 (antes de mesclar #206–#212): tabela explícita de fornecedor/família de modelo, autoridades autenticadas, identidade composta de série, validadores de entidade/direção/unidade no #211, herança de contrárias por similaridade e gate obrigatório no #212.

## 6. Cobertura e limites

50 requisitos congelados (25 P0; todos com resultado): 16 aprovados, 9 com ressalva, 16 falharam, 7 inexistentes, 2 inconclusivos (`final/coverage-report.md`). Dependências: mesmo fornecedor de modelo em toda a cadeia, inclusive este auditor; sem controlador independente para fixtures cegas; sem banco; três fontes bloqueadas. Nenhuma afirmação de confiabilidade absoluta ou cobertura completa.

## 7. Revisão independente

<!-- REVIEW_PLACEHOLDER -->
