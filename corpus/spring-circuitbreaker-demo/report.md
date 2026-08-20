# CRAFT Audit — spring-circuitbreaker-demo
**Repo:** rbiedrawa/spring-circuitbreaker-demo
**Commit:** 2e7be63ed140d33f55498bc9b43c9d786b02cf78
**IRC: 2.17 — Unsatisfactory**

## Why this result matters more than the number

This repository exists specifically to showcase Resilience4j. `HelloService.sayHello()` is decorated with all four core annotations at once:

```java
@TimeLimiter(name = CB_SAY_HELLO)
@Retry(name = CB_SAY_HELLO)
@CircuitBreaker(name = CB_SAY_HELLO, fallbackMethod = "sayHelloFallback")
@Bulkhead(name = CB_SAY_HELLO)
Mono<String> sayHello(Optional<String> name) { ... }
```

Backed by a fully calibrated `application.yml` — exponential backoff with a 2x multiplier, a 50% failure-rate threshold over a sliding window of 10 calls, a 1-second time limiter, a real fallback method. Every value is explicit, not a framework default. **By a presence-counting index — exactly the "macro index" the original CRAFT specification downgraded in 2023 — this service scores at or near the ceiling.** It has more distinct annotated patterns per line of code than any other service audited in this corpus.

**CRAFT scores it 2.17, Unsatisfactory, and the reason is the finding:** `remoteCall()`, the method all four annotations wrap, does no I/O. It is:

```java
private Function<String, Mono<String>> remoteCall(long delayInSeconds) {
	return str -> {
		var msg = String.format("Hello %s! (completed in %d sec.)", str, delayInSeconds);
		return Mono.just(msg);
	};
}
```

No HTTP client. No gRPC stub. No database. The "failure" the circuit breaker, retry, and time limiter are protecting against is an artificial `Math.random()`-driven delay injected purely to make the demo trip its own thresholds. Per CRAFT's boundary rule — score only integrations at the frontier of the application whose failure would compromise its function — **there is no CE point here at all.** There is nothing external to be a frontier of.

## What the audit credited, and what it correctly withheld

- **EE-1 (Bulkhead): full credit, 5/5.** The bulkhead is real regardless of what it wraps — it protects this service's own thread pool from concurrent-call exhaustion, which is a legitimate self-contained protection.
- **CE, SE, DI: not scored, and not scored as zero either.** They are excluded from the index's denominator entirely, because no interaction point of those kinds exists in this topology. `index_max = 23` (5 EE + 18 AC), not 113 or 53 as in the richer services audited earlier — this service's ceiling is honestly bounded by what it actually has.
- **A configured-but-orphaned rate limiter, found and flagged.** `application.yml` fully specifies a rate limiter (10 requests/second) that no `@RateLimiter` annotation in the codebase ever applies. Logged as a new status category — `CONFIGURED_BUT_UNAPPLIED` — distinct from `UNVERIFIED`. This is more informative to a developer than silence: it's a dead config block, worth knowing about on its own terms.
- **AC vertical: same absence pattern as every other service in the corpus.** Actuator exposes genuinely rich health data (circuit breaker and rate limiter state included), but nothing wires it to a `docker-compose` healthcheck. This is now the fourth repository in a row where the health-check *content* exists but isn't *connected* — a pattern worth stating as a cross-corpus finding, not a one-off.

## Interpretation note — read this before treating 2.17 as "the app is bad"

The score decomposes into two independent risk axes, and this repository is a clean, worked example of why keeping them separate matters:

- **Boundary risk (EE + CE + SE + DI): as good as it can be.** The one real interaction point this service has — its own entry surface — scores full marks (5/5) on a genuine, well-configured protection. CE/SE/DI are correctly excluded from the denominator rather than scored as failing, precisely because there is no dependency there to protect. **The absence of something that shouldn't exist does not count against this service — verify this yourself in the numbers: `index_max` is 23, not 113 or 53 like the richer services in this corpus.** If this service's only job is to return a constant, its boundary-risk profile is legitimately excellent, and the audit says so.
- **Lifecycle risk (AC): unmitigated, and this is a separate concern from the above.** The 18 unearned AC points are about container crash recovery, deploy-time request draining, and resource exhaustion — risks that exist regardless of what the code inside the container does. A container that only formats strings can still be OOM-killed, still loses in-flight requests on a careless redeploy, still benefits from a liveness probe that reflects real state. This axis is genuinely open regardless of how trivial the business logic is.

**The one caveat worth stating plainly: this repository is a published tutorial, not a production deployment,** and judging its `docker-compose.yml` by production-readiness expectations is a defensible but debatable choice — the file is scored exactly as written, which is the fair and reproducible thing to do, but the practical reading for anyone actually working from this repo is: *the AC gaps here are close to the lowest-priority fix imaginable, because nothing of consequence is actually being protected.* A future profile revision could weight AC risk by the consequence of the boundary it sits behind — losing an in-flight string-formatting request is cheaper than losing an in-flight payment — but that is a deliberate model extension for a later version, not a correction applied retroactively to this score. Flagging it here rather than quietly adjusting the number is the more honest choice: the score stays comparable to the rest of the corpus, and the context travels with it.

## The methodological payoff

This case is a direct, real-world demonstration of the paper's central distinction between a **macro/presence index** and CRAFT's **boundary-anchored, calibration-aware model**. A tool that counted annotations would rank this repository above every other service audited so far. CRAFT ranks it below `cartservice` (2.97) and above `checkoutservice` (0.16) — for the correct reason: it has excellent, real protection on the one real interaction point it has (its own entry surface), and zero protectable surface anywhere else, because there is nothing else to protect.

This is worth using in the paper verbatim as the canonical illustration for Section 5.1 — it is a stronger example than any synthetic one, precisely because the author of this repository was not trying to fool an evaluator. They were trying to teach Resilience4j, honestly and well, and in doing so built the clearest natural specimen of "protection density without a boundary" available in the open-source ecosystem.

## Data quality

- 0 unverified items
- 1 set-aside (orphaned rate limiter config)
- Indirect-protection sweep run and returned negative — no AOP, no shared library, no mesh, confirmed by dependency and codebase inspection
