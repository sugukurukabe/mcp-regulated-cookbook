# GCP Console Screenshots — Production Evidence

Captured: 2026-04-28 (from user-provided screenshots of GCP Cloud Console)

## Extracted Facts

### sugukuru-core (Screenshots 1 & 4)
- **Region**: asia-northeast1
- **URL**: https://sugukuru-core-771327592526.asia-northeast1.run.app
- **Scaling**: Auto (**Min: 1**, Max: 20)
- **Container startup latency**: p50 ~5s, p99 up to 30s
- **Request latency (p95)**: ~5-10 min range (expected for long-lived MCP streaming connections)
- **Container instances**: max observed ~20, with active/idle pattern
- **HTTP status codes**: predominantly 2xx, occasional 3xx/4xx/5xx

### sugukuru-finance (Screenshot 2)
- **Region**: asia-northeast1
- **URL**: https://sugukuru-finance-771327592526.asia-northeast1.run.app
- **Scaling**: Auto (Min: 0, Max: 20)
- **Container startup latency**: p50 ~5s, spikes to ~10s
- **Container instances**: max observed ~4
- **HTTP status codes**: predominantly 2xx, some 3xx/4xx

### sugukuru-crm (Screenshot 3)
- **Region**: asia-northeast1
- **URL**: https://sugukuru-crm-771327592526.asia-northeast1.run.app
- **Scaling**: Auto (Min: 0, Max: 20)
- **Container startup latency**: p50 ~5s, spikes to ~10s
- **Container instances**: max observed ~4
- **HTTP status codes**: predominantly 2xx, some 4xx

## Critical Discrepancies vs deploy-mcp-split.sh

| Setting | deploy-mcp-split.sh | GCP Console (actual) |
|---|---|---|
| sugukuru-core min-instances | 0 | **1** |
| All services max-instances | 10 | **20** |

**Conclusion**: The deploy script represents the initial deployment configuration, but production settings have been subsequently modified (likely via `gcloud` CLI or GCP Console directly). The GCP Console screenshots are the ultimate source of truth.
