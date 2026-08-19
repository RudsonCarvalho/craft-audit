# CRAFT — Conformance-based Resilience Assessment of Fault Tolerance

**Análise de qualidade da construção de microsserviços, com foco em resiliência.**
*Build-quality analysis for microservices, focused on resilience.*

CRAFT scores a service's resilience **as built** — the presence and calibration of protection mechanisms at its functional boundary — rather than as observed in production. It produces a 0–10 **CRAFT Score** with a four-tier classification, a per-item evidence ledger, and an ordered remediation plan with ready-to-execute fix prompts.

It is not observability (it does not watch production), not chaos engineering (it does not inject failure), and not SLO measurement (it does not measure outcome). It answers a question none of those answer: **where is this service structurally fragile, and how would we know before the incident?**

## Why

Outcome metrics — MTBF, SLIs, chaos experiments, load tests — are all conditioned on what the environment happened to exercise. A service that was never stressed and a service engineered to withstand stress produce indistinguishable readings. Aviation (DO-178C), automotive (ISO 26262), and medical devices (IEC 62304) resolved this decades ago by assessing *how the artifact was built*. CRAFT brings that discipline to distributed systems.

## What's here

```
SKILL.md                    the audit procedure (9 steps) — usable as an agent skill
references/profile.md       reference profile CRAFT/MS-1.1.1 — weights, penalties, conditionals
references/output-schema.md JSON output schema
corpus/                     9 audited services across 5 public repositories
CRAFT-preprint-v0.9.pdf     the paper
craft-badge-howto.md        how to display a CRAFT Score badge
```

## Running an audit

Point a CRAFT-capable agent at a repository:

```
run the CRAFT resilience audit on ./my-service
```

The agent inventories services and interaction points, resolves each protection mechanism to its *configured value* (not merely its presence), applies anti-pattern penalties and the domain-coherence degradation factor, and emits scored output with file-and-line evidence for every claim.

**Core rule — provenance or reject:** no evidence, no score. An item whose effective value cannot be resolved in-repo is scored zero and logged `UNVERIFIED`, never credited from an assumed framework default.

## Classification

| CRAFT Score | Classificação | Meaning |
|---|---|---|
| 8.0–10.0 | **Excelente** | High reliability and resilience |
| 5.0–7.9 | **Bom** | Reliable, but single points of failure without fallback |
| 3.0–4.9 | **Aceitável** | Corrective measures required; low robustness |
| 0.0–2.9 | **Insatisfatório** | Requires revision; risks damage to adjacent services |

## Published corpus

Nine services across five public repositories, every score re-derivable from the recorded commit:

| Service | Repository | Score | Classificação |
|---|---|---:|---|
| customers/visits/vets-service | spring-petclinic | 0.00 | Insatisfatório |
| ts-preserve-service | train-ticket | 0.05 | Insatisfatório |
| api-gateway | spring-petclinic | 1.13 | Insatisfatório |
| checkoutservice | microservices-demo | 1.72 | Insatisfatório |
| circuitbreaker-demo | spring-circuitbreaker-demo | 2.17 | Insatisfatório |
| cartservice | microservices-demo | 2.97 | Insatisfatório |
| resilience-golden-demo | resilience-golden-demo | 10.00 | Excelente |

See [`corpus/scorecard.md`](corpus/scorecard.md) for the portfolio view and the four structurally distinct failure shapes found.

## Positive control

[**resilience-golden-demo**](https://github.com/RudsonCarvalho/resilience-golden-demo) — a fixture implementing every mechanism in the profile against a real running stack (Spring Boot, Redis Sentinel, Kafka, Avro, Kubernetes, CI). It scores 10.0, and it caught an arithmetic defect in this profile's declared maxima during its own audit — corrected in MS-1.1.1.

## Status

Preprint v0.9. The most important open validation item is an agent-versus-human auditor agreement study; the corpus also cannot currently support a meaningful weight-sensitivity analysis because its score distribution is bimodal. Both are stated in the paper (§9) rather than glossed.

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
