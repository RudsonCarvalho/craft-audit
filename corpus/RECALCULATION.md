# Corpus Recalculation — MS-1.1 → MS-1.1.1

**Date:** 2026-08-19 · **Applies to:** every audit in `corpus/`

The corpus was originally scored under profile MS-1.1. Two defects in that profile were found after the audits were complete, both corrected in MS-1.1.1, and every affected score was recomputed. This file records what changed and why, rather than silently republishing new numbers.

## Defect 1 — Declared vertical maxima did not match the weight tables

MS-1.1 declared CE max = 15 and SE max = 21. The literal sum of each vertical's own table, including the +1 global-retry-budget modifier, is **17** (CE) and **23** (SE):

```
CE: circuit breaker 3 + fallback 5 + retry band 2 + retry budget 1 + timeout 4 + pool 2 = 17
SE: the above + idempotent write 4 + compression 1 + async dispatch 1              = 23
```

This was an arithmetic error present since the profile was drafted. It was **found by the positive-control fixture** (`resilience-golden-demo`), whose own documentation flagged the inconsistency during its audit — a fixture correcting the instrument rather than merely confirming it.

Effect: any service with CE or SE interaction points had an understated `index_max`, and therefore an overstated score.

## Defect 2 — checkoutservice did not follow the published normalisation formula

The `checkoutservice` ledger recorded `index = -1`, `index_min = -3`, `index_max = 113`, and a score of 1.72. Applying the published formula to those same values gives:

```
(-1 - (-3)) / (113 - (-3)) × 10 = 2/116 × 10 = 0.17
```

The 1.72 figure was not derivable from its own ledger. Under the corrected MS-1.1.1 maximum (`5 + 6×17 + 18 = 125`) the correct value is **0.16**.

## Clarification — penalties are excluded from the degradation term

MS-1.1.1 specifies:

```
Index_degraded = [ Σ max(V×W, 0) ] × 0.9^(D-1) + Σ penalties
```

Applying the degradation factor to a negative total would make a penalised service score *less* negative as domains are added — additional incoherence would algebraically relieve an anti-pattern. Degradation therefore scales only the positive protection total.

This clarification is **inert for the present corpus** (every audited service has D = 1) but is recorded because the formula, once published, will be applied where it is not.

## Clarification — retry band is conditional on a verified timeout

MS-1.1.1 makes explicit the prerequisite already stated in the paper's conditional-weights table: the retry band scores 0 without a verified timeout on the same interaction point, since a retry without a time bound can re-issue a hanging call indefinitely.

**No corpus score changes as a result**: every retry scored in this corpus co-occurs with a verified timeout.

## Score changes

| Service | MS-1.1 (superseded) | MS-1.1.1 (current) | Cause |
|---|---:|---:|---|
| api-gateway | 1.13 | **1.05** | CE max 15→17 on two CE points |
| checkoutservice | 1.72 | **0.16** | Defect 2 + CE max on six CE points |
| ts-preserve-service | 0.05 | **0.04** | CE max on eleven CE points, SE max on one |
| customers-service | 0.00 | 0.00 | unchanged (no CE/SE points) |
| visits-service | 0.00 | 0.00 | unchanged |
| vets-service | 0.00 | 0.00 | unchanged |
| circuitbreaker-demo | 2.17 | 2.17 | unchanged (no CE/SE points) |
| cartservice | 2.97 | 2.97 | unchanged (no CE/SE points) |
| resilience-golden-demo | 10.00 | 10.00 | already scored under MS-1.1.1 |

**Corpus mean: 2.00 → 1.82.** Range unchanged (0.00–10.00). Tier assignment unchanged for every service — all eight low-scoring services remain Insatisfatório and the fixture remains Excelente.

## Note on evidence

No evidence ledger entry was altered: every file, line, resolved value, and mechanism classification recorded during the original audits stands unchanged. Only the derived arithmetic — `index_max`, `index_min`, and the resulting score — was recomputed. The audits remain re-derivable from their recorded commits.
