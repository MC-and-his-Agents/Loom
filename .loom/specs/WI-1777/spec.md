# WI-1777 Spec

## Suite Path Decision

- Suite path: minimal
- Rationale: WI-1777 is a focused CLI behavior slice that adds read-only `loom ship status` / `loom ship preflight` diagnostics on top of existing ship delivery logic. It does not need a full research/contracts suite because #1774 already freezes the product direction and this PR owns one bounded command surface plus regression coverage.
- Consumer Boundary: suite validate, implementation review, PR metadata, hosted checks, PR gate, controlled merge, closeout sync, and downstream #1775 may consume this minimal suite without treating skipped full-path artifacts as completed.
- Recheck Condition: Require full suite artifacts if this work expands into mutating closeout sync, release verdict taxonomy, PR metadata race handling, merge fallback behavior, publishing, credentials, or cross-command orchestration.
- Scope Proof: Changes are limited to `tools/loom.py`, `tools/check_cli_contract.py`, WI-1777 carriers, and `.loom/specs/WI-1777`.
- Review Requirement: current_head_review_required
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1777 is a bounded read-only CLI status/preflight slice with direct fixture coverage and no new external write authority. consumer boundary: suite validate, implementation review, PR metadata, hosted checks, PR gate, controlled merge, closeout sync, and #1775 may consume this minimal suite without requiring the skipped full-path artifacts. recheck condition: require full suite artifacts if the work expands into mutating closeout sync, release verdict taxonomy, PR metadata race handling, merge fallback behavior, publishing, credentials, or cross-command orchestration.

## Scenarios

- S1: A clean status readback with no release/tag/npm conflict and terminal carrier state passes and points to the normal ship dry-run/apply path.
- S2: A checkout whose HEAD differs from `origin/main` reports `checkout_stale_against_origin_main` and suggests recreating or fast-forwarding the worktree.
- S3: An already existing target tag, GitHub Release, or npm package blocks before release work and asks for release readback.
- S4: A closed host issue with an active `.loom/status/current.md` reports host/carrier drift and suggests `loom closeout sync` or carrier closeout sync.
- S5: `loom ship status` does not require or synthesize a PR binding.

## Acceptance

- [x] A1: `ship status` and `ship preflight` are first-class command matrix entries.
- [x] A2: command output includes blocked/fixed/next_action diagnostic data.
- [x] A3: checkout stale, release exists, and host-closed carrier-active drift are covered by fixture tests.
- [x] A4: command does not require a PR number.
- [x] A5: `ship-wrapper` contract, Python compile, and `git diff --check` pass.
