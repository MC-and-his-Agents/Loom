# WI-1115 Spec

- Suite path: minimal
- Work Item: WI-1115

## Goal

Implement explicit repo-local writes for `loom suite scaffold --apply`.

## Scope

- Keep `loom suite scaffold` dry-run behavior read-only by default.
- Allow `loom suite scaffold --apply` to create missing minimal suite artifacts only: `.loom/specs/<item>/spec.md` and `.loom/specs/<item>/plan.md`.
- Preserve existing files and report only the locators actually created during the apply invocation.
- Fail closed before writes when `<item>` is not a single repo-local path segment or the scaffold path would traverse symlinks or non-file artifact placeholders.
- Keep full suite scaffold planning reserved for its later Work Item.
- Keep host truth, review truth, merge-ready truth, closeout truth, generated skills, spec-kit command names, and `.specify/` layout out of scope.

## Scenarios

### S1 Apply Creates Missing Minimal Artifacts

Given a target repository and Work Item id with no existing minimal suite artifacts,
When `loom suite scaffold --json --apply` runs,
Then it creates `.loom/specs/<item>/spec.md` and `.loom/specs/<item>/plan.md` from the Loom scaffold templates, reports `mutates: true`, and returns both locators in `created_locators`.

### S2 Apply Preserves Existing Artifacts

Given a target where one planned artifact already exists,
When apply scaffold runs,
Then it preserves the existing file, creates only the missing artifact, and returns only the newly created locator.

### S3 Repeat Apply Is A No-Op

Given a target where all minimal suite artifacts already exist,
When apply scaffold runs again,
Then it reports `mutates: false`, preserves existing files, and returns an empty `created_locators` list.

### S4 Full Suite Remains Reserved

Given a caller requests `--suite full`,
When scaffold runs with or without apply intent,
Then it fails closed to the reserved full-suite surface and creates no locators.

### S5 Unsafe Artifact Paths Fail Closed

Given a caller supplies a traversal or absolute item, or the target scaffold path contains a symlink or directory artifact placeholder,
When apply scaffold runs,
Then it fails closed before writing any scaffold artifact and returns an empty `created_locators` list.

## Acceptance

- AC-1115-1: `loom suite scaffold --target . --item WI-1115 --json` remains read-only, emits `mutates: false`, keeps `apply_required: true`, and creates no locators.
- AC-1115-2: `loom suite scaffold --target <repo> --item <item> --json --apply` creates only missing minimal `spec.md` and `plan.md` artifacts under `.loom/specs/<item>/`.
- AC-1115-3: Apply output reports `apply: true`, `apply_required: false`, actual `created_locators`, per-artifact write status, and `mutates: true` only when at least one file was created.
- AC-1115-4: Existing files are never overwritten, and repeat apply returns an empty `created_locators` list with `mutates: false`.
- AC-1115-5: Traversal items, absolute items, symlink artifact paths, and directory artifact placeholders fail closed before writes.
- AC-1115-6: `--suite full` remains fail-closed, and no host, review, merge-ready, closeout, generated skill, spec-kit command, or `.specify/` surfaces are introduced.
