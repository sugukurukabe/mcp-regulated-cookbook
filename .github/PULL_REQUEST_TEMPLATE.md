## What this PR does

<!-- One or two sentences. -->

## Type of change

- [ ] New pattern (`docs/patterns/NN-title.md`)
- [ ] New case study (`docs/case-studies/NN-title.md`)
- [ ] Pattern revision (existing pattern, version bump)
- [ ] Case study revision
- [ ] Errata correction (filing fix; updating `memo-errata.md` accordingly)
- [ ] Operations / governance change (`OPERATIONS.md`, `cookbook-strategy-principles.md`, `CONTRIBUTING.md`, `MAINTAINERS.md`, `CODE_OF_CONDUCT.md`)
- [ ] Truth ledger update (`gcp-verified-facts.md`)
- [ ] Tooling (under `scripts/`)
- [ ] Other

## OPERATIONS.md compliance checklist

For chapter additions and revisions, please confirm:

- [ ] Frontmatter validates (`scripts/validate_frontmatter.py`).
- [ ] Every numerical claim is traceable to `gcp-verified-facts.md` or a cited source per `OPERATIONS.md` C.1.
- [ ] "When this pattern fails" section is present (patterns only; required per `cookbook-strategy-principles.md` §3.5).
- [ ] Length is within the limit: 3,000 words for patterns, 2,500 words for case studies.
- [ ] Changelog entry added at the bottom of the chapter, with today's date and a brief description.
- [ ] If any prior claim is contradicted by this PR, `memo-errata.md` is updated accordingly per `OPERATIONS.md` C.3.

## Linked issue

<!-- Reference the issue this PR resolves. Patterns generally come from a Pattern Proposal issue first. -->

Closes #

## Reviewer notes

<!-- Anything the reviewer should know to evaluate the PR efficiently. -->
