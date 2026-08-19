---
name: craft-audit
description: Perform a CRAFT structural resilience audit on a code repository and compute the CRAFT Score (0-10) per service, with a full evidence ledger and machine-readable output. Use this skill whenever the user asks to audit, score, or evaluate the resilience, reliability, or structural robustness of a repository, microservice, or codebase; asks for an CRAFT Score score; asks to "run the resilience audit" against a repo; or wants to build a resilience dataset/corpus from one or more repositories. Trigger even if the user just provides a repo URL/path and mentions resilience, CRAFT, CRAFT Score, or structural analysis.
---

# CRAFT Structural Resilience Audit

Audit a repository's resilience **as built** — not as observed in production. Score protection mechanisms at each service's functional boundary using the MS-1.1 reference profile, apply anti-pattern penalties and the domain-coherence degradation factor, and emit a normalized CRAFT Score per service plus a machine-readable dataset.

**Core rule — provenance or reject:** every scored item MUST carry evidence: file path, line(s), and the resolved configuration value. If you cannot point to the evidence, the item scores 0 and is logged as `UNVERIFIED`. Never score from assumption, framework defaults you did not confirm, or "this project probably has X".

Read `references/profile.md` (weight tables, penalties, conditionals, bands) before scoring. Read `references/output-schema.md` before writing output files.

**Plain-language labels — mandatory in every human-facing report.** Vertical codes (EE, CE, SE, DI, AC, SE-KAFKA) are internal shorthand for evidence traceability, not something a reader should have to learn. In `-report.md`, `-findings-report.md`, and `scorecard.md` files, always use the plain-language name; the code may follow in parentheses only where it helps cross-reference the JSON, never on its own.

| Code | Never write this alone | Write this instead |
|---|---|---|
| EE | "EE-1" | **Entrada do cliente** (client entry point) |
| CE | "CE-1", "CE" | **Consulta externa** (call to an external dependency) |
| SE | "SE-1", "SE" | **Integração de saída** (outbound integration to another system) |
| DI | "DI-1", "DI" | **Dados internos** (internal data store) |
| AC | "AC-1", "AC" | **Configuração de container/implantação** (container & deployment configuration) |
| SE-KAFKA | "SE-KAFKA-1" | **Publicação de eventos** (event/message publishing) |

