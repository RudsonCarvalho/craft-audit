# CRAFT — Conformance-based Resilience Assessment of Fault Tolerance

**Análise de qualidade da construção de microsserviços, com foco em resiliência.**  
*Build-quality analysis for microservices, focused on resilience.*

CRAFT scores a service's resilience **as built** — the presence and calibration of protection mechanisms at its functional boundary — rather than as observed in production. It produces a 0–10 **Nota de Resiliência** (CRAFT Score), a four-tier classification, a per-item evidence ledger, and an ordered remediation plan with ready-to-execute fix prompts.

> **Looking for the agent skill? Use [`skills/craft-audit/`](skills/craft-audit/).**  
> That directory is the complete portable skill. Copy it as a unit; `SKILL.md` depends on both files under its local `references/` directory.

## Repository structure

```text
craft-audit/
│
├── README.md
├── LICENSE
│
├── skills/
│   └── craft-audit/
│       ├── SKILL.md
│       └── references/
│           ├── profile.md
│           └── output-schema.md
│
├── docs/
│   ├── CRAFT-preprint-v0.9.pdf
│   ├── craft-badge-howto.md
│   └── craft-score-badge.svg
│
└── corpus/
    ├── scorecard.md
    └── ...
```

The separation is intentional:

- **`skills/craft-audit/`** is the reusable agent skill.
- **`docs/`** contains human-facing methodology and presentation material.
- **`corpus/`** contains published audit evidence and benchmark data.
- **`README.md`** explains how the pieces fit together.

A future packaged distribution may live under `dist/`, but no generated package is committed today. The source of truth is the directory under `skills/`.

## Use CRAFT as an agent skill

### Canonical skill package

The smallest portable CRAFT unit is this directory:

```text
skills/craft-audit/
├── SKILL.md
└── references/
    ├── profile.md
    └── output-schema.md
```

The three files have different responsibilities and should always be versioned and copied together:

| File | Role | When the agent must read it |
|---|---|---|
| [`skills/craft-audit/SKILL.md`](skills/craft-audit/SKILL.md) | **Audit procedure** — trigger, repository inventory, boundary discovery, evidence resolution, anti-pattern checks, scoring workflow, findings and output steps | First; this is the entry point |
| [`skills/craft-audit/references/profile.md`](skills/craft-audit/references/profile.md) | **Scoring policy** — CRAFT/MS-1.1.1 weights, maxima, conditional rules, penalties, normalization and classification | Before assigning any score |
| [`skills/craft-audit/references/output-schema.md`](skills/craft-audit/references/output-schema.md) | **Output contract** — JSON fields, evidence ledger shape, findings/remediation structure and CSV schemas | Before writing audit artifacts |

Inside the skill directory the dependency remains intentionally relative:

```text
SKILL.md
├── requires before scoring ──> references/profile.md
└── requires before output  ──> references/output-schema.md
```

**Do not copy `SKILL.md` alone.** Preserve the directory layout so those relative references remain valid in any agent, repository, or harness.

### Copy the skill into another environment

The destination directory is agent/harness-specific. Copy the whole skill directory rather than selecting files individually:

```bash
git clone --depth 1 https://github.com/RudsonCarvalho/craft-audit.git

cp -R craft-audit/skills/craft-audit <agent-skill-dir>/craft-audit
```

After the copy, the destination should still look like:

```text
<agent-skill-dir>/craft-audit/
├── SKILL.md
└── references/
    ├── profile.md
    └── output-schema.md
```

If an agent can read this GitHub repository directly, point it to [`skills/craft-audit/SKILL.md`](skills/craft-audit/SKILL.md); the required references are available beside it at their expected relative paths.

### Run without native skill support

CRAFT does not require a proprietary skill loader. A generic coding agent can be given the contract explicitly:

```text
Use skills/craft-audit/SKILL.md as the CRAFT audit procedure.
Before scoring, read skills/craft-audit/references/profile.md.
Before writing outputs, read skills/craft-audit/references/output-schema.md.
Run the audit against <repository-or-service-path>.
Do not award points without file/line evidence and a resolved configuration value.
```

A shorter invocation is enough when the skill is already installed:

```text
Run the CRAFT resilience audit on ./my-service
```

### Expected output

The skill creates `<repo-name>-craft/` and emits, per service:

```text
<service>-audit.json        machine-readable evidence ledger and score
<service>-report.md         human-readable findings and remediation plan
```

