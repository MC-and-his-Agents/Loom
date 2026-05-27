# WI-1110 Spec

- Suite path: minimal
- Work Item: WI-1110

## Goal

Expose read-only suite path and artifact inventory locator reporting through `loom suite inspect`.

## Scope

- Detect explicit suite path decisions from repo-local suite artifacts.
- Report repo-relative locators for present suite artifacts.
- Report missing expected locators for explicit minimal and full paths.
- Keep `suite inspect` read-only and non-authoritative.

## Scenarios

### S1 Unknown Suite

Given a target has no explicit suite path decision,
When `loom suite inspect --json` runs,
Then the payload reports `suite_path: unknown`, `missing_inputs: ["suite_path_decision"]`, and no mutation.

### S2 Minimal Suite Locators

Given a target has an explicit minimal suite path and `spec.md` plus `plan.md`,
When `loom suite inspect --json` runs,
Then the payload reports `suite_path: minimal` and repo-relative `spec.md` / `plan.md` locators.

### S3 Full Suite Locators

Given a target has a full suite index and optional suite artifacts,
When `loom suite inspect --json` runs,
Then the payload reports `suite_path: full` and repo-relative locators for present suite artifacts.

### S4 Missing Expected Artifact

Given a target has an explicit full or minimal path with a required artifact absent,
When `loom suite inspect --json` runs,
Then the payload reports the missing repo-relative locator without deciding readiness.

## Acceptance

- AC-1110-1: artifact inventory locators are repo-relative and never durable absolute paths.
- AC-1110-2: unknown path behavior from #1109 remains intact.
- AC-1110-3: inspect does not write files, host state, review truth, merge-ready truth, or closeout truth.
