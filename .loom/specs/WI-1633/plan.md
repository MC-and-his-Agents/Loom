# WI-1633 Plan Boundary

- WI-1633 is a bounded PR4 CLI surface cleanup Work Item for issues #1633/#1639, with implementation scope already limited by the Work Item carrier, build evidence, and the formal suite path decision in `.loom/specs/WI-1633/spec.md`.
- No separate multi-phase implementation plan is required because this PR removes old root `loom` command surfaces and repo-local write paths, then verifies the resulting CLI surface through targeted and aggregate contract checks.
- This file is a build-readiness locator only. It does not replace Work Item scope, build evidence, current-head review, PR body metadata/head binding, hosted checks readback, PR gate, release/no-release judgment, controlled merge, or closeout evidence.
- Require a concrete implementation plan if this PR expands into npm package payload changes, host verify global provider semantics, legacy residue gate behavior, migration playbook, release/tag/npm/GitHub Release mechanics, permissions, external-visible actions, PR5 work, or shared contract/failure vocabulary changes.
