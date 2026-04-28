---
title: "Cloud Run Multi-Instance Session Continuity"
status: stable
version: 0.3.0
last_reviewed: 2026-04-28
spec_version: "2025-11-25"
domains:
  - immigration
  - labor
  - agriculture
  - other
platforms_tested:
  - "Google Cloud Run (asia-northeast1)"
contributors:
  - "@sugukurukabe (Sugukuru Inc., CEO/CTO) — primary deployment"
evidence:
  - "GCP Console screenshots (2026-04-28) — sugukuru-core, sugukuru-finance, sugukuru-crm"
  - "deploy-mcp-split.sh (initial deployment script)"
---

# Pattern 01: Cloud Run Multi-Instance Session Continuity

> **One-sentence summary.** Run stateful MCP `streamable_http` servers on Cloud Run without losing the `mcp-session-id`, by combining `sessionAffinity: true` with either a warm baseline (`min-instances: 1`) for critical services or scale-to-zero (`min-instances: 0`) for cost-sensitive services.

## When to use this pattern

You are likely in scope if:

- You deploy your MCP server on a serverless platform that scales horizontally (Google Cloud Run).
- You use `streamable_http` transport with stateful sessions.
- Your server is configured with autoscaling that allows more than one instance under load.
- You want to balance cloud costs against session reliability during horizontal scaling.

You are likely **not** in scope if:

- You run on a single VM or a single always-on container.
- You have already moved to fully stateless mode.
- You use only `stdio` transport.

## Forces

- **Cost vs session continuity.** `min-instances: 0` is the cheapest configuration but adds cold-start latency (5–10s observed in live operation). `min-instances: 1` eliminates cold starts but costs ~$15-30/month per service.
- **Cloud Run-native session affinity.** Cloud Run supports cookie-based session affinity (`--session-affinity`) that pins a session's traffic to the same instance.
- **External session store cost vs latency.** Adding Redis for session storage adds 1–5 ms latency and a new failure domain.
- **Service criticality asymmetry.** Not all MCP servers in a fleet have the same availability requirements.

## Solution

**The recommendation.** Use Cloud Run-native sticky sessions (`--session-affinity`) combined with a **per-service scaling strategy**: set `min-instances: 1` for your most critical MCP server (the one users connect to first and most frequently), and `min-instances: 0` for secondary services. This hybrid approach, verified in live operation at Sugukuru Inc., balances cost against cold-start user experience without any external session store.

### Path A: Warm baseline for critical services

For the primary MCP server that handles the majority of user sessions:

```
Verified in live operation (GCP Console, 2026-04-28):
  sugukuru-core → Min: 1, Max: 20, session-affinity: true
```

The session affinity annotation is confirmed in the Cloud Run service YAML:

```yaml
# Cloud Run YAML tab — sugukuru-core (lines 38-43)
annotations:
  autoscaling.knative.dev/maxScale: "10"
  run.googleapis.com/client-name: gcloud
  run.googleapis.com/client-version: 550.0.0
  run.googleapis.com/sessionAffinity: "true"        # ← definitive proof
  run.googleapis.com/startup-cpu-boost: "true"       # ← cold-start mitigation
```

This eliminates cold-start latency for the first user request. The session affinity cookie pins subsequent requests to the warm instance. Under load, Cloud Run scales up additional instances, and the cookie ensures each session stays pinned to its assigned instance.

**When to choose Path A:**
- The service is the primary entry point for users.
- Cold starts of 5–10 seconds on the first request are unacceptable for the user experience.
- The cost of one always-on instance (~$15-30/month) is acceptable.

### Path B: Scale-to-zero for secondary services

For MCP servers that are called less frequently or where occasional cold-start latency is acceptable:

```
Verified in live operation (GCP Console, 2026-04-28):
  sugukuru-finance → Min: 0, Max: 20, session-affinity: true
  sugukuru-crm     → Min: 0, Max: 20, session-affinity: true
```

These services scale to zero when idle. The first request triggers a cold start (p50: ~5s, p99: up to 10s, as observed in operational metrics). The session affinity cookie then pins the session to the newly created instance.

**When to choose Path B:**
- The service is called infrequently or as a secondary service in an agent workflow.
- Cold-start latency of 5–10 seconds is tolerable.
- You want zero idle cost.

