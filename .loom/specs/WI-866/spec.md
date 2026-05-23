# WI-866 Spec

## Acceptance

- Ordinary closeout defaults to a lightweight `closeout-contract` profile and does not implicitly run the full `loom_check`.
- Explicit heavy profiles remain available through `--gate-profile` and preserve their gate source.
- Closeout consumes retained review, validation summary, merge-ready attempt, PR head, host required checks, merge commit, target branch, and reconciliation evidence as backlink subchecks.
- Stale, mismatched, unreadable, or missing backlink evidence fails closed with the most specific fallback target.
- Generated `skills/` surfaces and the stable demo runtime reflect the canonical shared runtime changes.

## Non-Goals

- Do not change GitHub required checks, rulesets, ProjectV2, review engine behavior, or low-level host merge APIs.
- Do not make full `loom_check` a default ordinary closeout requirement.
- Do not close parent FR #866 without consuming PR, merge commit, target branch, Project, issue, and reconciliation evidence.
