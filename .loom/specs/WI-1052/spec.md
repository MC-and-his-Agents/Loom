# WI-1052 Spec

## Goal

Plan the full spec suite CLI command surface so later Work Items can implement automation without changing the already frozen #1014-#1020 contracts.

## Scope

- Add a planning record for full spec suite CLI automation.
- Cover command names, subcommand boundaries, behavior classes, JSON fields, failure taxonomy, `loom doctor` / `loom verify` integration points, scenario skill integration points, and implementation backlog.
- Keep the work docs/planning-only.

## Non-Goals

- Do not implement CLI commands.
- Do not add real command entries to `tools/loom.py`, `loom help --json`, package binaries, generated skills, or installed runtime.
- Do not copy spec-kit `/speckit.*` command names or `.specify/` layout.
- Do not rewrite #1014-#1020 frozen contracts.

## Scenarios

### SC-1052-1: Planning Surface Is Present

Given #1014-#1020 contracts are closed and consumable,
When a later CLI implementation Work Item needs the suite automation boundary,
Then it can read `docs/methodology/harness/full-spec-suite-cli-surface.md` for the planned command family, behavior classes, JSON fields, failure taxonomy, integration points, and implementation backlog.

### SC-1052-2: Planning Does Not Become Implementation

Given #1052 is planning-only,
When the PR is reviewed,
Then no non-Markdown CLI implementation entry exists for the planned `loom suite ...` commands.

### SC-1052-3: Existing Contracts Remain Authority

Given #1052 consumes #1014-#1020,
When the planning document names suite, evidence, consistency, task carrier, gate, doctor, verify, or scenario skill behavior,
Then it links to the owning source contracts and does not redefine them as new truth.

## Acceptance Criteria

- AC-1052-1: The planning record covers read-only, scaffold-write, validate, analyze, and fail-closed behavior classes.
- AC-1052-2: The planning record proposes command names and subcommand boundaries without adding them to the implemented CLI matrix.
- AC-1052-3: The planning record defines JSON output fields and a failure taxonomy suitable for later CLI implementation.
- AC-1052-4: The planning record defines `loom doctor`, `loom verify`, and scenario skill integration points.
- AC-1052-5: The planning record includes follow-up CLI implementation backlog slices.
- AC-1052-6: Validation confirms no real CLI command implementation entry was added.
