# WI-1961 Spec

## Suite Contract

- Suite path: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1961 is the v0.28.0 gate stabilizer batch with a bounded implementation scope and is reviewable through this spec, plan, implementation contract, evidence map, task carrier, local targeted checks, PR metadata readback, and hosted checks; consumer boundary: suite validate, implementation review, PR metadata, hosted checks, PR gate, controlled merge, and issue closeout may consume this minimal suite without treating skipped full-path artifacts as completed; recheck condition: require full suite artifacts if this work expands into host tax core behavior, migration semantics, release publication, credentials, or external write automation outside PR metadata/profile validation.
- Consumes:
  - Work Item / FR locator: #1961 and #1963.
  - Story Readiness locator: not required because the accepted v0.28.0 milestone issue tree and user-provided temporary low-friction execution contract define this stabilizer batch; recheck if scope expands beyond PR metadata stability and host validation profiles.
  - Story scenario locator: not required; scenarios are defined below from #1961/#1963 and this thread's v0.28.0 execution strategy.
  - Story Business Confirmation locator: not required because this is internal delivery cost reduction governed by #1935/#1961/#1963; recheck if user-facing adoption semantics change outside the declared profile/metadata contract.
- Produces:
  - Scenario ids / locators: S1 authored PR head SHA removal, S2 digest-bound review summary, S3 host-consumer/carrier-only validation profile.
  - Acceptance ids / locators: A1-A5 below.
  - Behavior evidence expectation: targeted contract checks, aggregate CLI contract check, skills release-check, PR metadata readback, and hosted checks.
- Locator:
  - Spec locator: `.loom/specs/WI-1961/spec.md`
- Provenance:
  - Source issue / PR / doc / conversation locator: #1935, #1961, #1963, PR #1970, and the v0.28.0 temporary low-friction execution strategy from this thread.
  - Freshness rule: rerun targeted checks and refresh review/PR metadata after changes to PR metadata parsing, review disposition, validation profile routing, generated runtime copies, plugin payload metadata, or PR body machine carrier.

## Goal

Stabilize the gates that would otherwise make v0.28.0 pay the old Loom process tax on every PR.

After this change, PR metadata must not require an authored `head_sha` field, review validation summaries must be compared by stable digest/source/locator rather than fragile raw text, and `host-consumer` / `carrier-only` profiles must avoid source-repository validation checks.

## Scope

- In scope:
  - Remove `head_sha` from the repo PR metadata carrier contract and generated PR templates.
  - Keep PR head authority in host readback instead of authored PR body fields.
  - Bind semantic review validation summaries by digest/source/locator while keeping legacy exact-summary compatibility where needed.
  - Add `host-consumer` and `carrier-only` validation profile behavior to `loom ship`.
  - Update contract fixtures and targeted tests for the new stable PR metadata behavior.
  - Sync generated skill/runtime/plugin payload surfaces.
- Out of scope:
  - Default light-governance host mode.
  - Repo installed-state slimdown.
  - Global current pointer and runtime ledger.
  - Host-only closeout default.
  - Batch implementation/closeout semantics.
  - Host planning taxonomy mapping.
  - Existing host slim migration.
  - v0.28.0 release publication.

## Key Scenarios

### Scenario S1

Given a PR body contains Loom governance metadata for an implementation PR

When merge gate or metadata preflight reads the PR

Then it validates stable Work Item and branch bindings, reads the current PR head from GitHub host state, and does not require or compare an authored `head_sha` in the PR body.

### Scenario S2

Given a review artifact records the validation evidence for the current head

When PR gate consumes the semantic review disposition

Then it accepts a matching validation summary hash/source/locator and does not fail solely because equivalent validation text was formatted differently.

### Scenario S3

Given `loom ship` is evaluating a host repository or a carrier-only metadata path

When the selected validation profile is `host-consumer` or `carrier-only`

Then the plan does not schedule Loom source-repository checks that require source-only tools or repo-local shims.

## Behavior Evidence

- Story scenario mapping: #1961 maps to S1/S2; #1963 maps to S3.
- Story readiness locator: not required; v0.28.0 issue tree and thread strategy are the scope authority.
- Story business confirmation locator: not required; this is an internal process-cost stabilizer.
- Scenario coverage:
  - S1 -> `python3 tools/check_cli_contract.py --surface pr-metadata`, `--surface pr-gate-target-readback`, and PR #1970 metadata readback.
  - S2 -> `python3 tools/check_cli_contract.py --surface governance-closeout`, `--surface merge-wrapper`, and PR gate review consumption.
  - S3 -> `python3 tools/check_cli_contract.py --surface ship-wrapper`.
- Expected evidence locator: `.loom/progress/WI-1961.md` latest validation summary and PR #1970 checks.
- Freshness rule: refresh after any relevant code, fixture, generated runtime, plugin payload, PR body, review, or hosted check change.
- Execution ledger acceptance locator: `.loom/specs/WI-1961/plan.md#validation`.
- Behavior-bearing status: this change alters Loom gate/profile behavior, so no skipped behavior rationale is used.

## Exceptions And Boundaries

- Failure modes:
  - Hosted gate may still fail on stale current pointer or stale review artifact until this PR is consumed by the old flow once.
  - PR body edits do not trigger all hosted workflows, so failed runs from pre-repair metadata must be classified before rerun.
  - Renderer/update tooling may still overwrite human PR prose if it uses the template as the base body.
- Operational boundaries:
  - No WebEnvoy-specific taxonomy hardcoding.
  - No downstream repo-local `tools/loom.py` shim requirement.
  - No scope from #1957/#1958/#1959/#1960/#1962/#1964/#1965/#1966.
- Rollback or fallback expectations:
  - Revert PR metadata/profile changes together if gate behavior regresses.
  - Keep host readback as the head authority; do not restore authored PR body `head_sha`.

## Acceptance Criteria

- [x] A1: PR metadata no longer requires an authored `head_sha` field.
- [x] A2: PR metadata readback for PR #1970 passes with Work Item and branch bindings only.
- [x] A3: Review validation summary matching supports digest/source/locator.
- [x] A4: `host-consumer` and `carrier-only` profiles avoid source-repository validation commands.
- [x] A5: Targeted local contract checks and release-check pass before hosted rerun.
