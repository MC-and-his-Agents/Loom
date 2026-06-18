# WI-1512 Spec

## Suite Contract

- Suite path: minimal
- Consumes:
  - Work Item locator: `.loom/work-items/WI-1512.md`
  - GitHub issue locator: `https://github.com/MC-and-his-Agents/Loom/issues/1512`
  - Gate freeze producer: #1510 / `loom-gate-freeze/v1`
  - Failure classifier producer: #1513 / `loom-failure-classifier/v1`
  - Story Readiness: issue-graph provenance in #1512 and #1505.
  - Story Business Confirmation: issue-graph provenance in #1512 and #1505.
- Produces:
  - Hosted freeze admission payload: `loom-hosted-freeze-admission/v1`
  - CI workflow readback inputs for PR body and PR payload.
  - PR gate failure categories for hosted freeze admission and snapshot mismatch.
- Locator:
  - Spec locator: `.loom/specs/WI-1512/spec.md`
- Provenance:
  - Source issue: `https://github.com/MC-and-his-Agents/Loom/issues/1512`
  - PR locator: `https://github.com/MC-and-his-Agents/Loom/pull/1572`
  - Freshness rule: recheck when `pr-gate`, gate freeze payload fields, PR metadata readback, or hosted workflow inputs change.

## Goal

Hosted PR merge gate admission must recompute and consume the same freeze/readback inputs that local gate freeze uses, then fail closed when hosted PR body readback, retained snapshot metadata, or fact-chain carriers are stale.

## Suite Path

- Full-suite-artifacts not_applicable: rationale: WI-1512 is a bounded runtime/workflow hosted admission slice with deterministic fixture coverage and no product story, external business workflow, data migration, or closeout release behavior; consumer boundary: suite validate, spec review, implementation review, merge-ready, hosted CI, downstream #1532/#1533 closeout freeze consumers, and milestone closeout may consume the minimal suite plus Work Item evidence for hosted PR gate admission only; recheck condition: require full suite artifacts if scope expands into closeout profile semantics, one-shot closeout run orchestration, release/no-release behavior, security/privacy behavior, external host writes beyond PR readback, or a user-facing workflow.

## Scope

- In scope:
  - Add a hosted freeze admission step to runtime `pr-gate check`.
  - Allow `pr-gate check` to consume `--body-file`, `--compare-body-file`, and `--gate-freeze-snapshot-file`.
  - Expose the same hosted admission arguments through `tools/loom.py pr gate`.
  - Update `.github/workflows/pr-merge-gate.yml` to read back PR body/payload from GitHub and pass them to `pr-gate check`.
  - Add focused CLI contract fixture coverage for pass, PR body drift, and snapshot mismatch.
  - Refresh generated skill runtime copies and demo bootstrap runtime fixture.
- Out of scope:
  - Do not redefine `loom-gate-freeze/v1`; consume #1510 fields.
  - Do not rename #1513 classifier categories beyond adding hosted admission consumers.
  - Do not implement #1532/#1533 closeout freeze profiles or closeout-specific gates.
  - Do not implement #1555 one-shot post-merge closeout run.
  - Do not bypass fact-chain, review, PR metadata, or merge checkpoint requirements.

## Key Scenarios

### S1: Hosted PR gate recomputes current freeze inputs

Given a hosted PR gate run has a PR JSON payload and readback PR body for the current PR head,

When `pr-gate check` runs with hosted admission inputs,

Then it recomputes gate freeze inputs from the current checkout, consumes carrier refresh, shadow freshness, PR body pinning, review binding, and classifier output, and exposes `hosted_freeze_admission.result = pass`.

### S2: Hosted PR body drift fails closed

Given the PR body read back from GitHub no longer matches the expected rendered PR body for the same Work Item and head,

When hosted freeze admission runs,

Then `pr-gate check` blocks and reports readback drift through hosted freeze admission and failure classifier evidence.

### S3: Retained freeze snapshot mismatch fails closed

Given a retained `loom-gate-freeze/v1` snapshot is provided but its subject or snapshot id does not match hosted recomputation,

When hosted freeze admission compares it with the recomputed payload,

Then `pr-gate check` blocks with snapshot mismatch evidence and a refresh action.

## Behavior Evidence

- Scenario coverage:
  - S1 -> `tools/check_cli_contract.py` hosted freeze admission fixture pass case.
  - S2 -> `tools/check_cli_contract.py` hosted freeze admission PR body drift case.
  - S3 -> `tools/check_cli_contract.py` hosted freeze admission snapshot mismatch case.
- Expected runtime evidence:
  - PR #1572 hosted `loom-pr-merge-gate` run consumes PR body readback and emits hosted freeze admission evidence.
  - Local `pr gate` targeted run passes after WI-1512 carriers and review record are current.
- Freshness rule: rerun targeted pr-metadata fixture and PR gate readback after code, generated runtime, PR body, review record, or carrier changes.

## Exceptions And Boundaries

- Failure modes:
  - Missing or unreadable hosted snapshot blocks as `freeze_artifact_unreadable`.
  - Snapshot subject mismatch blocks as `hosted_snapshot_mismatch`.
  - PR body readback drift blocks via `pr_body_pin`/hosted admission evidence.
  - Fact-chain mismatch remains blocking; hosted admission must not silently switch Work Items.
- Operational boundaries:
  - Hosted admission is a consumer of freeze/readback inputs, not the authority that authors Work Item or closeout carriers.
  - Closeout-only PR surface semantics remain owned by #1532/#1533/#1534.
- Rollback expectation: remove hosted admission arguments and workflow readback wiring if hosted gate cannot consume the payload without blocking valid current-head PRs.

## Acceptance Criteria

- [x] A1: Runtime `pr-gate check` accepts hosted readback and snapshot inputs.
- [x] A2: `tools/loom.py pr gate` forwards hosted admission inputs.
- [x] A3: Hosted workflow passes PR payload and PR body readback to `pr-gate check`.
- [x] A4: Fixture coverage proves pass, body drift block, and snapshot mismatch block.
- [x] A5: Generated skill runtime copies and demo bootstrap runtime fixture are refreshed.
