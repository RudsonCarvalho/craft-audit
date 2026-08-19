# CRAFT Reference Profile MS-1.1.1

Weight semantics (anchor): 5 = preserves function under total dependency failure; 4 = prevents shared-resource exhaustion; 3 = limits blast radius; 2 = accelerates recovery; 1 = marginal; 0 = null; negative = anti-pattern (worse than absence).

Conditional notation: `w [req: X, else w′]` — score w only if prerequisite X is present and verified on the same interaction point; otherwise score w′.

## EE — External Entry (max 5)

| Weight | Protection |
|---|---|
| 0 | None |
| 3 | Rate limiter — mutually exclusive with bulkhead |
| 5 | Bulkhead — mutually exclusive with rate limiter |

## SE — External Exit (max 23 per point)

| Weight | Protection |
|---|---|
| 3 | Circuit breaker [req: timeout, else 1] |
| 5 | Fallback [req: timeout or circuit breaker, else 2] |
| 0–2 | Retry band: none 0 · fixed backoff + attempt cap 1 · exponential backoff + jitter + cap 2 · +1 if global retry budget/token bucket |
| 4 | Timeout (resolved value must be recorded) |
| 2 | Connection pool |
| 4 | Idempotent write (idempotency key, or operation naturally idempotent) |
| 1 | Data compression |
| 1 | Asynchronous dispatch |

## CE — External Consultation (max 17 per point)

| Weight | Protection |
|---|---|
| 3 | Circuit breaker [req: timeout, else 1] |
| 5 | Fallback [req: timeout or circuit breaker, else 2] |
| 0–2 | Retry band (as SE) |
| 4 | Timeout |
| 2 | Connection pool |

## DI — Internal Data (max 14 per point)

| Weight | Protection |
|---|---|
| 5 | Replication (verified in the data store config this repo controls) |
| 3 | Fallback |
| 4 | Timeout |
| 2 | Connection pool |

## AC — Application Container (max 18; one instance per service)

| Weight | Protection |
|---|---|
| 3 | Specific readiness probe (real dependency/readiness check) |
| 3 | Specific liveness probe (real health logic) |
| 3 | Self-healing configured [req: specific liveness probe, else 0] |
| 4 | Graceful shutdown — SIGTERM handling with connection draining |
| 2 | Declared resource limits (CPU/memory request AND limit) |
| 2 | Startup probe distinct from liveness |
| 1 | Declared disruption policy (e.g., PodDisruptionBudget) |

## SE-KAFKA — Producer-type async exit (max 17 per point; use instead of SE for queue producers)

| Weight | Protection |
|---|---|
| 3 | Schema validation |
| 5 | Error handling (DLQ/dead-letter or explicit failure path) |
| 1 | Throttling |
| 4 | Producer idempotence |
| 2 | Bounded batch size (explicitly configured) |
| 1 | acks=1 — mutually exclusive with acks=all |
| 2 | acks=all — mutually exclusive with acks=1 |

## Penalties (apply wherever detected; sum into Index and into Index_min)

| Penalty | Anti-pattern | Detection |
|---|---|---|
| −3 | Timeout inversion | This call's resolved timeout > its in-repo caller's timeout |
| −3 | Unconditional liveness | Probe endpoint returns success with no real check |
| −2 | Circular fallback | Fallback targets the same dependency or one sharing its backend |
| −2 | Inert circuit breaker | Threshold/window values make tripping implausible under realistic traffic |
| −2 | Retry without backoff or without attempt cap | Config fields |
| −2 | Retry over non-idempotent write | Retry policy wraps POST/non-idempotent op without idempotency key |
| −1 | Pool without timeout | Pool present, pooled calls have no timeout |

## Changelog

- **v1.1.1** (found via independent audit of `RudsonCarvalho/resilience-golden-demo`, a purpose-built positive-control fixture): corrected CE declared max 15→17 and SE declared max 21→23. The stated maxima did not match the literal sum of each vertical's own weight table once the +1 global-retry-budget modifier is included (circuit breaker 3 + fallback 5 + retry band 2 + retry bonus 1 + timeout 4 + pool 2 = 17 for CE; +4 idempotent write +1 compression +1 async = 23 for SE). This was an arithmetic bug in the profile, not a scoring rule change — no weights were altered, only the declared ceiling was corrected to match them.

## Scoring rules

1. Score each interaction point independently, then sum per vertical.
2. Mutual exclusions: if both present, score only the higher.
3. Conditionals: prerequisite must be evidenced on the same point.
4. Bands: resolve the configured value first; no value ⇒ lowest band, log `UNVERIFIED`.
5. Penalties are additive and independent of positive scores on the same point.
6. Index_min for the topology = sum of penalties applicable to that topology's shape (a topology with retries present can carry retry penalties; one without retries cannot).
7. Mechanisms found that the profile does not list: score 0, log as `SET_ASIDE` with description — this measures profile coverage; report the set-aside count.
