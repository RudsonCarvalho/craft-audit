# Auditoria adversarial independente — GCI-ADV-2026-11-03-01

Somente leitura sobre `Craft-dreams/Global-Catalyst-Intelligence` e `Craft-dreams/knowledge-hub`. Nenhum repositório auditado foi alterado; nada foi mesclado; holdout não acessado; sem serviços pagos.

| Pasta | Conteúdo |
|---|---|
| `manifest/audit-manifest.json` | congelamento (SHAs, PRs, ambiente, executor, permissões, orçamento, fontes, changelog v1→v2) |
| `requirements/` | `requirements-matrix.v1.json` (congelada antes dos testes) e `requirements-matrix.json` (v2, com resultados) |
| `missions/` | `M1-inventory.md`, `M2-series-audit.md`, `M3-causality-audit.md`, `M4-quant-audit.md`, `M5-compression-audit.md`, `M6-document-audit.md`, `M7-reviewer-audit.md` |
| `findings/findings.json` | 25 achados com severidade, grau de confirmação, causa-raiz, evidências |
| `fixtures/` | fixtures adversariais sintéticas (M2, M5) e o script de traço de H07 |
| `evidence/` | saídas das sondas, fontes externas com data de recuperação e estado de acesso, PDF arquivado |
| `final/` | `executive-summary.md`, `coverage-report.md`, `findings-index.json`, `remediation-plan.md`, `independent-review.md` |

Como reproduzir as sondas: cada relatório de missão descreve o comando; os scripts usam os harnesses de teste dos próprios repositórios (`tests/test_fidelidade_211.py`, `tests/test_sectioned_doc_212.py`, `tests/iec_fixtures_206.py`) em worktrees dos SHAs congelados.
