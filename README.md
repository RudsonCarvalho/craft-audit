# CRAFT — Conformance-based Resilience Assessment of Fault Tolerance

**Análise de qualidade da construção de microsserviços, com foco em resiliência.**  
*Build-quality analysis for microservices, focused on resilience.*

CRAFT scores a service's resilience **as built** — the presence and calibration of protection mechanisms at its functional boundary — rather than as observed in production. It produces a 0–10 **Nota de Resiliência** (CRAFT Score), a four-tier classification, a per-item evidence ledger, and an ordered remediation plan with ready-to-execute fix prompts.

> **Looking for the agent skill? Start with [`SKILL.md`](SKILL.md).**  
> The executable skill is a **three-file package**: `SKILL.md` plus the two files under `references/`. Copying `SKILL.md` alone is incomplete.

## Use CRAFT as an agent skill

### Canonical skill package

The smallest portable CRAFT unit is exactly this structure:

```text
craft-audit/
├── SKILL.md
└── references/
    ├── profile.md
    └── output-schema.md
```

The three files have different responsibilities and should be versioned together:

| File | Role | When the agent must read it |
|---|---|---|
| [`SKILL.md`](SKILL.md) | **Audit procedure** — trigger, repository inventory, boundary discovery, evidence resolution, anti-pattern checks, scoring workflow, findings and output steps | First; this is the entry point |
| [`references/profile.md`](references/profile.md) | **Scoring policy** — CRAFT/MS-1.1.1 weights, maxima, conditional rules, penalties, normalization and classification | Before assigning any score |
| [`references/output-schema.md`](references/output-schema.md) | **Output contract** — JSON fields, evidence ledger shape, findings/remediation structure and CSV schemas | Before writing audit artifacts |

The dependency is intentionally explicit:

```text
SKILL.md
├── requires before scoring ──> references/profile.md
└── requires before output  ──> references/output-schema.md
```

**Do not detach these files from one another.** The paths in `SKILL.md` are relative, so when the skill is copied into another agent, repository, or harness, preserve the `references/` directory beside it.

### What is optional

Everything else in this repository supports research, validation, or presentation, but is **not required to run the skill**:

```text
corpus/                     published audit evidence and benchmark data
CRAFT-preprint-v0.9.pdf     methodology paper
craft-badge-howto.md        score-badge usage
craft-score-badge.svg       badge asset
```

This distinction matters when embedding CRAFT elsewhere: the runtime package is three Markdown files; the corpus and paper do not need to travel with it.

### Copy the skill into another environment

The destination directory is agent/harness-specific. Whatever directory your agent uses for skills, copy the CRAFT package while preserving the relative layout:

```bash
git clone --depth 1 https://github.com/RudsonCarvalho/craft-audit.git

mkdir -p <agent-skill-dir>/craft-audit/references
cp craft-audit/SKILL.md <agent-skill-dir>/craft-audit/SKILL.md
cp craft-audit/references/profile.md <agent-skill-dir>/craft-audit/references/profile.md
cp craft-audit/references/output-schema.md <agent-skill-dir>/craft-audit/references/output-schema.md
```

If your agent can read a GitHub repository directly, no installation convention is required: point it to `SKILL.md` and make the two referenced files available at their relative paths.

### Run without native skill support

CRAFT does not require a proprietary skill loader. A generic coding agent can be given the contract explicitly:

```text
Use SKILL.md as the CRAFT audit procedure.
Before scoring, read references/profile.md.
Before writing outputs, read references/output-schema.md.
Run the audit against <repository-or-service-path>.
Do not award points without file/line evidence and a resolved configuration value.
```

A shorter invocation is enough when the agent already has the skill installed:

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

The exact machine-readable contract is defined by [`references/output-schema.md`](references/output-schema.md), not by examples in the README.

### Versioning rule

Treat the three-file skill package as one release unit:

- `SKILL.md` defines **how to audit**;
- `references/profile.md` defines **how to score**;
- `references/output-schema.md` defines **how to serialize the result**.

The `profile_version` emitted by an audit should match the profile actually loaded by the agent. The active reference profile in this repository is **CRAFT/MS-1.1.1**.

## Repository map

```text
.
├── SKILL.md                    portable skill entry point
├── references/
│   ├── profile.md              CRAFT/MS-1.1.1 scoring profile
│   └── output-schema.md        machine-readable output contract
├── corpus/                     published audit corpus and scorecard
├── CRAFT-preprint-v0.9.pdf     paper
├── craft-badge-howto.md        badge documentation
├── craft-score-badge.svg       badge asset
└── LICENSE
```

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

Preprint v0.9. The most important open validation item is an agent-versus-human auditor agreement study; the corpus also cannot currently support a meaningful weight-sensitivity analysis because its score distribution is bimodal. Both limitations are stated in the paper rather than hidden.

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
