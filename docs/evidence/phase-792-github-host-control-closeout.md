# Phase #792 GitHub Host Control Closeout Basis

## Scope

This evidence closes the retained #792 GitHub issue / Project / PR host control plane scope:

- GitHub issue intake and routing: #793 / #794.
- GitHub native dependency read, drift, sync-plan, gate, and capability detection: #826 / #828 / #831 / #832 / #833.
- Layered local and CI check profiles retained in #792: #872 / #953.
- Phase closeout evidence carrier: #812.

GitHub issue, Project, PR, required checks, branch protection, and native dependency edges remain host-control mirrors. They do not replace repo-authored truth.

## Closeout Basis

- `github-intake issue` provides a read-only GitHub issue entrypoint with object classification, route, host binding inspection, dependency graph, Project drift, and provenance.
- Native dependency reads prefer GraphQL `blockedBy` / `blocking`, report `read-only` or `read-write` capability, and expose unreadable host mirrors instead of treating them as clear.
- Safe sync plans now include dry-run native dependency actions for mechanically proven `missing_native_edge` and stale closed-blocker `stale_native_edge`, with proof source and verification step.
- `flow resume` and `flow merge-ready` can consume native dependency state without requiring a Project read; closeout blocks on open blocker or stale dependency mirror.
- `loom_check --profile source --source-surface ...` separates contract-only, source-self-fixture, bootstrap-regression, and distribution-regression surfaces while preserving full source self-check as the default.

## Validation Commands

Validated locally during PR preparation:

```bash
python3 -m py_compile src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_check.py skills/shared/scripts/loom_check.py
python3 tools/loom_flow.py github-intake issue --target . --issue 794 --phase 792 --fr 793
python3 tools/loom_flow.py flow resume --target . --issue 828
python3 tools/loom_flow.py governance-profile upgrade-plan --target . --host github --issue 833
python3 tools/loom_check.py --profile source --source-surface contract-only .
python3 tools/loom_check.py --profile source --source-surface bootstrap-regression .
python3 tools/loom_check.py --profile source --source-surface distribution-regression .
python3 tools/loom_check.py --profile source --source-surface source-self-fixture .
python3 tools/check_loom_check_runtime_regressions.py
python3 tools/loom_check.py --profile consumer examples/new-project
python3 tools/loom_check.py --profile source .
```

Expected live host observations:

- #794 is classified as `work_item`.
- #794 currently reports an open native blocker from #793, proving intake blocks rather than guessing.
- Native dependency capability for this repository reports `read-write`.
- `contract-only`, `bootstrap-regression`, `distribution-regression`, `source-self-fixture`, and full source surfaces complete with visible step progress and no failures.

## Rollback Basis

- Revert the implementation PR to remove `github-intake`, native dependency sync-plan actions, dependency gate consumption, and source-surface selection together.
- If a native dependency write is ever applied from a safe sync plan, use the paired rollback note in the planned action and re-read `blockedBy` / `blocking` to verify.
- If source-surface splitting causes CI drift, keep `--profile source` defaulting to `full` and temporarily pin closeout callers to `--source-surface contract-only` while restoring the affected surface.

## Remaining Risk

- GitHub native dependency availability is host/API dependent; unsupported or permission-denied hosts remain explicit gaps, not passes.
- Project item reconciliation must still be verified against live Project state before #812 and #792 are closed.
- Full source self-check remains intentionally heavier than closeout contract checks; release readiness should still run full or explicit regression surfaces.
