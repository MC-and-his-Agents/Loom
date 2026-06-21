# WI-1691 Spec

## Suite Contract

- Suite path: minimal
- Suite index locator, or N/A rationale: `.loom/specs/WI-1691`
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1691 is a bounded root CLI wrapper apply-path extension over already-frozen ship dry-run, controlled-merge, reconciliation, closeout, and closeout policy surfaces. consumer boundary: suite validate, review, PR gate, controlled merge, and closeout may consume this minimal spec, plan, evidence map, task carrier, and focused validation output. recheck condition: require full suite artifacts if scope expands into runtime controlled-merge closeout-run, release publishing, new policy semantics, or a new host-write adapter.
- Consumes:
  - Work Item / FR locator: issue #1691 under FR #1689
  - Story Readiness confirmed locator, blocking locator, or N/A rationale: N/A; #1691 is a bounded CLI Work Item produced by milestone #15 planning.
  - Story scenario locator, or N/A rationale: N/A; scenarios are authored below.
  - Story Business Confirmation confirmed locator, blocking locator, or N/A rationale: N/A; no product-domain business semantics change.
- Produces:
  - Scenario ids / locators: S1-S4
  - Acceptance ids / locators: A1-A5
  - Behavior evidence expectation: `loom ship --apply` performs the shortest legal merge-and-host-closeout path for eligible work without creating a closeout PR by default.
- Locator:
  - Spec locator: `.loom/specs/WI-1691/spec.md`
- Provenance:
  - Source issue / PR / doc / conversation locator: GitHub issue #1691
  - Freshness rule: Recheck before review, PR metadata, PR gate, controlled merge, and closeout consume this Work Item.

## Goal

- Add a root CLI `loom ship --apply` entry that turns a passing `loom ship` plan into a controlled merge followed by host closeout.
- Keep closeout policy visible: only inline / host-only policies can use the default apply path; carrier or full closeout PR policies fail closed to explicit closeout paths before merge.

## Scope

- In scope:
  - Add apply-path orchestration in `tools/loom.py`.
  - Run safe PR metadata repair when explicit issue, branch, and head inputs make it deterministic.
  - Preserve read-only gate sequence before any merge execution.
  - Execute controlled merge with `--execute` only after metadata, PR gate, merge check, and closeout policy pass.
  - After merge, run host reconciliation sync and final closeout check for eligible host-only / inline policies.
  - Add focused wrapper contract coverage for pass and blocker paths.
- Out of scope:
  - Adding `controlled-merge --closeout-run`; that is owned by #1692.
  - Updating README, skills, or fixtures to document the new primary path; that is owned by #1694.
  - Publishing the milestone release; that is owned by #1696.
  - Creating closeout PRs by default or writing versioned repo carrier closeout from `ship --apply`.

## Key Scenarios

### Scenario S1

Given a PR has valid Loom metadata, review, merge checks, and light closeout policy

When the user runs `loom ship --item <id> --issue <n> --pr <n> --apply --json`

Then the command applies safe PR metadata repair, executes controlled merge, runs host reconciliation, runs final closeout check, and reports `creates_closeout_pr=false`.

### Scenario S2

Given PR gate blocks before merge

When `loom ship --apply` evaluates the path

Then it reports the first blocker and does not execute controlled merge or closeout mutation.

### Scenario S3

Given closeout policy requires a carrier PR or full closeout PR

When `loom ship --apply` evaluates the path

Then it fails closed before merge and points to the explicit closeout queue/full closeout path.

### Scenario S4

Given target branch is not readable from controlled merge check or explicit input

When `loom ship --apply` evaluates the path

Then it fails closed before merge because post-merge closeout cannot be bound.

## Behavior Evidence

- Story scenario mapping: N/A; scenarios S1-S4 are authored in this spec.
- Story readiness locator or N/A rationale: N/A; issue #1691 is already scoped and accepted as a milestone #15 Work Item.
- Story business confirmation locator or N/A rationale: N/A; no product-domain business semantics change.
- Scenario coverage:
  - S1 -> `tools/check_cli_contract.py --surface ship-wrapper`
  - S2 -> `tools/check_cli_contract.py --surface ship-wrapper`
  - S3 -> `tools/loom.py` policy admission and implementation review
  - S4 -> `tools/loom.py` target-branch admission and implementation review
- Expected evidence locator: `.loom/specs/WI-1691/evidence-map.md`
- Freshness rule: Refresh validation after changes to `tools/loom.py`, `tools/check_cli_contract.py`, or WI-1691 carriers.
- Execution ledger acceptance locator: `.loom/progress/WI-1691.md`
- N/A rationale, if this is not a behavior-bearing change: N/A; this is a root CLI behavior change.

## Exceptions And Boundaries

- Failure modes: apply path merges before gate pass, hides closeout policy escalation, creates a closeout PR by default, writes versioned carrier closeout without explicit policy, or loses host closeout readback.
- Operational boundaries: `loom ship --apply` may orchestrate existing gate and host closeout actions; it must not redefine controlled merge, review, reconciliation, or closeout truth.
- Rollback or fallback expectations: users can continue invoking existing `pr-metadata`, `pr-gate`, `merge run --apply`, `reconciliation sync`, and `closeout check` commands directly.

## Acceptance Criteria

- [x] A1: `loom ship --apply` no longer fail-closes as unimplemented.
- [x] A2: apply mode preserves metadata preflight, PR gate, and controlled merge check before controlled merge execution.
- [x] A3: apply mode executes controlled merge with `--execute` and never passes `--apply` to controlled merge runtime.
- [x] A4: eligible light/inline closeout policy performs host reconciliation and final closeout check without creating a closeout PR.
- [x] A5: gate blockers and closeout policy escalation stop before merge.
