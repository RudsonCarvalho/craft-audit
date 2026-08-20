# CRAFT Audit — microservices-demo (Google Online Boutique)
**Repo:** GoogleCloudPlatform/microservices-demo
**Commit:** 34ffea9175946982c3088ed84994fe6019ad6e92
**Profile:** MS-1.1.1.1 · **Date:** 2026-08-19
**Services audited:** checkoutservice (Go), cartservice (C#)

## Scores

| Service | Index | Max | D | IRC | Tier |
|---|---|---|---|---|---|
| checkoutservice | −1 | 113 | 1 | **0.16** | Unsatisfactory |
| cartservice | 11 | 37 | 1 | **2.97** | Unsatisfactory *(0.03 below Acceptable)* |

## Repo-wide confirmed absence

A repository-wide search across `src/` found **zero** matches for any circuit breaker, retry interceptor, or resilience library (Hystrix, Polly, custom or otherwise) in any service. This is not an inference from two services — it is a grep-confirmed fact about the whole codebase. Google's own reference architecture for microservices, used widely as a teaching and demo tool, ships its core order-processing path with no circuit breaking and no retry anywhere.

## checkoutservice — the flagship finding

`checkoutservice.PlaceOrder` orchestrates six downstream calls (shipping, cart, product catalog, currency, payment, email) to complete a single business transaction. All six have zero explicit timeout, zero circuit breaker, zero fallback, zero retry — confirmed at the call site for each.

**Worse than absence:** the call to `currencyservice` uses `context.TODO()` instead of the inbound request context, which discards the caller's deadline and cancellation signal entirely rather than merely lacking its own. This didn't fit any penalty in the MS-1.1 table — it's logged as a `SET_ASIDE` with a proposed new anti-pattern for the next profile revision (*deadline propagation break*).

**The health check is a confirmed active anti-pattern, not just an absence.** The gRPC health handler backing both the readiness and liveness probes unconditionally returns `SERVING`:

```go
func (cs *checkoutService) Check(ctx context.Context, req *healthpb.HealthCheckRequest) (*healthpb.HealthCheckResponse, error) {
	return &healthpb.HealthCheckResponse{Status: healthpb.HealthCheckResponse_SERVING}, nil
}
```

This is exactly the `unconditional_liveness` penalty (−3) the MS-1.1 revision added. It means Kubernetes can never detect that this pod is unhealthy through its own signal, regardless of whether any of its six downstream connections are actually reachable.

**One clean positive finding:** resource requests and limits (CPU and memory) are both fully declared — full credit on that item. The gaps here are specifically about failure handling, not general deployment hygiene.

## cartservice — the contrast case

Same repository, same language family of concerns, a genuinely different profile. `cartservice`'s health check calls `_cartStore.Ping()` against Redis and returns `NotServing` on failure — a **real, conditional check**, not a stub. Resource limits are fully declared. Self-healing earns full credit because its prerequisite is genuinely met.

What's missing is entirely on the data-dependency side: the `redis-cart` deployment has no `replicas:` field (defaults to 1 — no redundancy), and every Redis exception in `RedisCartStore.cs` is caught only to be re-thrown as an `RpcException` — translated for the gRPC boundary, not gracefully degraded. No fallback, no explicit timeout declared, no replication. **cartservice lands at 2.97 — three hundredths of a point below the Acceptable tier**, which is a useful illustration that the tier boundaries are not decorative: this service's remediation plan needs exactly one meaningful step (Redis timeout, projected +0.8) to cross into Acceptable.

## Cross-service pattern

Both services share a signature that PetClinic also showed: the health-check *machinery* is either present-but-real (cartservice) or present-but-hollow (checkoutservice) — never simply absent. Nobody skipped writing a health check. The gap is between having a probe wired and having it actually reflect service health, which is a calibration failure, not a presence failure, and is exactly the class of defect Section 5.1 argues only a value-resolving evaluator can catch.

## Data quality

- checkoutservice: 0 unverified, 2 set-aside (deadline-discard anti-pattern candidate; non-idempotent-write-without-retry visibility note)
- cartservice: 2 unverified (Redis timeout, graceful shutdown — both are plausible framework defaults, neither explicitly configured, neither credited)
- 0 items dropped as unclassifiable in either service
