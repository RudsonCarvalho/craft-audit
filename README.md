# CRAFT — Conformance-based Resilience Assessment of Fault Tolerance

**Análise de qualidade da construção de microsserviços, com foco em resiliência.**  
*Build-quality analysis for microservices, focused on resilience.*

CRAFT evaluates a service's resilience **as built**: the presence and calibration of protection mechanisms at its functional boundary. It produces a 0–10 resilience score, a four-tier classification, a per-item evidence ledger, and an ordered remediation plan with ready-to-execute fix prompts.

It is not observability, chaos engineering, or SLO measurement. Those approaches evaluate behavior or outcomes. CRAFT asks a different question: **where is this service structurally fragile, and how can that be proven from the artifact before the incident?**

## Install the agent skill

The canonical runtime skill lives here:

[`skills/craft-audit/`](skills/craft-audit/)

```text
skills/craft-audit/
├── SKILL.md
└── references/
    ├── profile.md
    └── output-schema.md
```

> **Do not copy `SKILL.md` alone.** The three files above are one execution unit. `SKILL.md` loads the scoring profile and output contract through relative paths, so the `references/` directory must travel with it.

### What each file does

| File | Responsibility |
|---|---|
| [`SKILL.md`](skills/craft-audit/SKILL.md) | Agent audit procedure and evidence-resolution workflow |
| [`profile.md`](skills/craft-audit/references/profile.md) | Normative `CRAFT/MS-1.1.1` scoring model: weights, conditionals, maxima and penalties |
| [`output-schema.md`](skills/craft-audit/references/output-schema.md) | Machine-readable audit/output contract |

### Option A — install from source

Copy the **entire** `skills/craft-audit/` directory into the skill search path used by your agent runtime. Installation paths vary by runtime; the portable contract is the directory structure above.

### Option B — build the packaged `.skill`

```bash
python3 scripts/package_skill.py
```

The command generates:

```text
dist/craft-audit.skill
```

The package is ZIP-compatible and contains:

```text
craft-audit/
├── SKILL.md
└── references/
    ├── profile.md
    └── output-schema.md
```

This makes the source directory and the packaged distribution equivalent: the package is generated from the canonical files, not maintained separately.

## Run an audit

Point a CRAFT-capable agent at a repository and ask:

```text
Run the CRAFT structural resilience audit on this repository.
```

or, when the repository is local to the agent:

```text
Run the CRAFT structural resilience audit on ./my-service.
```

The agent inventories independently deployable services and their interaction points, resolves each resilience mechanism to its **effective configured value**, checks anti-patterns, computes the score, and emits evidence-backed output.

**Core rule — provenance or reject:** no evidence, no score. A mechanism whose effective value cannot be resolved from code/configuration is scored zero and recorded as `UNVERIFIED`; it is never credited from an assumption.

## How the skill executes

```text
Target repository
      │
      ▼
craft-audit/SKILL.md
      │
      ├── references/profile.md
      │      scoring rules and penalties
      │
      └── references/output-schema.md
             output contract
      │
      ▼
<repo-name>-craft/
      ├── <service>-audit.json
      ├── <service>-report.md
      ├── summary.csv
      └── scorecard.md       # multi-service / corpus audits
```

The skill is intentionally evidence-first: the profile defines **what counts**, while the procedure defines **how the agent must prove it**.

## Repository structure

```text
.
├── README.md
├── LICENSE
├── skills/
│   └── craft-audit/              # canonical executable skill
│       ├── SKILL.md
│       └── references/
│           ├── profile.md
│           └── output-schema.md
├── scripts/
│   └── package_skill.py          # builds the portable .skill archive
├── dist/                         # generated distribution artifacts
├── docs/
│   ├── CRAFT-preprint-v0.9.pdf   # methodology paper
│   ├── craft-badge-howto.md      # score-badge integrity and usage
│   └── craft-score-badge.svg
└── corpus/                       # reproducible audit evidence
    ├── scorecard.md
    ├── corpus-summary.csv
    └── ...
```

The separation is deliberate:

- **`skills/`** is the executable product.
- **`docs/`** is human-facing methodology and supporting documentation.
- **`corpus/`** is the empirical/reproducibility layer.
- **`dist/`** is generated from `skills/`; it is not a second source of truth.

## Classification

| Resilience score | Classificação | Meaning |
|---|---|---|
| 8.0–10.0 | **Excelente** | High reliability and resilience |
| 5.0–7.9 | **Bom** | Reliable, but with meaningful structural gaps |
| 3.0–4.9 | **Aceitável** | Corrective measures required; low robustness |
| 0.0–2.9 | **Insatisfatório** | Requires revision; significant structural risk |

## Published corpus

The repository includes audited services from public projects, with evidence tied to recorded commits. The portfolio view lives in [`corpus/scorecard.md`](corpus/scorecard.md).

| Service | Repository | Score | Classificação |
|---|---|---:|---|
| customers/visits/vets-service | spring-petclinic | 0.00 | Insatisfatório |
| ts-preserve-service | train-ticket | 0.05 | Insatisfatório |
| api-gateway | spring-petclinic | 1.13 | Insatisfatório |
| checkoutservice | microservices-demo | 1.72 | Insatisfatório |
| circuitbreaker-demo | spring-circuitbreaker-demo | 2.17 | Insatisfatório |
| cartservice | microservices-demo | 2.97 | Insatisfatório |
| resilience-golden-demo | resilience-golden-demo | 10.00 | Excelente |

## Positive control

[**resilience-golden-demo**](https://github.com/RudsonCarvalho/resilience-golden-demo) is the positive-control fixture: a small runnable Spring Boot service designed to expose every profile vertical against real network dependencies and deployment configuration.

Its complete evidence ledger is versioned in [`corpus/resilience-golden-demo/audit.json`](corpus/resilience-golden-demo/audit.json).

## Paper and methodology

The current preprint is [`docs/CRAFT-preprint-v0.9.pdf`](docs/CRAFT-preprint-v0.9.pdf).

The normative scoring rules used by the agent are not hidden in the paper: they are versioned directly in [`skills/craft-audit/references/profile.md`](skills/craft-audit/references/profile.md). This keeps the executable evaluator and the published methodology independently inspectable.

## CRAFT badge

Repositories may display a score badge, but the badge should always remain traceable to:

1. the audited commit;
2. the profile version;
3. the corresponding `audit.json` evidence ledger.

See [`docs/craft-badge-howto.md`](docs/craft-badge-howto.md) for the recommended badge formats and integrity rule.

## Versioning and integrity

The active reference profile is **CRAFT/MS-1.1.1**.

When the scoring profile changes, the profile file is the normative source and generated audit artifacts should record the exact profile version used. A score describes a specific repository state under a specific profile; it is not a timeless certification of the repository.

## Status

Preprint v0.9. The repository includes the executable audit procedure, the versioned scoring profile, the output contract, a positive control, and a public audit corpus. Open validation work described in the paper remains part of the research roadmap.

## Citation

```bibtex
@misc{carvalho2026craft,
  author = {Carvalho, Rudson Kiyoshi Souza},
  title  = {{CRAFT}: A Structural Conformance Index for System Resilience,
            and the Evaluator That Did Not Exist},
  year   = {2026},
  note   = {Preprint v0.9},
  url    = {https://github.com/RudsonCarvalho/craft-audit}
}
```

## License

Apache-2.0
