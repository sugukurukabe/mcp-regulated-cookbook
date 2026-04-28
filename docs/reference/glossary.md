---
title: "Glossary"
status: living
version: 0.1.0
last_reviewed: 2026-04-28
---

# Glossary

Terms used across cookbook chapters. Spec-native terms are cross-referenced to the MCP specification where possible.

## A

**`aios`** — The internal name for the Sugukuru MCP fleet's Python monorepo (containing `sugukuru-core`, `sugukuru-finance`, `sugukuru-crm`, and `sugukuru-hub` source). When chapters reference Sugukuru's codebase, the convention is "the `sugukuru-core` Python codebase (internally named `aios`)."

**Annotation** — A property attached to an MCP tool definition signaling its risk profile to the client. The four annotations the MCP spec currently defines are `readOnlyHint`, `destructiveHint`, `idempotentHint`, and `openWorldHint`. See Pattern 02.

**`attributed`** — A case study attribution level: the deploying organization is named, and a contact participates in review. Contrast with `industry-attributed` and `anonymized`. See `cookbook-strategy-principles.md` §5.2.

## C

**Case study** — A documented live deployment. Distinguishable from a pattern in that it does not need to recommend anything; it can simply describe.

**Cloud Run** — Google Cloud's managed serverless container platform. The deployment target for Sugukuru's MCP fleet and the target of Pattern 01.

**`containerConcurrency`** — A Cloud Run setting that controls how many concurrent requests one instance handles. Sugukuru's fleet runs at `80` (the Cloud Run default).

## D

**`destructiveHint`** — One of the four MCP tool annotations. Per Pattern 02, `destructiveHint` follows the legal effect of the tool, not the technical reversibility — a tool that records a regulatory filing is `destructiveHint: true` even if calling it twice is technically safe, because the filing event is itself reportable.

**Document AI** — Google Cloud Document AI, used by `sugukuru-core` for OCR and structured extraction. See Pattern 03.

## F

**FastMCP** — A Python framework for building MCP servers. The runtime for `sugukuru-core`, `sugukuru-finance`, and `sugukuru-crm`.

## G

**`gcp-verified-facts.md`** — The truth ledger for facts about Sugukuru's GCP deployment that other cookbook chapters cite. See `OPERATIONS.md` Section C.1.

## I

**`idempotentHint`** — MCP tool annotation. True if calling the tool twice with the same input produces the same observable outcome as calling it once.

**`industry-attributed`** — A case study attribution level: industry and rough scale are named, but not the organization.

## L

**Lethal Trifecta** — A term coined by Simon Willison to describe the dangerous combination of (a) untrusted external input, (b) tools capable of taking action, and (c) access to private data — a combination commonly present in agentic MCP deployments. Related to the proposed Pattern: Lethal Trifecta Defenses for MCP Servers.

## M

**MCP** — Model Context Protocol. See [https://modelcontextprotocol.io](https://modelcontextprotocol.io).

**`mcp-session-id`** — A header per the MCP `streamable_http` transport identifying a stateful session. Validated server-side on every non-`initialize` request. The integrity of this validation across multiple Cloud Run instances is the central concern of Pattern 01.

**MCP Apps** — A spec proposal published in 2025 covering client-side UI patterns for MCP. Adjacent to but separate from this cookbook's server-side scope.

**`memo-errata.md`** — The cookbook's running record of factual claims that turned out to be false, kept on file as a negative reference.

**`min-instances`** — A Cloud Run scaling parameter. `min-instances: 1` keeps an instance always warm; `min-instances: 0` allows the service to scale to zero. Pattern 01 explores when each is appropriate.

## O

**`openWorldHint`** — MCP tool annotation. True if the tool acts on data drawn from sources outside the deploying organization's control. Combined with `destructiveHint: true`, this is the strongest signal to clients that user confirmation should be requested.

**OPERATIONS.md** — This cookbook's operations manual. Defines procedures for chapter-authoring, fact-verification, and tool interoperation.

## P

**Pattern** — A reusable solution to a recurring problem when running an MCP server in a regulated domain. See [Pattern Index](../patterns/INDEX.md).

**Path A / B / C** — In Pattern 01, three configurations for handling MCP session continuity on Cloud Run: (A) single-instance pinning, (B) Cloud Run-native sticky sessions with warm baseline, (C) externalized session state via shared store.

## R

**`readOnlyHint`** — MCP tool annotation. True if the tool only reads data and produces no side effects.

**RFC 2119** — The IETF specification defining `MUST`, `SHOULD`, and `MAY` as conformance language. Used in `OPERATIONS.md` and `cookbook-strategy-principles.md`.

**RLS** — Row-Level Security. PostgreSQL's per-row access-control mechanism, used in Pattern 04 as the database-layer enforcement for tenant isolation.

## S



**SEP** — Specification Enhancement Proposal. The formal mechanism for proposing changes to the MCP specification.

**`sessionAffinity`** — A Cloud Run service-level annotation (`run.googleapis.com/sessionAffinity: "true"`) enabling cookie-based pinning of session traffic to a single instance. Central to Pattern 01 Path A and B.

**SSW / 特定技能** — Specified Skilled Worker, a Japanese visa category. Sugukuru's primary domain.

**Streamable HTTP** — The stateful HTTP transport defined in the MCP specification, as opposed to stdio or stateless modes.

**Sugukuru / `sugukuru-core` / `sugukuru-finance` / `sugukuru-crm` / `sugukuru-hub` / `sugukuru-comms`** — Sugukuru Inc.'s MCP fleet and supporting services. See `gcp-verified-facts.md` §1.

**`suguvisa-mcp`** — A separate TypeScript MCP project at https://github.com/sugukurukabe/suguvisa-mcp, in a separate GCP project. Out of scope for the current cookbook; anticipated to be Case Study #02 after a planned mid-2026 corporate split.

## T

**Truth precedence rule** — `OPERATIONS.md` Section C.1's ten-level ordering of evidence sources, used to resolve conflicts between claims. Live GCP state is highest; human recollection is lowest.

## V

**Vertex AI Search** — Google Cloud's enterprise search service. Used by `sugukuru-hub` (not by the MCP servers themselves).

## W

**WG / IG** — Working Group / Interest Group, structures within the MCP community for collaborative spec development.