For multi-service/repository audits it also emits:

```text
summary.csv                 corpus-level summary
scorecard.md                portfolio view when 2+ services are audited
```

The exact machine-readable contract is defined by [`skills/craft-audit/references/output-schema.md`](skills/craft-audit/references/output-schema.md).

### Versioning rule

Treat `skills/craft-audit/` as one release unit:

- `SKILL.md` defines **how to audit**;
- `references/profile.md` defines **how to score**;
- `references/output-schema.md` defines **how to serialize the result**.

The `profile_version` emitted by an audit should match the profile actually loaded by the agent. The active reference profile in this repository is **CRAFT/MS-1.1.1**.

## Documentation

Human-facing material is intentionally separate from the executable skill:

- [`docs/CRAFT-preprint-v0.9.pdf`](docs/CRAFT-preprint-v0.9.pdf) — methodology paper.
- [`docs/craft-badge-howto.md`](docs/craft-badge-howto.md) — how to display a traceable CRAFT score badge.
- [`docs/craft-score-badge.svg`](docs/craft-score-badge.svg) — versioned badge asset.

None of these files is required to execute the audit skill.

## Why

CRAFT is not observability (it does not watch production), not chaos engineering (it does not inject failure), and not SLO measurement (it does not measure outcome). It asks a different question: **where is this service structurally fragile, and how would we know before the incident?**

Outcome metrics — MTBF, SLIs, chaos experiments, load tests — are conditioned on what the environment happened to exercise. A service that was never stressed and a service engineered to withstand stress can produce indistinguishable readings. CRAFT instead evaluates the construction of the artifact and the protections visible at its functional boundary.

## Audit principle

**Core rule — provenance or reject:** no evidence, no score. An item whose effective value cannot be resolved is scored zero and logged `UNVERIFIED`; the auditor must not credit an assumed framework default or a mechanism that merely appears likely to exist.

The workflow inventories services and interaction points, resolves each protection mechanism to its configured value, checks indirect/injected protection, applies anti-pattern penalties and the domain-coherence degradation factor, then normalizes the result to 0–10.

## Classification

| Nota de Resiliência | Classificação | Meaning |
|---|---|---|
| 8.0–10.0 | **Excelente** | High reliability and resilience |
| 5.0–7.9 | **Bom** | Reliable, but with meaningful structural gaps |
| 3.0–4.9 | **Aceitável** | Corrective measures required; low robustness |
| 0.0–2.9 | **Insatisfatório** | Requires revision; risks damage to adjacent services |

## Published corpus

The repository contains nine service audit entries across five public repositories. Every published score is tied to a recorded commit so the evidence can be re-derived.

| Service | Repository | Score | Classificação |
|---|---|---:|---|
| customers-service | spring-petclinic-microservices | 0.00 | Insatisfatório |
| visits-service | spring-petclinic-microservices | 0.00 | Insatisfatório |
| vets-service | spring-petclinic-microservices | 0.00 | Insatisfatório |
| ts-preserve-service | train-ticket | 0.05 | Insatisfatório |
| api-gateway | spring-petclinic-microservices | 1.13 | Insatisfatório |
| checkoutservice | microservices-demo | 1.72 | Insatisfatório |
| circuitbreaker-demo | spring-circuitbreaker-demo | 2.17 | Insatisfatório |
| cartservice | microservices-demo | 2.97 | Insatisfatório |
| resilience-golden-demo | resilience-golden-demo | 10.00 | Excelente |

See [`corpus/scorecard.md`](corpus/scorecard.md) for the portfolio view and the structurally distinct failure shapes found in the corpus.

## Positive control

[**resilience-golden-demo**](https://github.com/RudsonCarvalho/resilience-golden-demo) is the positive-control fixture: a microscopic Spring Boot service that deliberately exposes every mechanism needed by the active profile across HTTP entry, synchronous consultation, outbound integration, Redis, Kafka, and container/deployment configuration.

Its published audit is stored under [`corpus/resilience-golden-demo/`](corpus/resilience-golden-demo/). The positive control also exposed an arithmetic inconsistency in the previous profile maxima, which was corrected in **MS-1.1.1**.

## Status

Preprint v0.9. The most important open validation item is an agent-versus-human auditor agreement study; the corpus also cannot currently support a meaningful weight-sensitivity analysis because its score distribution is bimodal. Both limitations are stated in the [paper](docs/CRAFT-preprint-v0.9.pdf) rather than hidden.

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
