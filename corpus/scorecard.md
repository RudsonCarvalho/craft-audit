# CRAFT Portfolio Scorecard
**Profile:** MS-1.1.1 · **Audit window:** 2026-08-19 · **Services audited:** 9 · **Repositories:** 5

---

## Executive summary

Nine services were audited across five repositories: two established microservice reference architectures (Spring PetClinic, Google's Online Boutique), one large academic benchmark (train-ticket, 1 of 47 services sampled), one single-pattern tutorial (spring-circuitbreaker-demo), and one purpose-built positive-control fixture (craft-golden-demo). CRAFT Score ranges from **0.00 to 10.00**, mean **2.00**. Eight of nine services land in **Insatisfatório (Unsatisfactory)**; one — the fixture deliberately engineered to demonstrate full conformance — reaches **Excelente (Excellent)**.

**The single most consequential cross-service pattern:** in every service where a health probe was found, it existed as *infrastructure* (an Actuator dependency, a gRPC health handler) without being *connected* to anything that acts on it — or, where connected, it was frequently backed by a check incapable of failing. This pattern repeats in 5 of the 8 Insatisfatório-tier services and is the highest-leverage fix across the portfolio: cheap per service, and the only finding that generalizes almost verbatim across every affected service.

## Benchmark legend

| CRAFT Score | Label | What it means |
|---|---|---|
| 8.0–10.0 | **Excelente** (Excellent) | High reliability and resilience; no additional-domain overhead |
| 5.0–7.9 | **Bom** (Good) | Reliable, but has single points of failure without fallback, or unprotected adjacent integrations |
| 3.0–4.9 | **Aceitável** (Acceptable) | Room for improvement; corrective measures required; low robustness |
| 0.0–2.9 | **Insatisfatório** (Unsatisfactory) | Requires revision; risks damage to adjacent services and the system as a whole |

## Tier distribution

```
Excelente      (Excellent)     █ 1
Bom            (Good)            0
Aceitável      (Acceptable)      0
Insatisfatório (Unsatisfactory) ████████ 8
```

## Scorecard

| Service | Repo | CRAFT Score | Classificação | D | Penalties | Unverified | Headline finding |
|---|---|---:|---|---:|---:|---:|---|
| customers-service | spring-petclinic | 0.00 | Insatisfatório | 1 | 0 | 2 | No protections on any vertical; DB config externalized out of boundary |
| visits-service | spring-petclinic | 0.00 | Insatisfatório | 1 | 0 | 2 | Same shape as customers-service |
| vets-service | spring-petclinic | 0.00 | Insatisfatório | 1 | 0 | 2 | Same shape; has an in-process cache the profile doesn't yet score |
| ts-preserve-service | train-ticket | 0.05 | Insatisfatório | 1 | 0 | 0 | 11 unprotected downstream calls on one shared, unconfigured HTTP client |
| api-gateway | spring-petclinic | 1.13 | Insatisfatório | 1 | 0 | 4 | Asymmetric protection — the higher-consequence call is the unprotected one |
| checkoutservice | microservices-demo | 1.72 | Insatisfatório | 1 | 1 | 0 | Liveness handler unconditionally returns SERVING — active anti-pattern, not just absence |
| circuitbreaker-demo | spring-circuitbreaker-demo | 2.17 | Insatisfatório | 1 | 0 | 0 | Textbook-perfect annotations wrapping a call with no real dependency — presence ≠ boundary |
| cartservice | microservices-demo | 2.97 | Insatisfatório | 1 | 0 | 2 | 0.03 below Acceptable; real health check, but zero DI replication/fallback |
| craft-golden-demo | craft-golden-demo | 10.00 | Excelente | 1 | 0 | 0 | Positive control — every vertical independently verified against source |

*(Sorted by CRAFT Score ascending — worst first.)*

## Cross-cutting capability findings

### 1. Health check machinery present, not connected or not real (5 of 8 Insatisfatório-tier services)
Affects: api-gateway, customers/visits/vets-service, checkoutservice, circuitbreaker-demo.
Two distinct sub-patterns, both closing at the same fix:
- **Unwired**: Actuator or equivalent health endpoint exists in the dependency tree; no `docker-compose` healthcheck or k8s probe references it (api-gateway, customers/visits/vets-service, circuitbreaker-demo).
- **Wired but hollow**: the probe is wired, but the handler behind it cannot fail — checkoutservice's gRPC health check unconditionally returns `SERVING` regardless of the six connections it depends on.

**Representative fix prompt (generalizes across the unwired cases):**
```
Add a healthcheck (docker-compose) or readiness/liveness probe (Kubernetes) pointing at this service's existing
health endpoint (Actuator /actuator/health, or the framework-equivalent). Do not introduce a new health-check
implementation if one already exists in the dependency tree — wire the existing one. Verify the check reflects
real downstream state (a database ping, a critical connection's status) rather than returning a static success;
if the current handler is unconditional, make it conditional on the actual dependency it claims to represent
before wiring it to the orchestrator.
```

### 2. Zero circuit breakers, zero retries, repo-wide (train-ticket, microservices-demo)
Confirmed by exhaustive grep across `src/`, not inferred from a sample: neither repository contains a single circuit breaker or retry mechanism anywhere in its business logic. Both are widely used as reference/teaching architectures. This is the strongest evidence in the corpus for the paper's opening claim — that structural resilience is not measured anywhere in the ordinary development lifecycle, and it shows even in flagship examples.

### 3. Fan-out without protection scales the exposure linearly (ts-preserve-service)
11 downstream calls sharing one unconfigured `RestTemplate` produced the lowest score in the corpus (0.05) without a single active anti-pattern — pure absence, multiplied by fan-out. This is a distinct risk shape from low cohesion (which the degradation factor targets): high fan-out inflates `Index_max` (more points to protect) while `Index` stays at zero, and the ratio does the rest. Worth a dedicated mention in the paper's methodology section — fan-out risk and cohesion risk are both real, are structurally different, and MS-1.1 already discriminates between them correctly.

## Per-tier detail

### Excelente (1 service)
`craft-golden-demo`. Purpose-built positive control; every mechanism across all six verticals independently verified against source, not accepted from the repository's own documentation. See its dedicated report for the full verification trail.

### Insatisfatório (8 services)
Four distinct root causes, not one uniform failure:
- **Pure absence** (customers/visits/vets-service, ts-preserve-service): no protections implemented; the DI boundary was in several cases externalized out of scope entirely.
- **Asymmetric coverage** (api-gateway): protection exists, but on the lower-consequence call.
- **Active anti-pattern** (checkoutservice): a real, wired mechanism that cannot do its job — worse than absence because it manufactures false confidence.
- **Protection without a boundary** (circuitbreaker-demo): excellent mechanism density around an operation with no real external dependency to protect.

## Methodology footnote

This scorecard reports **structural conformance** — what each service's construction demonstrably protects against, verified from source and configuration. It is not a measurement of observed production behavior, uptime, or incident history; see the CRAFT paper (§8, "What CRAFT does not measure") for the boundary of this claim. Profile MS-1.1.1, corrected during this audit window (CE/SE maxima; see `craft-golden-demo` report for the correction record). All JSON audits and per-service reports underlying this scorecard are included alongside it.
