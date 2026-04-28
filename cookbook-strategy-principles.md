---
title: "Cookbook Strategy Principles"
status: living
version: 0.1.0
last_reviewed: 2026-04-28
audience: "public — anyone who reads, contributes to, or considers using the cookbook"
license: "Apache-2.0"
---

# Cookbook Strategy Principles

> **Purpose.** This file declares the principles that govern the `mcp-regulated-cookbook` project's editorial direction, contribution acceptance, and long-term coherence. It complements [`OPERATIONS.md`](./OPERATIONS.md), which governs procedure. Where OPERATIONS.md says *how*, this file says *why* and *what for*.
>
> **Conformance language.** This document uses MUST / SHOULD / MAY in the [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) sense.
>
> **How to read this.** New contributors and maintainers MUST read this file before submitting a pattern proposal or case study. Existing contributors SHOULD re-read it when proposing changes that touch the cookbook's scope, tone, or licensing.

---

## 1. The cookbook's reason for existing

The `mcp-regulated-cookbook` exists because the intersection of three conditions is currently underserved by the available MCP literature:

1. **Regulated business domains** — sectors where deployment decisions have legal, financial, or labor-law consequences. Immigration, healthcare, finance, labor, agriculture, education, public sector.
2. **Production operation** — running an MCP server long enough to encounter the failure modes that do not show up in tutorials.
3. **Reusable patterns** — knowledge structured so that another operator can apply it without re-doing the discovery work.

Tutorials cover #1 partially. Engineering blogs cover #2 partially. Vendor documentation rarely covers either. None of the three reliably produces #3.

The cookbook's job is to make the intersection navigable. Every chapter MUST contribute to that intersection or be rejected.

## 2. Scope rules

### 2.1 In scope [MUST]

A pattern or case study is in scope if it satisfies all of the following:

- It addresses a problem an operator running MCP in a regulated business domain will face.
- It is grounded in at least one live deployment whose operator participates in the chapter's review.
- The recommended solution is reproducible by another operator without proprietary tooling.
- The chapter cites the relevant MCP specification version explicitly.

### 2.2 Out of scope [MUST]

The cookbook MUST NOT publish:

- Tutorials for first-time MCP users. The official MCP documentation handles this.
- Vendor product comparisons. We document what we run; we do not rank what we don't.
- Speculation about future MCP features. Specs evolve; we document what works against shipped specs.
- Marketing material for any organization, including Sugukuru.
- Patterns that depend on a single vendor's proprietary extension.
- Patterns whose only deployment evidence is a hello-world demo.

### 2.3 Borderline cases [SHOULD]

Patterns that exist in live operation but whose operator declines to participate in review SHOULD NOT be published, to preserve the verification guarantee.

### 2.4 What "live deployment" means [MUST]

The cookbook MUST use "live deployment" or "live operation" to mean the deploying organization's own real business operations on real data, regardless of whether the organization sells the deployment as a product to external customers. Both internal-only operations (a small operator running their own business on the MCP fleet) and external-product deployments (a SaaS company selling MCP-based services) qualify as "live deployments" for cookbook purposes, as long as the deployment is processing real operational load.

The cookbook MUST NOT use "production" as a synonym for "live deployment", because "production" colloquially implies "external product" in some readings. Where a chapter needs to refer to a cloud-platform environment tier (e.g., "Cloud Run production traffic"), `production` is acceptable as a technical adjective for that tier; outside that narrow technical sense, prefer "live deployment" or "live operation". 

When a proposal sits on the boundary, the maintainers SHOULD apply the following test: *would a reader operating an MCP server in a regulated domain change something about their deployment after reading this chapter?* If yes, accept. If no, reject regardless of how technically interesting the chapter is.

## 3. Editorial principles

### 3.1 Honesty over polish [MUST]

Chapters MUST disclose what the operator does not know, has not measured, or got wrong. A chapter that hides uncertainty produces false confidence in readers, which is worse than a chapter that says "we ran this for five weeks and have not yet observed the failure mode this pattern protects against."

The companion file [`memo-errata.md`](./memo-errata.md) is the running record of claims this project has gotten wrong. Honesty about errata is part of the cookbook's product, not a defect.

### 3.2 Specificity over generality [MUST]

A chapter MUST cite specific platforms, SDK versions, configuration values, and error messages. "A serverless platform" is unacceptable; "Google Cloud Run with `min-instances: 0` and `containerConcurrency: 80`" is acceptable. The cookbook's value to readers comes from its specificity; generality is what they can already get elsewhere.

### 3.3 The "warning a colleague" tone [MUST]

