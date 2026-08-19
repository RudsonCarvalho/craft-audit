# CRAFT Audit — resilience-golden-demo
**Repo:** RudsonCarvalho/resilience-golden-demo
**Commit:** c1cbfbcfdf3c8e503387807792af522ab42e7681
**Profile:** MS-1.1.1 · **Date:** 2026-08-19

## CRAFT Score = 10.0 — Excellent. First non-Unsatisfactory result in the corpus.

## Methodology note, read first

This repository ships its own evidence map (`CRAFT-MAP.md`) and its README explicitly warns any auditor: *"the map is documentation, not scoring evidence... nothing should be scored merely because it is mentioned here."* That instruction was followed literally. Every mechanism below was located and read in source or configuration **before** the map's claimed value was consulted, then cross-checked. Nothing in this audit was taken on the map's word.

One real defect surfaced during this process — not in the fixture, but in the auditor's own MS-1.1 profile:

**The profile's declared CE and SE maxima were arithmetically wrong.** `profile.md` stated CE max = 15 and SE max = 21. The literal sum of each vertical's own weight table — circuit breaker (3) + fallback (5) + retry band (2) + global-retry-budget bonus (+1) + timeout (4) + pool (2) — is 17 for CE, and 23 for SE once idempotent write (+4), compression (+1), and async dispatch (+1) are added. This repository's README caught and stated this inconsistency explicitly, rather than silently working around it, and predicted correctly that either resolution path (literal sum with a clamp, or capping each vertical at its stated max) converges on the same result. **The profile has been corrected to MS-1.1.1** (CE 15→17, SE 21→23) as a direct consequence of this audit. This is a genuine case of an external test fixture catching a bug in the measurement instrument itself — which is exactly what a positive-control fixture is for.

## What was independently verified, vertical by vertical

| Vertical | Score | Max | Key evidence |
|---|---|---|---|
| EE | 5 | 5 | `@Bulkhead(type=SEMAPHORE, maxConcurrentCalls=32)` on the sole endpoint |
| CE | 17 | 17 | Real GET, circuit breaker (window 10/min 5/threshold 50%), local fallback, exponential+jitter+capped retry gated by a real shared token bucket, explicit 200/700/150ms timeouts, pooled client (32/16) |
| SE | 23 | 23 | Real PUT with `Idempotency-Key` header, gzip via `GZIPOutputStream`, async dispatch on a named bounded executor, same CB/fallback/retry/timeout/pool rigor as CE |
| DI | 14 | 14 | Real Redis master + replica + 3 Sentinels (`compose.yaml`), explicit connect/command timeouts, Lettuce pool, **a hand-written try/catch fallback with no annotation at all** — see note below |
| AC | 18 | 18 | Three distinct, *real* (non-static) health indicators wired to k8s probes; `restartPolicy: Always`; two-layer graceful shutdown (app-level + `preStop`); resource requests/limits; `PodDisruptionBudget` |
| SE-KAFKA | 17 | 17 | Real Avro schema enforced by `GenericDatumWriter`; bounded failure buffer (max 100, ring eviction, never republishes); rate limiter (50/s); `acks=all` + `enable.idempotence=true` |
| **Total** | **94** | **94** | |

**Penalties: 0.** Explicitly checked and cleared, not merely absent by omission: no timeout inversion (one shared timeout config, nothing shorter wraps it), no unconditional liveness (the liveness check inspects real executor state and can fail), no circular fallback (all three fallbacks — catalog, webhook, Redis — return local values and never re-target the failed dependency), no inert circuit breaker (realistic threshold/window), no retry without backoff or cap, no retry over a non-idempotent write, no pool without a timeout.

**D = 1**, confirmed by inspection: exactly one `@PostMapping` exists in the entire codebase.

$$\text{CRAFT Score} = \frac{94 - 0}{94 - 0} \times 10 = 10.0$$

No clamp was even needed once the profile arithmetic was corrected — the implemented sum lands exactly on the corrected maximum.

## A finding worth keeping: the DI fallback would defeat a naive scanner

`ResilientOrderStateStore`'s Redis fallback is **not** a `@CircuitBreaker`/`@Retry` annotation. It's a hand-written `try/catch` around each Redis call, falling back to a local `ConcurrentHashMap`, with the catch block deliberately never touching Redis again. An auditor that only greps for annotation names would score this point 0 — the protection is real, but it's expressed as ordinary control flow, not a decorator. This is the same class of finding as Section 5.1's core argument: presence-scanning misses protection that a semantic reader catches, and this repository happens to contain a clean, real-world instance of it in its own most rigorously verified state.

## Why this result matters for the corpus

This is the ninth service audited and the first to leave the Unsatisfactory tier — every other result so far (PetClinic, Online Boutique, train-ticket, spring-circuitbreaker-demo) landed between 0.0 and 2.97. That raised a fair methodological question earlier in this work: can CRAFT ever say a service is well-built, or does it only produce pessimism? This result answers it. The instrument reaches its ceiling when the evidence genuinely earns it, verified independently rather than asserted, and it reaches exactly the ceiling this repository was deliberately engineered to demonstrate — no more, no less.

This repository is the correct positive control for the paper's validation section: unlike a purely synthetic minimal example, it exercises all six verticals against a real, running stack (Spring Boot, Redis Sentinel, Kafka, Avro, WireMock-based failure injection, Kubernetes manifests, CI), and its own README predicted the exact CRAFT Score/tier/penalty outcome this audit reached independently.

## Data quality

- 0 unverified items — every mechanism resolved to a concrete configured value with file:line evidence
- 0 set-aside items — nothing found outside the current profile's vocabulary
- Indirect-protection sweep run and returned clean: no hidden AOP, no undisclosed internal library, no service mesh
- 1 defect found and fixed in the auditor's own instrument (profile.md CE/SE maxima) as a direct result of this audit
