# M3 — Causalidade e mecanismos econômicos

Episódio obrigatório: suspensões de frigoríficos brasileiros pela China em maio de 2026 (issue #178 cita "BEEF3"). Fontes em `evidence/m3-sources/sources.json` (datas de recuperação 2026-11-03; itens bloqueados ou não verificados marcados). Código: `event_normalize.py`, `event_matcher.py`, `monitor.py` (main); nenhum componente de causalidade/exposição existe (#178 só issue). Sonda: `evidence/m3_matcher_probe.txt`.

## 1. Linha do tempo reconstruída (fatos datados, com fonte)

| Data | Fato | Fonte | Grau |
|---|---|---|---|
| 2025-03-04 | GACC suspende 3 plantas (JBS Mozarlândia-GO, Frisa Nanuque-MG, Bon-Mart Presidente Prudente-SP) após vídeo-auditorias; MAPA: 126 plantas habilitadas | SRC-M3-01 (nota oficial, texto lido) | primária |
| 2025-12-31 | MOFCOM confirma salvaguarda sobre carne bovina: 2026-01-01 a 2028-12-31; cota Brasil 2026 = 1,106 Mt; +55% acima da cota | SRC-M3-02, SRC-M3-03 | secundária datada |
| 2026-04-16 | China suspende Pantaneira/Frigosul (Várzea Grande-MT) por acetato de medroxiprogesterona | SRC-M3-04 | secundária (não aberta) |
| 2026-05-19 | MAPA anuncia retomada das 3 plantas suspensas desde mar/2025 | SRC-M3-05 | secundária datada |
| 2026-05-20 | GACC suspende (Ciferquery) JBS Pontes e Lacerda (SIF 51), PrimaFoods Araguari (SIF 177), Vale Grande/Frialto Matupá (SIF 4490) por acetato de medroxiprogesterona; MAPA notificado | SRC-M3-06 (21/05) | secundária datada |
| 2026-05-21 → 25 | Abiec: "temporária e preventiva"; Frialto: Brasil "se aproxima do limite da cota"; nenhuma menção a preços/tickers | SRC-M3-06, SRC-M3-07 | secundária |
| 2026-07-21 / 08-10 | cota em 80% / 90% (Mofcom) | SRC-M3-08 | secundária datada |
| "50% em maio; abates param 15/05–15/06" | **não verificado** (snippet sem página aberta; conflita com 80% só em 21/07) | SRC-M3-09 | não verificado |
| Cotações BEEF3/JBSS3/MBRF em mai/2026 | **bloqueado** (sem fonte licenciada no ambiente; COTAHIST 2026 do GCI reside no banco do operador) | SRC-M3-10 | bloqueado |

## 2. Decomposição exigida pelo protocolo

| Camada | O que as fontes sustentam | O que **não** sustentam |
|---|---|---|
| Ocorrência | Suspensão de 3 plantas específicas (SIF 51, 177, 4490) com vigência 20/05/2026 e motivo sanitário (resíduo hormonal) | horário exato da publicação GACC; o próprio aviso GACC não foi obtido |
| Exposição | JBS (uma planta entre dezenas habilitadas), PrimaFoods e Frialto (fechadas); Minerva (BEEF3) **não** é parte do evento; Minerva/MBRF têm plantas na Argentina/Uruguai com cotas próprias (SRC pesquisa) | fração da receita/volume de cada empresa afetada; exposição de Minerva é indireta (setor/sentimento), não documentada |
| Surpresa | precedente de abr/2026 (Pantaneira, mesmo resíduo) e reabilitação de outras 3 plantas em 19/05 tornam a suspensão parcialmente antecipável; Abiec a chamou de "preventiva" | nenhum consenso/expectativa mensurável existe para eventos sanitários; `surprise=null` é a única saída honesta |
| Reação | nenhum dado de preço verificado nesta auditoria | qualquer afirmação sobre "variação de BEEF3" fica **não confirmada** |
| Causas concorrentes datadas | salvaguarda vigente desde 01/01 com cota que se esgotaria (80% em 21/07); suspensão de abr/2026; reabilitação de 19/05; câmbio e ciclo pecuário (não medidos aqui) | ordenação de magnitude entre causas (sem preços, sem controles) |
| Atribuição | **não é possível**; qualquer frase do tipo "a notícia derrubou BEEF3" é `hipótese`/`não confirmado` | — |

## 3. Armadilha de homônimo de evento (achado F-18, Alta, inspeção documental)

O PDF "Esclarecimento sobre a suspensão de três plantas frigoríficas para a China — MAPA" hospedado em `static.poder360.com.br/2026/05/…` (sha256 `bcd7dc83…`, cópia em `evidence/m3-sources/`) tem rodapé de impressão **20/05/2026 15:13**, mas o corpo diz **"Publicado em 04/03/2025 18h12"**: é a nota de **março de 2025**, sobre **outro trio** (Mozarlândia, Nanuque, Presidente Prudente) e **outro motivo** (vídeo-auditoria). Um agente que use esse PDF como "fonte primária" do evento de maio de 2026 atribui plantas, empresas e causa errados, com um documento oficial autêntico à mão. O mesmo título ("três plantas") descreve dois eventos distintos separados por 14 meses, e as três plantas de 2025 foram **reabilitadas um dia antes** da nova suspensão.

## 4. Como o GCI atual trata o caso (sonda reproduzível)

| Entrada | `normalize_event` + `match_event` (21 fichas) | `group_events` |
|---|---|---|
| notícia de 2026-05-21 | `no_match` ("nenhuma ficha com sinal estruturado e lexical suficiente"); `discovery_suggestion` com setores/entidades **vazios** (JBS/PrimaFoods/Frialto não estão no índice) | — |
| nota MAPA 2025 | idem | não agrupada com 2026 (similaridade 0,17; janela 3 dias) |
| nota MAPA 2025 **datada erroneamente** 2026-05-20 | idem | não agrupada (textos diferentes) — mas também **não sinalizada**: nada compara o conteúdo (plantas/SIF/motivo) com outras notícias do mesmo dia |
| republicação idêntica 4 dias depois (origem distinta) | — | **não** agrupada: a janela padrão de `group_events` é de 3 dias (e a similaridade exigida, 0,85); republicações tardias viram eventos novos |
| mesmo evento parafraseado no mesmo dia | — | **não** agrupada (Jaccard abaixo de 0,85): dois "eventos" para um fato |

Conclusão: o GCI não possui (a) identidade de evento por atores/SIF/datas, (b) registro de causas concorrentes, (c) separação ocorrência/exposição/surpresa/reação/atribuição além do campo `materiality` do monitor (relevância). O `hig-impact/1` do monitor é explicitamente "relevância, não causalidade" — honesto, mas nada impede que um especialista escreva "a suspensão explica a queda" numa claim `inference` que a reconciliação aceita (M5/M7). A issue #178 descreve exatamente os controles que faltam; nada dela existe em código.

## 5. Resultados por requisito (v2)

REQ-039 **inexistente**; REQ-040 **falhou** (sem decomposição; homônimo não detectável); REQ-017/018 aprovados por inspeção (o que existe é relevância e dedupe por origem/similaridade). Limitações: preços bloqueados; GACC não consultada; três fontes 403; uma alegação (50% da cota em maio) não verificada e registrada como tal.


## 6. Errata (v2, após revisão independente)

- §3 e SRC-M3-01: o PDF do MAPA (04/03/2025) **não nomeia** as três plantas de 2025; os nomes (JBS Mozarlândia, Frisa Nanuque, Bon-Mart Presidente Prudente) vêm do Poder360 de 20/05/2026 (SRC-M3-05). `evidence/m3-sources/sources.json` foi corrigido.
- F-18 rebaixado para **Média**: o impacto descrito ("um resumidor que cite o PDF…") é hipotético, pois nenhuma ficha, entrega ou dossiê do GCI trata o caso; é lacuna de capacidade (mesma classe de F-17), não perda demonstrada.