Chapters MUST be written as if warning a colleague who is about to step on the same rake the author already stepped on. They MUST NOT be written as marketing material, evangelism, conference talks, or recruitment pitches.

Test: would the author's tone hold up if the reader is tired, frustrated, paged at 2 AM, and skeptical that the cookbook will help? If yes, the tone is correct.

### 3.4 Length discipline [MUST]

Patterns MUST be 3,000 words or fewer. Case studies SHOULD be 2,500 words or fewer; longer is acceptable when the case includes substantial numerical evidence that would lose meaning if compressed.

The discipline forces specificity. A 10,000-word chapter is rarely better than a 2,500-word chapter on the same topic; it is usually a 2,500-word chapter padded with material that should have been cut.

### 3.5 Falsifiability [MUST]

Every pattern MUST include a "When this pattern fails" section. A pattern with no documented failure mode is either incomplete or unfalsifiable; either way it is not ready for publication.

### 3.6 Self-application [SHOULD]

Where a pattern declares a rule that the cookbook itself can follow, the cookbook SHOULD follow it. Self-application produces tighter patterns and earlier discovery of pattern defects.

## 4. Language and accessibility

### 4.1 English-only publication [MUST]

The cookbook publishes in English only. Translation versions MUST NOT be merged into the published cookbook even when contributed in good faith. The reasons:

- The cookbook's target reader is technically literate in English (the language MCP itself, and most regulated-domain technical literature, is published in).
- Translation maintenance for a multi-author cookbook with frequent updates exceeds the maintainer capacity that exists or is forecast.
- Out-of-sync translations produce factual drift; an English-only cookbook with no translation drift is more reliable than a multilingual cookbook with stale translations.

### 4.2 Internal drafts [MAY]

Authors MAY draft in any language they prefer. Internal drafts in Japanese, Mandarin, German, etc., MAY exist outside the published `docs/` tree (for example in scratch files or private notebooks) and MAY be referenced during writing. Only the English version of a chapter is publishable.

### 4.3 Vocabulary care [SHOULD]

Authors SHOULD prefer terminology already used in the MCP specification over neologisms. Where a regulated-domain term has a precise legal meaning (e.g., "destructive operation" in the context of the Worker Dispatch Law), the chapter SHOULD use that term and define it in the [glossary](./docs/reference/glossary.md), rather than inventing a synonym.

## 5. Licensing and attribution

### 5.1 Apache 2.0 [MUST]

