# CRAFT Audit — api-gateway
**Repo:** spring-petclinic/spring-petclinic-microservices
**Commit:** 305a1f13e4f961001d4e6cb50a9db51dc3fc5967
**Profile:** MS-1.1 · **Date:** 2026-08-19

## Score

| Vertical | Score | Max |
|---|---|---|
| EE (client entry) | 0 | 5 |
| CE-1 (→ customers-service) | 0 | 15 |
| CE-2 (→ visits-service) | 6 | 15 |
| AC (container) | 0 | 18 |
| **Total** | **6** | **53** |

**D = 1** (single domain, no degradation applied)
**CRAFT Score = (6−0)/(53−0) × 10 = 1.13 → Tier: Unsatisfactory**

## Evidence ledger (summary — full detail in api-gateway-audit.json)

### CE-1 — call to customers-service (`CustomersServiceClient.java:29-32`)
No circuit breaker, no fallback, no retry, no timeout, no declared pool. **Zero protection on this call.** If `customers-service` hangs, this call hangs with it — nothing bounds it. This is a single point of total failure on the gateway's primary read path.

### CE-2 — call to visits-service (`ApiGatewayController.java:44-52`)
Circuit breaker present (`getOwnerDetails`), with a graceful fallback to an empty visit list. Scored 6/15: fallback earns full credit (5), but the circuit breaker earns only partial credit (1 of 3) because its prerequisite — an explicit timeout — could not be verified anywhere in the repository. Resilience4j ships a default TimeLimiter, but this repo declares no `resilience4j.*` configuration at all, so the effective value is unconfirmed rather than assumed.

### AC — container (`docker-compose.yml`, `pom.xml`)
Spring Boot Actuator is a declared dependency — `/actuator/health` exists at runtime — but **nothing in this repository wires it to anything.** `docker-compose.yml` defines a `healthcheck` block for `config-server` and `discovery-server` but not for `api-gateway`, and no Kubernetes manifests exist anywhere in the repo. The mechanism exists in the dependency tree; it is not connected to the orchestration layer. No graceful shutdown is configured — `server.shutdown: graceful` is absent — so every redeploy is a small, avoidable outage for in-flight requests.

### EE — the gateway's own entry
No rate limiter, no bulkhead on the gateway's own surface. (A `Retry` filter exists on the *outbound* proxy routes — that's SE/CE-class protection on traffic leaving the gateway toward vets/visits/customers services, logged as set-aside evidence, not counted here.)

## Remediation plan (ordered, cumulative)

| # | Action | Projected CRAFT Score |
|---|---|---|
| 1 | Explicit timeout on the customers-service call | 1.9 |
| 2 | Circuit breaker on the customers-service call | 2.5 |
| 3 | Fallback on the customers-service call | 3.4 |
| 4 | Wire `/actuator/health` to a real readiness + liveness probe | 4.5 |
| 5 | Distinct liveness probe + self-healing | 5.1 |
| 6 | Graceful shutdown | 5.9 |
| 7 | CPU limit + resource reservations | 6.3 |
| 8 | Rate limiter or bulkhead at the gateway's own entry | 7.5 |
| 9 | Confirm/configure explicit timeout & pool for the visits-service call | 8.9 |

## Data quality

- **4 items UNVERIFIED** (framework defaults not explicitly configured in-repo: timeout and pool on both CE calls, breaker's own timeout). None were scored positively — consistent with provenance-or-reject.
- **1 item SET_ASIDE** (outbound Retry filter on proxy routes — real evidence, doesn't fit the EE slot it was found near).
- **0 anti-pattern penalties triggered.** This service's weaknesses are *absences*, not *malformed presences* — worth noting, since the profile is equally capable of finding the opposite.

## A structural observation

The two downstream calls in this gateway are asymmetric in a way that is easy to miss reading the code casually and impossible to miss once scored: **the call with more business consequence (owner details) is the one with zero protection**, while the secondary enrichment call (visit history) is the one that's guarded. A reviewer skimming the file sees "there's a circuit breaker in here" and may reasonably assume the gateway is protected. The index disagrees, with evidence at the line level.
