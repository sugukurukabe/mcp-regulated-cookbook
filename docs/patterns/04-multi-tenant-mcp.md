---
title: "Multi-tenant MCP Architectures: Context-bound Data Isolation"
status: stable
version: 1.0.0
last_reviewed: 2026-04-28
spec_version: "2025-11-25"
domains:
  - finance
  - hr
  - healthcare
  - public-sector
  - saas
platforms_tested:
  - "Supabase (PostgreSQL RLS)"
  - "FastMCP (Python ContextVar)"
contributors:
  - "@sugukurukabe (Sugukuru Inc., CEO/CTO) — primary deployment"
---

# Pattern 04: Multi-tenant MCP Architectures: Context-bound Data Isolation

> **One-sentence summary.** Securely isolate tenant data in MCP servers by binding tenant identity at the transport layer to asynchronous context variables, enforcing it automatically at the database query and RLS layers without relying on LLM input.

## When to use this pattern

You are likely in scope if:
- You are building a B2B SaaS or an MCP server that serves multiple client organizations (tenants).
- You need to guarantee that an AI agent acting on behalf of Tenant A cannot query, update, or delete data belonging to Tenant B.
- You are using connection-level authentication (e.g., API keys, OAuth tokens) to identify the calling client.

You are likely **not** in scope if:
- Your MCP server serves a single organization (single-tenant) or local personal data only.
- Your tools operate exclusively on open, public data with no access restrictions.

## Forces

- **LLM Hallucination vs Security.** If you design an MCP tool like `get_staff_list(org_id: str)`, the LLM is responsible for passing the `org_id`. A hallucination or a prompt injection could cause the LLM to pass another tenant's ID, leading to a critical data breach.
- **Protocol Limitations.** The current MCP specification does not natively define a "tenant context" standard.
- **Developer Ergonomics.** Expecting developers to manually add `where org_id = current_tenant` to every SQL query across dozens of MCP tools will inevitably lead to a forgotten filter and a security incident.

## Solution

**The recommendation.** Never trust the LLM to define the security boundary. Extract the tenant identity at the transport connection phase (e.g., from an API key), store it in an asynchronous context variable, and automatically inject it into every database operation via an intercepted DB client and PostgreSQL Row Level Security (RLS).

### The Implementation Proof

This is not theoretical. At Sugukuru Inc., this pattern processes highly regulated HR and Visa data across multiple enterprise clients (e.g., "JA Kimotsuki", "WIN International").

#### 1. Transport & Context Layer (Python `ContextVar`)
When the MCP connection is established, the API key is verified and the `org_id` is stored in a thread-safe/async-safe `ContextVar`. The LLM never sees this ID.

```python
# Evidence from: /src/sugukuru_hub/tenant.py
from contextvars import ContextVar

_current_tenant: ContextVar[Optional["TenantContext"]] = ContextVar("_current_tenant", default=None)

async def resolve_tenant_by_api_key(api_key: str) -> Optional[TenantContext]:
    # Resolves 'sk-ja-kimotsuki-001' -> '00000000-...-0002'
    result = supabase.table("organizations").select("*").eq("api_key", api_key).single().execute()
    # ...
```

#### 2. Application-Level Automatic Injection
The database client wraps all standard operations (SELECT, INSERT, UPDATE) and automatically injects the tenant filter. A developer writing a tool just calls `db.select("staff")`, and it securely becomes `select * from staff where org_id = '...'`.

```python
# Evidence from: /src/sugukuru_hub/tools/supabase_client.py
def _inject_org_id_filter(self, table: str, params: dict) -> dict:
    """Automatically inject org_id filter into tenant tables"""
    if table in TENANT_TABLES and "org_id" not in params:
        org_id = get_org_id() # Reads from ContextVar
        if org_id:
            params["org_id"] = f"eq.{org_id}"
    return params
```

#### 3. Database-Level Enforcement (PostgreSQL RLS)
For defense-in-depth, if client tokens are used or if a developer bypasses the wrapper, PostgreSQL Row Level Security (RLS) guarantees data isolation. 

```sql
-- Evidence from: /supabase/migrations/016_multi_tenant.sql
CREATE OR REPLACE FUNCTION get_current_org_id() RETURNS UUID AS $$
BEGIN
    RETURN (auth.jwt() -> 'app_metadata' ->> 'org_id')::UUID;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

CREATE POLICY "staff_tenant" ON staff FOR ALL TO authenticated
    USING (org_id = get_current_org_id())
    WITH CHECK (org_id = get_current_org_id());
```

## Trade-offs

- **Implementation overhead.** Requires building a wrapper around your database client or ORM.
- **Tool testing complexity.** You cannot test an MCP tool in isolation without mocking the transport-layer API key or ContextVar injection.

## When this pattern fails

- **Failure mode: Global dashboard queries.** If an internal administrator needs an MCP tool to query aggregate metrics across *all* tenants (e.g., total active users), this pattern's strict isolation will block the query. You must explicitly create an internal "Super Admin" bypass, which is high risk.

## Real deployments

- [**Case Study 01: Sugukuru Inc.**](../case-studies/01-sugukuru.md) — Over 100 MCP tools (115 unique tool definitions verified in the `aios` Python codebase) operating across organizations including `sugukuru`, `ja-kimotsuki`, and `win-international` (active production tenants—meaning live internal operational boundaries using real data, not external SaaS customers—verified via Supabase `organizations` table screenshot). The codebase securely separates foreign workers' PII, visa statuses, and financial records across 62 tenant-isolated database tables entirely through this `ContextVar` + automatic `org_id` injection + RLS combination.

## Changelog

- **1.0.0** (2026-04-28) — Initial publication. Extracted from the `sugukuru_hub` multi-tenant architecture.
