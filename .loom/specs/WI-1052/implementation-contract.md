# WI-1052 Implementation Contract

## Contract Delta

This Work Item adds planning documentation only:

- `docs/methodology/harness/full-spec-suite-cli-surface.md`
- `docs/methodology/harness/README.md`
- `docs/methodology/harness/cli-command-matrix.md`
- `.loom/` fact-chain, spec, plan, and review records for #1052 gate binding

## Preserved Contracts

- #1014 delivery planning remains the source for Phase / FR / Work Item / PR planning.
- #1016 full/minimal spec suite remains the source for suite path and artifact semantics.
- #1017 task carrier remains the source for carrier types, status, locator, and truth protection.
- #1018 evidence-map and consistency-analysis remain the source for evidence and analysis semantics.
- #1019 gate-chain remains the source for review, merge-ready, controlled merge, and closeout consumption.
- #1020 route matrix, GitHub profile, and source/generated skill sync remain the source for scenario and generated-surface consumption.

## Explicit Non-Implementation Boundary

No production CLI code, generated skills code, package manifest, binary entry, or installed runtime command surface is changed by this Work Item.
