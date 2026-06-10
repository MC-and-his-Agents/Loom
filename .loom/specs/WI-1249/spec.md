# WI-1249 Spec

## Suite Contract

- Suite path: minimal
- Work Item / issue locator: #1249
- Path decision provenance: #1249 is a bounded runtime observability slice for `daily-execution-cli` under the #1248 regression-surface inventory.
- Full-path artifacts not_applicable: artifacts: contracts.md, readiness-checklist.md, research.md, suite-index.md; rationale: this Work Item has a concrete issue, a fixed command inventory from #1248, implementation evidence in `loom_check.py`, and focused validation output. The minimal suite is sufficient to state the behavior, plan, and implementation boundary without duplicating the command inventory. consumer boundary: suite validate, review, merge-ready, PR gate, hosted CI, and closeout may consume this minimal suite plus PR validation evidence. recheck condition: require a full suite if #1249 expands beyond progress/timing/failure evidence, changes command membership, changes CI workflow semantics, introduces snapshot/bootstrap reuse or cost optimization, or absorbs #1250/#1251/#1252/#1253/#1254/#1247 scope.

## Goal

Make `daily-execution-cli` observable while it runs so operators can identify the active sub-scenario, elapsed timing, result, and failure location without waiting for the full step to finish.

## Scope

In scope:

- Emit stable `daily-execution-cli` sub-scenario `event=start`, `event=progress`, and `event=end` evidence.
- Include scenario label, command, elapsed timing, outcome/result, failure count, and relevant metadata.
- Enrich failure records with scenario label, command, concise summary, and metadata.
- Preserve command membership and required coverage from `docs/evidence/regression-surface-inventory.md` section `#1248 Daily Execution CLI`.
- Keep generated/shared runtime copies aligned where repo practice requires parity.

Out of scope:

- #1252 snapshot/bootstrap reuse or cost reduction.
- #1250 review-run fixture group splits or renames.
- #1251 Codex App fallback boundary changes.
- #1253 fast/full validation entrypoint semantics.
- #1254/#1247 parent or global milestone closeout.
- Guardian, formal review, controlled merge, closeout, or issue closure.

## Scenarios

### Scenario S1

Given `daily-execution-cli` runs the source merge-gate surface
When a sub-scenario or command batch starts, progresses, and ends
Then stderr includes stable labels with `event=start`, `event=progress`, and `event=end`.

### Scenario S2

Given a labeled sub-scenario completes
When evidence is emitted
Then the output includes elapsed timing, result/outcome, command evidence, failure count, and relevant metadata.

### Scenario S3

Given a labeled sub-scenario fails
When the failure is recorded
Then failure metadata identifies the scenario label, command, concise summary, and relevant metadata.

### Scenario S4

Given the #1248 `daily-execution-cli` command inventory
When #1249 observability is added
Then command membership and required coverage are preserved.

## Acceptance Criteria

- AC-1: Each meaningful `daily-execution-cli` subgroup emits start, progress, end, elapsed timing, and result evidence.
- AC-2: Failure details include scenario label, command, concise summary, and relevant metadata.
- AC-3: The source merge-gate validation no longer has long silent periods that resemble a hang.
- AC-4: The #1248 command inventory remains covered without weakening required failures into advisory results.
- AC-5: Shared/runtime copies and demo fixture runtime parity are synchronized where repo tooling requires them.

## Evidence Expectations

- `git diff --check`
- Focused `py_compile_clean` for touched `loom_check.py` copies.
- `make skills-check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface merge-gate .`
- Synthetic failure metadata harness.
- `make loom-demo-new-project-check`
- PR metadata preflight/readback and hosted checks on the current PR head.