All code in the cookbook is licensed under Apache 2.0. All prose chapters and case studies are also Apache 2.0 unless an individual case study negotiates a different license at submission time (in which case the deviation is explicit in the case study's frontmatter).

The reasons for Apache 2.0:

- Permissive enough that enterprise readers can incorporate cookbook patterns into proprietary deployments without legal review of each chapter.
- Includes the patent grant, which CC-BY does not.
- Compatible with the MCP SDK licenses themselves.

### 5.2 Attribution levels [MUST]

Case studies declare an attribution level in their frontmatter:

- **`attributed`**: The deploying organization is named, and a contact (typically a maintainer) participates in review.
- **`industry-attributed`**: The deploying organization is described by industry and rough size ("a Japanese SSW dispatch operator with under 30 staff") but not named.
- **`anonymized`**: Identifying details are removed beyond reconstruction by readers, with the anonymization noted explicitly.

The cookbook accepts all three levels. `attributed` carries the most weight and is recommended where possible. `anonymized` is acceptable when the deploying organization's regulatory or competitive context makes naming infeasible.

### 5.3 Contributor recognition [SHOULD]

Every chapter SHOULD list its primary contributor in the frontmatter. Contributors MAY be listed by GitHub handle alone, or with affiliation. The maintainers SHOULD be transparent about who has reviewed which chapter when asked.

## 6. Contribution acceptance

### 6.1 Non-goals for the contribution process [MUST]

The cookbook MUST NOT operate as:

- A general issue tracker for upstream MCP SDKs. Issues belonging in `modelcontextprotocol/typescript-sdk` or `python-sdk` go there, not here.
- A speculation forum for future MCP features. Use MCP Discord and SEPs for that.
- A clearinghouse for vendor announcements. Vendors with patterns are welcome to contribute case studies under the rules in §5.2; vendor product launches are not.

### 6.2 Pattern proposal flow [SHOULD]

Pattern proposals SHOULD enter via the `pattern-proposal.yml` issue template. The template asks the proposer to identify the problem, the relevant spec section, the current solution, the deployment evidence, and corroborating links. Proposals that arrive as PRs without a prior issue MAY be redirected to file an issue first.

### 6.3 Case study acceptance [SHOULD]

Case studies SHOULD enter via the `case-study-submission.yml` issue template. The maintainers SHOULD acknowledge receipt within two weeks. Acceptance criteria are in §2.1. The cookbook does not promise to publish every submitted case study; it promises to give submitters honest reasons when not.

### 6.4 Maintainer expansion [SHOULD]

The cookbook is currently maintained by Sugukuru Inc. (primary maintainer: @sugukurukabe). The cookbook SHOULD welcome additional maintainers as the contributor base grows. Criteria for maintainer addition:

- The candidate has authored or substantively reviewed at least three published chapters.
- The candidate operates an MCP fleet in live operation, ideally in a regulated domain different from the existing maintainers' domain.
- The candidate agrees to the principles in this document.

The goal is not to keep maintenance concentrated, but to keep maintenance coherent. As long as additions improve coherence, the cookbook welcomes them.

## 7. Specification version policy

### 7.1 Target spec version [MUST]

The cookbook targets a single MCP specification version at any time. As of this writing the target is **2025-11-25**. Each chapter declares its target version in frontmatter (`spec_version`).

### 7.2 Version transitions [SHOULD]

When the MCP specification publishes a new version that the cookbook will adopt:

1. The maintainers SHOULD announce the transition window (typically 60–90 days).
2. Chapters SHOULD be reviewed and updated to the new version during the window.
3. Chapters not yet updated SHOULD be marked with their original target version visibly; readers can then judge applicability.
4. The cookbook does not promise to update every chapter to every new spec version. Old chapters under old spec versions are still useful as long as the spec version is documented.

### 7.3 Deprecated specs [MAY]

When a spec version becomes deprecated by upstream, chapters targeting it MAY be moved to an `archive/` tree rather than updated. The decision is per-chapter and depends on whether the pattern is still useful for operators on the older spec.

## 8. The cookbook's relationship with upstream

### 8.1 We document; we do not lobby [MUST]

The cookbook MUST NOT be used as a lever to pressure upstream MCP SDK maintainers into accepting changes the cookbook's maintainers prefer. Patterns that work *around* SDK gaps are documented as workarounds, with links to upstream issues; the upstream issues are where the lobbying belongs.

### 8.2 Spec proposals that emerge from cookbook patterns [SHOULD]

When a cookbook pattern repeatedly demonstrates that a piece of the spec is missing or unclear, the maintainers SHOULD file a Specification Enhancement Proposal (SEP) referencing the pattern as evidence. The SEP is the appropriate channel; the cookbook chapter is the supporting record.

### 8.3 Citations in the cookbook [SHOULD]

Chapters SHOULD cite upstream MCP specs, SDK source files (with line numbers), and SDK issues by URL. Where the cited resource is unstable (a moving HEAD branch, a frequently-rebased PR), the citation SHOULD include the date of access.

## 9. The cookbook's stance on related but separate projects

The cookbook is not the only place where MCP knowledge lives. Adjacent resources include:

- The official MCP specification and its appendices.
- Vendor-published reference implementations (Anthropic, Google, others).
- Engineering blog posts from individual operators.
- Community discussions on the MCP Discord and GitHub Discussions.
- Other cookbooks (the `anthropics/claude-cookbooks` for Claude API patterns, vendor-specific MCP integration guides).

The cookbook's relationship to these is **complementary, not competitive**. Readers benefit from cross-referencing. Chapters MAY cite adjacent resources when they extend or correct the cookbook's content; chapters MUST NOT disparage adjacent resources to elevate the cookbook's status. The cookbook's value comes from being good at what it covers, not from claiming others are bad at what they cover.

## 10. Document maintenance

This file's status MUST remain `living`. Substantive changes (additions or removals to the principles, changes from MUST to SHOULD or vice versa) MUST be reflected in the version field and recorded in the changelog. The `last_reviewed` field SHOULD be updated at minimum quarterly.

When this file disagrees with a published chapter, the disagreement MUST be resolved within one quarter, either by updating the chapter or by updating this file. Persistent disagreement is itself a defect.

## 11. Changelog

- **0.1.0** (2026-04-28) — Initial publication. Defines scope, editorial principles, language policy, licensing, contribution flow, spec version policy, upstream relationship, and stance on adjacent projects. Companion to `OPERATIONS.md` v0.1.0 and `gcp-verified-facts.md` v0.2.0.
- **0.2.0** (2026-04-28) — Removed §9 (cookbook-scout integration) prior to initial publication. The scout was a designed-but-not-implemented component that violated the cookbook's production-grounding principle (§2.1) and would have shipped as vaporware. Will be reintroduced in a future cookbook version after the scout is actually built, deployed, and produces its own grounded case study.
