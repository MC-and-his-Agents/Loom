# WI-1116 Spec

- Suite path: minimal
- Work Item: WI-1116

## Goal

Implement full suite scaffold generation for `loom suite scaffold --suite full`.

## Scope

- Keep `loom suite scaffold` dry-run behavior read-only by default.
- Preserve the minimal suite scaffold contract for `spec.md` and `plan.md`.
- Allow `loom suite scaffold --suite full` to plan and, with `--apply`, create the standard full suite scaffold artifacts under `.loom/specs/<item>/`.
- Full suite scaffold artifacts are `suite-index.md`, `spec.md`, `plan.md`, `research.md`, `contracts.md`, and `readiness-checklist.md`.
- Preserve existing files and report only the locators actually created during the invocation.
- Classify `suite-index.md`, `spec.md`, and `plan.md` as required artifacts; classify `research.md`, `contracts.md`, and `readiness-checklist.md` as conditional artifacts.
- Retain fail-closed behavior before writes for invalid item values, symlink scaffold paths, and non-file artifact placeholders.
- Keep evidence-map, consistency-analysis, task-carrier, host writes, review writes, merge-ready writes, closeout writes, generated skills, spec-kit command names, and `.specify/` layout out of scope.

## Scenarios

### S1 Full Dry-Run Plans Standard Artifacts

Given a target repository and Work Item id,
When `loom suite scaffold --suite full --json` runs without `--apply`,
Then it reports the six full suite planned writes, marks required and conditional artifact sets, keeps `mutates: false`, and creates no files.

### S2 Full Apply Creates Missing Artifacts

Given a target repository with no existing full suite artifacts,
When `loom suite scaffold --suite full --json --apply` runs,
Then it creates the six standard full suite artifacts from Loom scaffold templates and returns those locators in `created_locators`.

### S3 Full Apply Preserves Existing Artifacts

Given a target repository where one or more full suite artifacts already exist,
When full scaffold apply runs,
Then it preserves existing files, creates only missing files, and returns only newly created locators.

### S4 Repeat Full Apply Is A No-Op

Given a target repository where all six full suite artifacts already exist,
When full scaffold apply runs again,
Then it reports `mutates: false`, preserves all files, and returns an empty `created_locators` list.

### S5 Unsafe Full Scaffold Paths Fail Closed

Given a traversal or absolute item value, a symlink in the scaffold path, or a non-file artifact placeholder,
When full scaffold apply runs,
Then it fails closed before writing any scaffold artifact and returns an empty `created_locators` list.

## Acceptance

- AC-1116-1: Minimal suite dry-run and apply behavior remains compatible with #1114 and #1115.
- AC-1116-2: Full suite dry-run is read-only and reports planned writes for exactly `suite-index.md`, `spec.md`, `plan.md`, `research.md`, `contracts.md`, and `readiness-checklist.md`.
- AC-1116-3: Full suite apply creates only missing full suite scaffold artifacts under `.loom/specs/<item>/`.
- AC-1116-4: Existing files are never overwritten, and repeat full suite apply returns no created locators.
- AC-1116-5: Full suite payload reports required artifacts, conditional artifacts, source template locators, preserve-existing overwrite policy, and actual `created_locators`.
- AC-1116-6: Invalid items, symlink paths, and non-file artifact placeholders fail closed before writes.
- AC-1116-7: The command does not introduce `/speckit.*`, `.specify/`, evidence-map, consistency-analysis, task-carrier, host, review, merge-ready, closeout, or generated skill mutation surfaces.
