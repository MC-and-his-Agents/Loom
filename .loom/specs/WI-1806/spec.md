# WI-1806 Spec

## Suite Path Decision

- Suite path: minimal
- Rationale: WI-1806 changes bounded CLI carrier composition, PR metadata consumption, and contract fixtures. A minimal suite covers the executable behavior without introducing a new operating-plane DSL.
- Consumer Boundary: suite validate, review, PR metadata, PR gate, merge-ready, and closeout may consume this minimal suite together with the focused CLI contract surfaces.
- Recheck Condition: Re-run py compile, pr-metadata, suite-contract, aggregate CLI contract, and diff checks after any change to profile definitions, metadata fields, changed-path scope policy, suite N/A semantics, or PR body carrier rendering.
- Scope Proof: `git diff origin/main...HEAD` must stay limited to `tools/loom.py`, `tools/check_cli_contract.py`, `docs/methodology/harness/cli-command-matrix.md`, and WI-1806 Loom carriers.
- Review Requirement: current_head_review_required
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: the public contract is the CLI prepare/check surface and PR metadata carrier consistency, both covered by focused executable fixtures. consumer boundary: suite validate, review, PR gate, merge-ready, release readiness, and closeout consume this as minimal suite evidence only. recheck condition: require full suite artifacts if the work expands into a new DSL, host mutation model, release automation rewrite, credentials, permissions, or cross-repo migration.

## Scenarios

- S1: `loom pr-intent prepare/check` exposes shared profiles for docs-governance-only, closeout-only, release-only, carrier-sync-only, and fixture-only PRs.
- S2: `loom docs-pr prepare/check` is a short path for the docs/governance-only profile.
- S3: suite N/A is a successful CLI result for the profiles that formally do not need suite artifacts, while review/gate/release/closeout evidence remains required.
- S4: profile checks fail closed on partial carriers, stale head SHA, manual PR body drift, cross-surface mismatch, and changed paths outside the declared profile.
- S5: release-only readiness can be prepared and checked without publishing `v0.22.0` while #1800 / `v0.21.2` owns the current release line.

## Acceptance

- [x] A1: Shared PR intent profile definitions drive carrier generation, metadata validation, head binding, scope proof, and carrier-set consistency.
- [x] A2: #1807 docs/governance-only, #1809 closeout-only, and #1810 docs-pr short path reuse the shared consistency layer.
- [x] A3: #1808 suite N/A exits successfully and is consumed by docs/governance-only and closeout-style profiles without bypassing other gates.
- [x] A4: #1812 release-only, #1813 carrier-sync-only, and #1814 fixture-only prepare/check paths reuse the shared foundation.
- [ ] A5: PR review, merge-ready, and #1806 closeout consume current-head PR metadata and Loom carriers.
- [ ] A6: #1815 `v0.22.0` release evidence, metadata, package readback, and closeout complete after #1800 / `v0.21.2` releases or explicitly frees the release line.
