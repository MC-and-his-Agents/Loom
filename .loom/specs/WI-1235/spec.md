# Spec

## Suite Contract

- Suite path: full
- Suite index locator, or `not required` rationale: .loom/specs/WI-1235/suite-index.md
- Consumes:
  - Work Item / FR locator: GitHub issue #1235; parent FR #1228
  - Story Readiness confirmed locator, blocking locator, or `not required` rationale: not required; GitHub issue #1235 is the executable Work Item.
  - Story scenario locator, or `not required` rationale: not required; scenarios below derive from issue #1235 acceptance criteria.
  - Story Business Confirmation confirmed locator, blocking locator, or `not required` rationale: not required; no external product/business semantics change.
- Produces:
  - Scenario ids / locators: S1, S2, S3 in this file.
  - Acceptance ids / locators: A1-A5 in this file.
  - Behavior evidence expectation: CLI JSON output and repo-local carrier diffs from focused fixtures.
- Locator:
  - Spec locator: .loom/specs/WI-1235/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: GitHub issue #1235; current Codex Round 9 goal.
  - Freshness rule: Recheck after repair CLI semantics, carrier write set, generated runtime sync, or issue acceptance changes.

## Goal

- Deliver a safe `loom repair plan/apply` flow that can terminalize a host-complete active Work Item carrier into repo-local idle state through reviewable diffs.
- Preserve strict ownership and fail-closed behavior so ambiguous retained-item matches, missing issue selectors, mismatched host locators, invalid carrier inputs, and mixed installed-surface repairs do not produce partial or misleading repair completion.

## Scope

- In scope:
  - Public `loom repair plan/apply` integration in `tools/loom.py`.
  - Shared runtime `repair plan/apply` implementation in `loom_flow.py`.
  - Repo-local updates to progress, status, and init-result carriers only when explicit apply succeeds.
  - Dry-run/non-mutating plan behavior.
  - Host readback through `gh api`; no host mutation actions.
  - Focused CLI contract fixtures and aggregate regression coverage.
  - Generated skills runtime sync.
- Out of scope:
  - #1236 fixture inventory expansion.
  - #1237 docs outline.
  - #1296 release/no-release closeout.
  - Round 10/11/deferred work.
  - Release, tag, npm publish, GitHub issue/project mutation by repair commands, and unrelated refactors.

## Key Scenarios

### Scenario S1

Given
- a repo-local active carrier points to a Work Item whose GitHub issue is closed/completed and PR is merged
- the caller supplies the matching `--issue`

When
- `loom repair plan --target <repo> --issue <n> --json` runs

Then
- it emits a non-mutating carrier closeout plan covering progress terminal metadata, idle status surface, and idle init-result fact-chain updates
- it reports `host_mutations: false` and an empty `host_actions` list.

### Scenario S2

Given
- the same host-complete active carrier

When
- `loom repair apply --target <repo> --issue <n> --dry-run --json` runs

Then
- it returns planned versioned carrier updates without changing files.

When
- `loom repair apply --target <repo> --issue <n> --json` runs and all carrier inputs are valid

Then
- it writes only repo-local progress/status/init-result carrier updates and the repo fact-chain reads back as idle.

### Scenario S3

Given
- the carrier ownership or write set is ambiguous, mismatched, missing an issue selector, has multiple issue locators, has invalid init-result input, or repair plan also contains installed-surface repair actions

When
- repair plan/apply runs

Then
- the command fails closed before unsafe mutation and exposes actionable missing inputs.

## Behavior Evidence

- Story scenario mapping: S1-S3 map to `assert_repair_apply_carrier_closeout_contract` in `tools/check_cli_contract.py`.
- Story readiness locator or `not required` rationale: not required; issue #1235 is the executable Work Item.
- Story business confirmation locator or `not required` rationale: not required; no business/product semantic decision.
- Scenario coverage:
  - S1 -> `python3 tools/check_cli_contract.py --surface governance-closeout`
  - S2 -> `python3 tools/check_cli_contract.py --surface governance-closeout`
  - S3 -> `python3 tools/check_cli_contract.py --surface governance-closeout`
- Expected evidence locator: .loom/specs/WI-1235/evidence-map.md
- Freshness rule: Rerun after any repair CLI, host truth, carrier write, generated runtime, or test fixture change.
- Execution ledger acceptance locator: GitHub issue #1235

## Exceptions And Boundaries

- Failure modes: missing `--issue`, ambiguous retained item matches, current item mismatch, multiple GitHub issue locators, host truth errors, incomplete host truth, missing terminal metadata, invalid init-result, and mixed installed-surface repair actions.
- Operational boundaries: repair commands may read host truth but must not close issues, update projects, push commits, tag releases, or publish packages.
- Rollback or fallback expectations: revert repo-local carrier diffs or use manual carrier closeout review; installed-surface repair remains blocked unless separately handled.

## Acceptance Criteria

- [x] A1: Host-complete active carrier can be moved to terminal/idle through explicit apply and reviewable diffs.
- [x] A2: Plan and dry-run remain non-mutating.
- [x] A3: Ambiguous ownership, missing issue selector, multi-issue locators, invalid carrier input, and mixed repair actions fail closed.
- [x] A4: Validation evidence is identified and present in `governance-closeout` and aggregate CLI contracts.
- [ ] A5: PR review, merge-ready, merge commit, issue CLOSED/COMPLETED, and closeout readback are pending host actions.