### The initial deploy script vs operational reality

The initial deployment script (`deploy-mcp-split.sh`) sets `--min-instances=0 --max-instances=10` for all services:

```bash
# deploy-mcp-split.sh L78-92 (initial deployment configuration)
gcloud run deploy "${SERVICE_NAME}" \
    --session-affinity \
    --min-instances=0 \
    --max-instances=10 \
    --timeout=300 \
    --concurrency=80
```

However, GCP Console screenshots from 2026-04-28 show that the production configuration has diverged:
- `sugukuru-core` was manually adjusted to **Min: 1, Max: 20** post-deployment.
- `sugukuru-finance` and `sugukuru-crm` remain at **Min: 0, Max: 20** (Max was raised from 10 to 20).

This divergence itself is a pattern worth documenting: **operational tuning after initial deployment is normal and expected.** The deploy script serves as the baseline, but production settings evolve based on observed traffic patterns and cold-start pain points.

### Path C: Externalized session state

For deployments that have grown beyond Path A/B's capacity or require zero session loss across `gcloud run deploy` revisions, you may introduce a shared session store like Memorystore for Redis. However, do not over-engineer to Path C without evidence that Path A or B is failing.

## Production metrics (from GCP Console, 2026-04-28)

| Metric | sugukuru-core | sugukuru-finance | sugukuru-crm |
|---|---|---|---|
| min-instances | 1 | 0 | 0 |
| max-instances | 20 | 20 | 20 |
| Container startup (p50) | ~5s | ~5s | ~5s |
| Container startup (p99) | ~30s | ~10s | ~10s |
| Max observed instances | ~20 | ~4 | ~4 |
| External session store | None | None | None |

> **Evidence source:** GCP Console Cloud Run Observability tab, Last 30 days view, captured 2026-04-28. Screenshots available in `reference/screenshots/`.

## Trade-offs

- **Operational cost.** Path A costs one always-on instance. Path B is zero idle cost. Total Cloud Run cost for 3 MCP servers: **~¥25,400/month (~$162 USD)** as verified from GCP Billing (April 2026, 26-day partial month).
- **Performance cost.** Path B cold starts take 5–10s (p50–p99). Path A eliminates cold starts for the first instance. Cloud Run's `startup-cpu-boost: "true"` annotation (confirmed in YAML) allocates additional CPU during startup to reduce cold-start duration.
- **Complexity cost.** Revision rollouts will drop in-flight sessions pinned to old instances. This is true for both Path A and B.

## When this pattern fails

- **Path A/B fail: traffic exceeds capacity envelope.** If concurrent sessions exceed what `maxScale` can handle, new sessions begin landing on instances they cannot stay pinned to.
- **Path A/B fail: revision rollout invalidates sessions.** During `gcloud run deploy`, in-flight sessions on the previous revision can be terminated mid-stream.
- **Path B fails: user-facing cold starts.** If the first request to a scale-to-zero service is user-initiated (not agent-initiated), the 5–10s cold start degrades the experience.

## Real deployments

- [**Case Study 01: Sugukuru Inc.**](../case-studies/01-sugukuru.md) — Three MCP servers on Cloud Run `asia-northeast1` running Python/FastMCP. `core` uses Path A (Min: 1), `finance` and `crm` use Path B (Min: 0). All use `--session-affinity`. No external session store. Production metrics confirm the configuration via GCP Console screenshots.

## Changelog

- **0.3.1** (2026-04-28) — Added definitive YAML evidence for `sessionAffinity: "true"` (line 42 of Cloud Run YAML tab). Added `startup-cpu-boost` annotation detail. Added Cloud Run billing data (¥25,400/month for 3 services).
- **0.3.0** (2026-04-28) — **Major correction from GCP Console evidence.** Discovered that `sugukuru-core` actually runs with `min-instances: 1` (not 0), and all services have `max-instances: 20` (not 10). The deploy script was only the initial configuration; production settings have diverged. Restructured pattern into Path A (warm) and Path B (scale-to-zero) as a complementary hybrid.
- **0.2.1** (2026-04-27) — Incorrectly stated all services use `min-instances: 0` based on deploy script alone. Corrected in v0.3.0.
- **0.2.0** (2026-04-27) — Restructured into paths.
