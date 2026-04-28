# Contributing

Thanks for considering a contribution. This document describes how patterns and case studies enter the cookbook, and the standards they need to meet.

## Before you start

If you have not already, please read:

1. [`cookbook-strategy-principles.md`](cookbook-strategy-principles.md) — the editorial principles that govern what the cookbook publishes and how. In particular §2 (scope), §3 (editorial principles), and §6 (contribution acceptance).
2. [`OPERATIONS.md`](OPERATIONS.md) — the operational procedures contributors and reviewers follow. In particular Section B (chapter-authoring procedure) and Section C (fact-verification procedure).

The two files together define what acceptance looks like. This file is a shorter summary of the contribution flow itself.

## What we accept

We accept three kinds of contribution:

1. **Patterns** — reusable solutions to recurring problems running MCP servers in regulated domains. A pattern documents the problem, the forces involved, the solution, the trade-offs, when the pattern fails, and at least one real deployment that uses it.
2. **Case studies** — descriptions of a specific deployment, attributed or anonymized. A case study can validate an existing pattern or motivate a new one. It does not have to recommend anything.
3. **Reference material** — glossaries, decision trees, checklists, or evidence files. Reference material must be cited from at least one pattern or case study; we do not collect reference content for its own sake.

We do not accept:

- "Hello world" or onboarding tutorials. The official MCP documentation handles these.
- Patterns derived only from blog posts, conference talks, or LLM-generated content with no live-deployment grounding.
- Vendor marketing material.
- Patterns whose only deployment evidence is a hello-world demo.

## How a pattern enters the cookbook

```
Issue (Pattern Proposal) → Discussion → Draft PR → Review → Merge as `draft` → Field validation → Promotion to `stable`
```

### 1. File an issue

Use the [pattern proposal template](.github/ISSUE_TEMPLATE/pattern-proposal.yml). The template asks you to identify:

- The problem the pattern addresses
- The relevant MCP spec section
- Your current solution (this is the seed of the pattern)
- The deployment evidence that supports the solution
- Any corroborating links (SDK issues, prior writing, related patterns)

Pattern proposals that arrive as PRs without a prior issue may be redirected to file an issue first.

### 2. Discussion

Maintainers and other contributors discuss the proposal in the issue. The discussion typically resolves:

- Whether the proposal is in scope (per `cookbook-strategy-principles.md` §2)
- Whether the problem belongs in a new pattern or extends an existing one
- What spec sections are relevant
- Who else might have deployment evidence to corroborate

### 3. Draft PR

Once discussion converges, the proposer (or another contributor) opens a PR adding a draft pattern under `docs/patterns/NN-title.md`. Use [`docs/patterns/_TEMPLATE.md`](docs/patterns/_TEMPLATE.md) as the structural starting point.

The draft PR follows the chapter-authoring procedure in `OPERATIONS.md` Section B. In particular:

- Frontmatter must validate (see `scripts/validate_frontmatter.py` if available)
- Every numerical claim must be traceable to a verified source
- The "When this pattern fails" section is mandatory (falsifiability)
- Length: 3,000 words or fewer

### 4. Review

Reviewers check the PR against:

- **Concreteness**: A reader should be able to tell within thirty seconds whether their situation matches the pattern.
- **Falsifiability**: The pattern must say when it is the wrong answer.
- **Production grounding**: At least one real deployment, with operator participation in review.
- **Spec correctness**: Citations to the MCP specification must be accurate against the current `spec_version` declared in frontmatter.

Reviewers may request specific verifications against `gcp-verified-facts.md` or comparable evidence files.

### 5. Merge as `draft`

When the PR passes review, it merges with `status: draft` in the chapter's frontmatter. Draft chapters are publicly visible and citable, but readers should understand the chapter has not yet been validated by independent deployment.

### 6. Field validation

A draft pattern is field-validated when:

- A second live deployment (other than the originating one) confirms the pattern works as documented, or
- 30+ days pass without errata or correction issues being filed against the chapter.

### 7. Promotion to `stable`

Maintainers promote a draft to `stable` after field validation. Promotion is a small PR updating the `status` and `last_reviewed` fields and adding a changelog entry.

## How a case study enters the cookbook

Case studies follow a similar flow but with a simpler review surface:

```
Issue (Case Study Submission) → Acceptance discussion → PR → Review → Merge
```

### Case study attribution

Per `cookbook-strategy-principles.md` §5.2, case studies declare an attribution level:

- **Attributed**: The deploying organization is named. A maintainer or designated reviewer participates in chapter review.
- **Industry-attributed**: The industry and rough scale are named, but not the organization.
- **Anonymized**: Only the technical and regulatory shape of the deployment.

The cookbook accepts all three. We recommend `attributed` where possible because it gives readers more to evaluate.

## Reporting errata

If you find a factual error in any chapter, please open an issue with the `errata` label. Include:

- The specific claim that is incorrect
- The verified truth (with source)
- Which sections of which chapters reference the incorrect claim, if you have looked

We will record the correction in [`memo-errata.md`](memo-errata.md) and update the affected chapters via PR. See `OPERATIONS.md` Section C.3 for the discrepancy-resolution procedure.

## Code of conduct

All participation in this project is subject to our [Code of Conduct](CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contribution is licensed under [Apache 2.0](LICENSE), the cookbook's license. If your contribution requires a different license (uncommon), declare this in the chapter's frontmatter and we will discuss in review.
