# WI-1690 Spec

## Suite Contract

- Suite path: minimal
- Suite index locator, or N/A rationale: `.loom/specs/WI-1690`
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1690 is a bounded root CLI dry-run wrapper change over existing metadata, PR gate, merge check, and closeout policy surfaces rather than a new workflow, release, or host-write design. consumer boundary: suite validate, review, PR gate, controlled merge, and closeout may consume this minimal spec, plan, evidence map, task carrier, and focused validation output. recheck condition: require full suite artifacts if scope expands into `loom ship --apply`, new host mutation behavior, release packaging, or public workflow design.
- Consumes:
  - Work Item / FR locator: issue #1690 under FR #1689
  - Story Readiness confirmed locator, blocking locator, or N/A rationale: N/A; #1690 is a bounded CLI orchestration Work Item produced by milestone #15 planning.
  - Story scenario locator, or N/A rationale: N/A; scenarios are authored below.
  - Story Business Confirmation confirmed locator, blocking locator, or N/A rationale: N/A; no product-domain business semantics change.
- Produces:
  - Scenario ids / locators: S1-S3
  - Acceptance ids / locators: A1-A5
  - Behavior evidence expectation: `loom ship` dry-run explains delivery steps and closeout policy without mutating host or repo state.
- Locator:
  - Spec locator: `.loom/specs/WI-1690/spec.md`
- Provenance:
  - Source issue / PR / doc / conversation locator: GitHub issue #1690
  - Freshness rule: Recheck before review, PR metadata, PR gate, controlled merge, and closeout consume this Work Item.

## Goal

- Add a root CLI `loom ship` dry-run entry that shows the intensity-aware delivery path for a PR.
- Keep #1690 non-mutating: dry-run may read metadata, PR gate, merge check, and closeout policy, but must not merge, close issues, write GitHub, or write repo carriers.

## Scope

- In scope:
  - Register `loom ship` in the root CLI command surface.
  - Add dry-run planning across PR metadata preflight, PR gate, controlled merge check, and closeout policy selection.
  - Explain skipped steps, upgrade reasons, and next action in a compact JSON payload.
  - Add focused CLI contract coverage proving dry-run delegates only read-only checks.
- Out of scope:
  - Implementing `loom ship --apply`; that is owned by #1691.
  - Adding `controlled-merge --closeout-run`; that is owned by #1692.
  - Publishing the milestone release; that is owned by #1696.
  - Writing host state, closing issues, creating closeout PRs, or mutating repo carriers from `ship` dry-run.

## Key Scenarios

### Scenario S1

Given a PR has usable Loom metadata and the user runs `loom ship --item <id> --pr <n> --intensity auto --json`

When the dry-run evaluates the delivery path

Then the output includes PR metadata preflight, PR gate, controlled merge check, closeout policy, skipped post-merge closeout, and a next action.

### Scenario S2

Given a light-intensity docs or governance item does not require release or versioned carrier closeout

When `loom ship` computes closeout policy

Then it selects host-only or inline closeout behavior and does not create a closeout PR by default.

### Scenario S3

Given the user passes `--apply` during #1690

When `loom ship` handles the request

Then it fails closed with a non-mutating blocker and points to #1691 instead of delegating a write path.

## Behavior Evidence

- Story scenario mapping: N/A; scenarios S1-S3 are authored in this spec.
- Story readiness locator or N/A rationale: N/A; issue #1690 is already scoped and accepted as a milestone #15 Work Item.
- Story business confirmation locator or N/A rationale: N/A; no product-domain business semantics change.
- Scenario coverage:
  - S1 -> `tools/check_cli_contract.py --surface ship-wrapper`
  - S2 -> `tools/check_cli_contract.py --surface ship-wrapper`
  - S3 -> `tools/check_cli_contract.py --surface ship-wrapper`
- Expected evidence locator: `.loom/specs/WI-1690/evidence-map.md`
- Freshness rule: Refresh validation after changes to `tools/loom.py`, `tools/check_cli_contract.py`, or WI-1690 carriers.
- Execution ledger acceptance locator: `.loom/progress/WI-1690.md`
- N/A rationale, if this is not a behavior-bearing change: N/A; this is a root CLI behavior change.

## Exceptions And Boundaries

- Failure modes: dry-run delegates a mutating flag, closeout policy hides an upgrade reason, `--apply` performs writes, or output loses next action guidance.
- Operational boundaries: `loom ship` may summarize the delivery plan; it must not change delegated gate results.
- Rollback or fallback expectations: users can continue invoking existing `pr-metadata`, `pr-gate`, `merge check`, and closeout commands directly.

## Acceptance Criteria

- [x] A1: `loom ship` appears in the root CLI command surface.
- [x] A2: dry-run delegates PR metadata preflight, PR gate, and controlled merge check in read-only mode.
- [x] A3: dry-run emits closeout policy with skipped post-merge closeout and next action.
- [x] A4: light-intensity policy does not create a closeout PR by default.
- [x] A5: `loom ship --apply` fails closed in #1690 without delegated writes.