Example: write "Consulta externa (CE-1) — chamada ao serviço de catálogo", not "CE-1: catalog". JSON output keeps the codes as-is (that's the schema other tooling reads); only the prose changes.

**Same rule for the score itself.** Never write "CRAFT Score" alone in prose — write **Nota de Resiliência** (Resilience Score), with the number and the pyramid grau together, e.g. "Nota de Resiliência: 1.13 — Primeiro grau (Insatisfatório)". "CRAFT Score" may appear once, parenthetically, on first mention in a report if useful for cross-referencing the JSON or the underlying methodology (e.g. "Nota de Resiliência 1.13"), but never stand alone as the primary label afterward, and never as a bare column header — use "Nota" or "Nota de Resiliência" as the header instead. The JSON field name (`irc`) is unaffected — this rule is about human-facing prose and tables only.

## Workflow

### Step 0 — Setup

1. Clone or locate the repository. Record: repo URL/path, commit hash (`git rev-parse HEAD`), audit date.
2. Detect stack(s): language, framework (Spring Boot, Quarkus, Express, Go stdlib, .NET, etc.), deployment descriptors (Dockerfile, Kubernetes manifests, Helm, docker-compose).
3. Create the working directory for outputs: `<repo-name>-craft/`.

### Step 1 — Service inventory

Identify each independently deployable service. Signals: separate build files (pom.xml/package.json/go.mod per directory), separate Dockerfiles, entries in docker-compose/k8s manifests. List them. A mono-repo of N services yields N audits.

For each service, record: name, directory, language/framework, entrypoint.

### Step 2 — Boundary and interaction-point inventory (per service)

Apply the boundary rule: count only integrations/components **at the frontier of this service** whose failure compromises this service's function, and which this service's code/config controls. A dependency owned by another system is out of scope.

Inventory every interaction point and classify into verticals:

- **EE** (External Entry): each exposed endpoint surface facing clients (count the surface, e.g. the HTTP controller layer — not every route as a separate EE; but record the route count for Step 5)
- **SE** (External Exit): each outbound send with functional dependency (message publish, webhook, downstream POST)
- **CE** (External Consultation): each synchronous call to another system this service depends on
- **DI** (Internal Data): each database/cache/file dependency in this service's own domain
- **AC** (Application Container): the container/runtime config (one per service)
- **SE-KAFKA**: each Kafka/queue producer (use instead of generic SE for that point)

For every point record: identifier, target, and where it is defined (file:line).

### Step 3 — Mechanism detection with value resolution

For each interaction point, detect protection mechanisms **and resolve their effective values**. Search code AND configuration: annotations (`@Retry`, `@CircuitBreaker`, `@Timeout`, `@Bulkhead`, `@RateLimiter`), resilience libs (Resilience4j, Hystrix, Polly, opossum, gobreaker), HTTP client config (connect/read timeouts, pool sizes), retry policies (backoff type, jitter, max attempts), fallback methods, k8s probes (readiness/liveness/startup, and what the probe endpoint actually returns), SIGTERM/shutdown hooks, resource requests/limits, replication config for data stores.

Value resolution order: inline code → properties/yaml → profile overlays → environment defaults in manifests → framework default (only if documented; cite the doc). Record the resolution path.

**Step 3a — Indirect/injected protection sweep (mandatory, run once per repo before scoring any service).** Protection can be applied outside the call site: via AOP (`@Aspect`/`@Around`), a `BeanPostProcessor`, an `HttpClient`/`RestTemplate`/`WebClient` customizer or interceptor registered globally, a service-mesh sidecar (Istio/Linkerd `DestinationRule`, retry/circuit-breaking annotations on the mesh config rather than the app), or an internal shared "starter" library pulled in as a dependency. Missing these causes systematic under-crediting, not just isolated misses. Before scoring, explicitly:

1. List every internal/shared dependency declared in the build file (`pom.xml`, `go.mod`, `package.json`, `.csproj`) that isn't a well-known public library, and open it.
2. Grep the whole repo for `@Aspect`, `@Around`, `HandlerInterceptor`, `ClientHttpRequestInterceptor`, `RestTemplateCustomizer`, `BeanPostProcessor`, `DelegatingFilterProxy`, and language-equivalent interception hooks (Go: `http.RoundTripper` wrapping; Node: axios/fetch interceptors; .NET: `DelegatingHandler`, `IHttpClientFactory` named-client policies).
3. Check for a service mesh: `istio-manifests/`, `linkerd`, `DestinationRule`, `VirtualService` with `retries:`/`outlierDetection:` — mesh-level resilience is real and must be credited, but scored as a distinct evidence type (mesh-applied, not app-applied) since it protects the network hop, not necessarily the specific business-logic fallback.
4. If a global interceptor/aspect/mesh policy IS found, apply its effect to every point it covers and cite it once per point, referencing the shared definition rather than re-deriving it per call site.
5. If none is found after this sweep, state so explicitly in the output (`indirect_protection_sweep: "none found — checked: <list of what was searched>"`) so a reader can see the absence was checked for, not assumed.

**Anti-pattern checks (mandatory, per point where applicable):**
- Timeout inversion: this call's timeout vs. its caller's timeout, when both are in the repo
- Retry without backoff or without attempt cap
- Retry wrapping a non-idempotent write (check HTTP method/operation semantics)
- Circuit breaker whose threshold/window make tripping implausible
- Fallback that calls the same target or a target sharing the failing backend
- Liveness probe that cannot fail (static 200 / no real check)
- Pool configured with no timeout on the pooled calls

### Step 4 — Scoring (per service)

Using `references/profile.md`:

1. For each vertical instance, sum resolved weights (apply conditional rules and bands; apply mutual exclusions).
2. Sum penalties for detected anti-patterns.
3. `Index = Σ(vertical scores) + Σ(penalties)` (penalties are negative).
4. `Index_max` = sum of each present vertical instance's maximum.
5. `Index_min` = sum of applicable penalties for this topology (0 if none applicable).

### Step 5 — Degradation factor

Determine D = number of distinct functional domains served by this service. Heuristics: distinct business capabilities across controllers/handlers; unrelated endpoint groups; unrelated entity clusters. Be conservative: cohesive CRUD on one aggregate = 1 domain. Record the rationale and the endpoint count. Apply:

`Index_degraded = Index × 0.9^(D−1)`

### Step 6 — Normalization and tier

`CRAFT Score = ((Index_degraded − Index_min) / (Index_max − Index_min)) × 10`

Clamp to [0, 10]. Classify using the four-grade Confiabilidade pyramid. **The plain-language label is primary; "grau" is internal framework numbering and communicates nothing on its own — never lead with it.**

| Nota (score) | Rótulo (label) — always lead with this | Grau — secondary, cite only if tying back to the original pyramid diagram | What it means |
|---|---|---|---|
| 8.0–10.0 | **Excelente** | Quarto grau | High reliability and resilience; no additional-domain overhead |
| 5.0–7.9 | **Bom** | Terceiro grau | Reliable, but has single points of failure without fallback, or unprotected adjacent integrations |
| 3.0–4.9 | **Aceitável** | Segundo grau | Room for improvement; corrective measures required; low robustness |
| 0.0–2.9 | **Insatisfatório** | Primeiro grau | Requires revision; risks damage to adjacent services and the system as a whole |

Every score reported anywhere — JSON totals, markdown reports, corpus summaries, table headers — states the plain label (Excelente / Bom / Aceitável / Insatisfatório) next to the score. "Primeiro/Segundo/Terceiro/Quarto grau" may appear once as a parenthetical if the pyramid framing itself is being explained, never as a table column header and never as the only descriptor of a result. If in doubt, drop "grau" entirely and use only the plain label — it loses nothing.

### Step 7 — Findings report and remediation plan with fix prompts

For every absent or penalized mechanism, produce a **finding**, not just a scored row. Each finding has four required parts:

1. **What and where** — the mechanism that's missing or misconfigured, the exact class/method/config file and line, and the vertical/point it belongs to.
2. **Why it's a problem** — the concrete failure mode this gap allows (e.g., "no timeout on this call means a hung dependency holds the calling thread/connection indefinitely"), stated in terms of mechanism, not generically ("this is bad practice").
3. **Risk of not fixing it** — what happens under realistic production conditions if this ships as-is; name the symptom an on-call engineer would actually see (thread pool exhaustion, cascading latency, duplicate side effects, lost in-flight requests on deploy, etc.), not a restatement of the missing mechanism.

**Do not let severity language and score movement talk past each other.** A finding can be described as the single most operationally dangerous gap on a service while moving the score by only a fraction of a point, because the score is an aggregate over many mechanisms and no single mechanism carries more than its own weight out of the topology's total. When a finding's described severity ("the highest-risk gap on this service") and its score impact (a small fraction of `Index_max`) could otherwise read as contradictory, say so explicitly in the finding itself — one sentence is enough, e.g. *"Este é o maior risco operacional do serviço, mas vale sozinho apenas N de M pontos possíveis — a nota só se recupera de verdade fechando várias lacunas, não uma."* Never let the two scales imply each other without saying whether they agree or diverge.

4. **Fix prompt** — a self-contained, ready-to-hand-to-a-coding-agent instruction that would implement the fix. It must include: the exact file path, the current state (quote or paraphrase precisely), the target state (the specific mechanism and calibration to add, with concrete values — not "add a timeout" but "add a 2s response timeout matching the existing connect timeout pattern in `HttpClientsConfig`"), and an explicit constraint not to change unrelated behavior. Write it so a coding agent could execute it with no further clarification needed.

Then, exactly as before: sort findings by projected cumulative CRAFT Score gain (highest-leverage first), and report the projected CRAFT Score after each fix is applied on top of the previous ones — this is the ordering and the numbers, unchanged from prior versions of this skill. The finding narrative and fix prompt are additions alongside each ordered step, not a replacement for the projection.

**Mandatory gap disclosure.** If the findings list does not cover every remaining point in `Index_max` (i.e., the last cumulative projection is below 10.0 for reasons other than a genuinely unreachable ceiling — see below), the report MUST say so explicitly, in a closing line immediately after the cumulative summary table: state the score the full list reaches, and name what remains unaddressed with its point value, e.g. *"Estes achados cobrem os itens de maior impacto. Ainda restam N pontos não detalhados aqui, em [X, Y, Z] — aplicá-los levaria a nota a 10.0."* Never let a cumulative table imply completeness it doesn't have. If every point IS covered and the plan genuinely reaches 10.0, say that explicitly too, so the reader isn't left to infer either way.

**Mandatory ceiling disclosure.** Before claiming 10.0 is reachable, check whether the deployment topology can actually support every mechanism in `Index_max`. Some AC items assume a Kubernetes-style orchestrator (a distinct startup probe, a PodDisruptionBudget) — if the service is deployed only via `docker-compose` with no Kubernetes manifests anywhere in the repo, those specific points may be structurally unreachable without first changing the deployment target, not merely unimplemented. When this applies, say so explicitly in the report (e.g., *"3 destes pontos dependem de Kubernetes; este serviço roda hoje só em docker-compose, então o teto real sem mudar a forma de implantação é X, não 10.0"*) rather than implying the full profile maximum is always attainable in place.

Output each finding using the schema in `references/output-schema.md` (`findings` array). In the human-readable report, render each finding as its own subsection: problem → risk → fix prompt (in a fenced code block, ready to copy) → projected CRAFT Score after this fix.

### Step 8 — Output

Write, per service: `<service>-audit.json` (schema in `references/output-schema.md`) and `<service>-report.md` (human-readable: scores table with pyramid grau, evidence ledger, anti-patterns found, findings with fix prompts). Write one corpus-level `summary.csv`: service, repo, commit, IRC_raw, D, IRC_degraded, IRC_final, tier, grau, n_penalties, n_unverified.

If multiple services form a journey the user names, compute CRAFT_MP = weighted mean of IRCs normalized to [0,10] (weights 1 unless given) and append to the summary.

### Step 8a — Portfolio scorecard (when auditing 2+ services, a repo, or a corpus)

Whenever the audit covers more than one service — a multi-service repo, a named journey, or a running corpus across repos — produce an additional `scorecard.md`, styled as an engineering benchmark report (the way a DORA/Accelerate-style report reads: a portfolio view with explicit tier benchmarks and cross-cutting capability findings, not a bare table). Required sections, in this order:

1. **Executive summary** — one paragraph: N services audited, CRAFT Score range and mean, tier distribution, the single most consequential cross-service pattern found (if any repeats across ≥2 services, name it explicitly — a repeated pattern is a portfolio-level finding, not a per-service one).
2. **Benchmark legend** — the four-grade pyramid table from Step 6, shown once, so every score below is read against it without re-explaining.
3. **Tier distribution** — a compact bar built from characters (e.g. `Primeiro grau ████████ 6`) or a table of counts per grau; this is the "how does our portfolio stack up" view a DORA report leads with.
4. **Scorecard table** — one row per service: service, repo, CRAFT Score, grau, D, penalties, unverified count, one-line headline finding. Sort by CRAFT Score ascending (worst first — that's where attention is needed) unless the person asks otherwise.
5. **Cross-cutting capability findings** — patterns that recur across ≥2 services (e.g. "health probes wired but never connected to orchestration in every service audited"), each with the count of services affected and a single representative fix prompt that generalizes across them.
6. **Per-tier detail** — one short subsection per grau present in the results, listing which services landed there and the one or two dominant reasons (not a full findings dump — point to the per-service report for that).
7. **Methodology footnote** — profile version, audit date(s), and a one-line reminder that this is structural conformance, not observed outcome (do not let the scorecard imply operational performance).

This scorecard is the artifact meant for a portfolio owner, staff engineer, or paper reader who wants the shape of the results before the detail — the per-service `-report.md` and `-audit.json` remain the source of truth underneath it.

### Step 9 — Honesty checks (before finishing)

- Every scored line has file:line evidence? Items without it are 0 + `UNVERIFIED`.
- Report the count of interaction points you could NOT classify — do not silently drop them.
- If the stack is one the profile's mechanism list fits poorly (e.g., no container, batch job), say so; do not force-fit.
- State the profile version used (MS-1.1) in every output file.

## Sensitivity mode (optional)

If the user asks for sensitivity analysis: re-run Step 4–6 perturbing each weight by ±1 and ±2, and the degradation base at 0.85/0.90/0.95. Report the fraction of services whose tier changes, per perturbation, in `sensitivity.csv`.
