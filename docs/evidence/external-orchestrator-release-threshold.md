# External Orchestrator Release Threshold

This file defines the v0.12.0 release threshold for external orchestrator interop.

External orchestrator interop is an `orchestration-extension/external-orchestrator`
profile. It is release-blocking only for its own extension scope; it does not turn
Loom into a default daemon or scheduler product.

## Required Evidence

Before v0.12.0 can close, the release candidate must show:

- `docs/methodology/harness/external-orchestrator-interop.md` defines Work Item read,
  workspace attach, recovery-only writeback, status/gate consumption, and truth
  boundaries.
- `docs/adoption/repo-interop-contract.md` exposes locator-only
  `external_orchestrators[*]` declarations with `status_read` and `gate_read`.
- `loom_status` exposes a read-only external consumer view that reuses
  `loom-governance-status/v2`, provenance, and the existing gate chain.
- `python3 tools/loom_flow.py live-smoke external-orchestrator-interop --target examples/new-project`
  emits `loom-external-orchestrator-conformance/v1`.
- `docs/evidence/fixtures/external-orchestrator-conformance-fixtures.json` covers
  happy path, truth pollution drift, scheduler-private fallback, and no-daemon /
  no-host-lifecycle ownership.
- `python3 tools/loom_check.py` validates the conformance fixtures and command
  contract.

## Release Interpretation

The release can pass when:

- required external orchestrator declarations fail closed on unreadable locators,
  truth pollution, private fallback, or lifecycle ownership drift
- optional/advisory locator gaps stay profile-local
- status and gates remain derived from Loom control planes
- writeback remains limited to recovery entry fields
- no daemon, scheduler state machine, tracker polling product, branch/PR/worktree
  ownership, worker lifecycle ownership, or second status surface is introduced

External orchestrator conformance does not require a real external scheduler for
v0.12.0. The fake external orchestrator fixtures are sufficient release evidence
because the release freezes the interop contract and boundaries, not a scheduler
implementation.
