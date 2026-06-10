# WI-1249 Plan

## Suite Contract

- Suite path consumed: minimal
- Spec locator: .loom/specs/WI-1249/spec.md
- Plan locator: .loom/specs/WI-1249/plan.md
- Implementation contract locator: .loom/specs/WI-1249/implementation-contract.md
- Full-path artifacts not_applicable: artifacts: contracts.md, readiness-checklist.md, research.md, suite-index.md; rationale: #1249 is a bounded runtime observability implementation with a fixed command inventory and focused validation evidence. consumer boundary: suite validate, review, merge-ready, PR gate, hosted CI, and closeout consume this minimal suite plus PR validation evidence. recheck condition: require full suite if this expands into validation mode taxonomy, cost/snapshot reuse, command membership changes, or adjacent Round 7 work.

## Steps

1. Read #1248 inventory and existing `daily-execution-cli` implementation surfaces.
2. Add stable per-sub-scenario start/progress/end evidence around the existing command batches.
3. Track elapsed timing, command result, failure count, and metadata for each labeled scenario.
4. Enrich failure details with scenario label, command, summary, and metadata.
5. Keep command membership and allowed result semantics unchanged.
6. Synchronize shared/runtime copies required by repo practice.
7. Run focused compile, skills, source merge-gate behavior, synthetic failure metadata, demo fixture, PR metadata, and hosted check validation.
8. Stop at scheduler-owned review/pr-gate/merge/closeout.

## Scenario Mapping

- S1 -> automated validation evidence: Steps 2, 3, and source merge-gate stderr evidence.
- S2 -> automated behavior evidence: Steps 2, 3, and command result metadata.
- S3 -> automated test evidence: Step 4 and synthetic failure metadata harness.
- S4 -> automated validation evidence: Steps 1, 5, and source merge-gate command inventory evidence.

## Acceptance Mapping

- AC-1 -> automated validation evidence: source merge-gate run observed `event=start/progress/end` labels for all 30 command inventory labels and fixture groups.
- AC-2 -> automated test evidence: synthetic failure metadata harness verified scenario, command, summary, and metadata.
- AC-3 -> behavior evidence: progress labels emitted during long-running source merge-gate execution.
- AC-4 -> automated validation evidence: #1248 command inventory remained covered by `tools/loom_check.py --profile source --source-surface merge-gate .`.
- AC-5 -> automated validation evidence: runtime copy compile checks, `make skills-check`, authorized demo fixture sync, and hosted demo/repo-local checks.

## Validation

- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py` on touched `loom_check.py` copies.
- `make skills-check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface merge-gate .`
- Synthetic failure metadata harness.
- `make loom-demo-new-project-check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py examples/new-project/.loom/bin/loom_check.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py fact-chain --target . --item WI-1249`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py flow review --target . --item WI-1249 --owner MC-and-his-Agents --repo Loom --issue 1249 --pr 1409 --branch work/1249-daily-cli-progress-timing`
- PR metadata preflight/readback compare after each pushed head.
- Hosted checks on PR #1409 current head.

## Constraints

- Do not change #1248 command membership.
- Do not convert required failures to advisory results.
- Do not implement #1252 source snapshot/bootstrap reuse or cost reduction.
- Do not split or rename #1250 fixture groups.
- Do not change #1251 fallback truth boundaries.
- Do not define #1253 fast/full entrypoint semantics.
- Do not run scheduler-owned semantic review, formal review, `loom-pr-merge-gate`, controlled merge, closeout, or issue closure.

## Ready For Review

- [x] Scope and non-goals are explicit.
- [x] Scenario and acceptance mapping are present.
- [x] Validation path is defined.
- [x] Adjacent Round 7 ownership boundaries are recorded.
- [x] Scheduler remains gate owner.
