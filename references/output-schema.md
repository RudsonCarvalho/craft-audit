# Output Schema

## Per-service `<service>-audit.json`

```json
{
  "profile_version": "MS-1.1",
  "audit": { "repo": "", "commit": "", "date": "", "auditor": "agent" },
  "service": { "name": "", "path": "", "language": "", "framework": "" },
  "boundary": {
    "included_points": 0,
    "excluded_points": [ { "target": "", "reason": "outside boundary" } ],
    "unclassified_points": 0
  },
  "points": [
    {
      "id": "CE-1",
      "vertical": "CE",
      "target": "payment-service /charge",
      "defined_at": "src/clients/PaymentClient.java:41",
      "mechanisms": [
        {
          "name": "timeout",
          "resolved_value": "PT2S",
          "resolution_path": "application.yml:23 -> profile prod overlay",
          "evidence": "config/application-prod.yml:23",
          "weight": 4,
          "condition_applied": null,
          "status": "VERIFIED"
        }
      ],
      "penalties": [
        { "name": "retry_without_backoff", "evidence": "…", "weight": -2 }
      ],
      "set_aside": [ { "name": "hedged-request", "evidence": "…" } ],
      "point_score": 0
    }
  ],
  "totals": {
    "index_raw": 0,
    "penalties_sum": 0,
    "index": 0,
    "index_min": 0,
    "index_max": 0,
    "domains_D": 1,
    "domains_rationale": "",
    "endpoint_count": 0,
    "degradation_factor": 1.0,
    "index_degraded": 0,
    "irc": 0.0,
    "tier": "Good"
  },
  "remediation": [
    { "order": 1, "action": "", "projected_irc": 0.0, "rationale": "" }
  ],
  "findings": [
    {
      "id": "F-1",
      "linked_action_order": 1,
      "point_id": "CE-1",
      "mechanism": "timeout",
      "location": { "file": "src/.../CustomersServiceClient.java", "line": "23-25" },
      "what": "The WebClient used for this call is built with no .responseTimeout()/.timeout() and no HttpClient customization; no timeout is configured anywhere in the resolution chain for this call.",
      "why_its_a_problem": "Without a bounded response timeout, the reactive pipeline holding this call has no upper limit on how long it will wait for the downstream service to respond.",
      "risk_if_unfixed": "If the downstream dependency hangs (not fails — hangs) rather than erroring, this call blocks indefinitely, holding the calling thread/connection and any upstream caller waiting on it. Under load this manifests as pool exhaustion and cascading latency into every service upstream of this one, and is invisible to health checks that don't specifically probe this path.",
      "fix_prompt": "In src/.../CustomersServiceClient.java, the WebClient injected via the constructor is used with no timeout configuration. Add an explicit response timeout of 2s to this specific call using .timeout(Duration.ofSeconds(2)) on the returned Mono, matching the existing timeout convention used elsewhere in this codebase if one exists (check HttpClientsConfig or equivalent for a shared pattern before introducing a new one). Do not change the method signature, the return type, or any other call in this file. Add a unit test that verifies the call fails fast (within ~2.1s) when the downstream does not respond, using a delayed/hanging stub."
    }
  ],
  "quality": { "unverified_count": 0, "set_aside_count": 0 }
}
```

## Corpus `summary.csv`

`repo,commit,service,language,framework,points,index,index_min,index_max,D,irc_raw,irc_final,tier,penalties,unverified,set_aside`

## `sensitivity.csv` (sensitivity mode only)

`perturbation,parameter,delta,services_total,tier_changes,tier_change_fraction`
