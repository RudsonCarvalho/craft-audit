# Selo CRAFT Score — como usar no README

## Opção A — shields.io (zero manutenção, recomendada para começar)

```markdown
![CRAFT Score](https://img.shields.io/badge/CRAFT%20Score-10.0%20·%20Excelente-2ea44f)
```

Variantes por classificação (cores fixas por tier):

```markdown
![CRAFT Score](https://img.shields.io/badge/CRAFT%20Score-10.0%20·%20Excelente-2ea44f)   <!-- Excelente: verde -->
![CRAFT Score](https://img.shields.io/badge/CRAFT%20Score-6.5%20·%20Bom-blue)            <!-- Bom: azul -->
![CRAFT Score](https://img.shields.io/badge/CRAFT%20Score-4.2%20·%20Aceitável-yellow)    <!-- Aceitável: amarelo -->
![CRAFT Score](https://img.shields.io/badge/CRAFT%20Score-1.1%20·%20Insatisfatório-red)  <!-- Insatisfatório: vermelho -->
```

## Opção B — SVG próprio versionado no repo (sem dependência externa)

Commite `craft-score-badge.svg` em `/.github/` ou `/docs/` e referencie:

```markdown
![CRAFT Score](./.github/craft-score-badge.svg)
```

## Bloco sugerido para o topo do README do craft-golden-demo

```markdown
# CRAFT Golden Demo

![CRAFT Score](https://img.shields.io/badge/CRAFT%20Score-10.0%20·%20Excelente-2ea44f)
![Profile](https://img.shields.io/badge/profile-CRAFT%2FMS--1.1.1-555)
![Audited](https://img.shields.io/badge/audited-2026--08--19-555)

> Positive-control fixture for the [CRAFT](LINK-DO-REPO-CRAFT-AUDIT) structural resilience audit.
> Score independently verified at commit `c1cbfbc` — see [`audit.json`](./craft-audit/audit.json) for the full evidence ledger.
```

## Regra de integridade do selo (importante)

O selo só é honesto se for **rastreável à auditoria que o gerou**. Sempre acompanhe o selo de:
1. O **commit auditado** (o selo vale para aquele estado do código, não para o repo eternamente)
2. A **versão do perfil** (CRAFT/MS-1.1.1)
3. Link para o **audit.json** com o ledger de evidências

Um selo sem esses três vira exatamente o tipo de "conformidade de fachada" que o CRAFT existe para combater. Recomendação futura (fase produto): o selo ser gerado automaticamente pelo pipeline de auditoria contínua, atualizado a cada commit — aí ele deixa de ser uma declaração e vira uma medição viva.
