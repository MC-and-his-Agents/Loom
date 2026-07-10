# WI-1509 Spec

## Suite Path

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts `suite-index.md`, `research.md`, `contracts.md`, and `readiness-checklist.md`; rationale: WI-1509 is a bounded CLI/runtime hardening of the already existing gate freeze and PR metadata-preflight surfaces. It does not change hosted workflows, PR template human presentation, GitHub host writes, release mechanics, security permissions, external data, or persistence outside existing repo-local runtime artifacts. consumer boundary: CLI contract checks, generated runtime drift checks, suite validate, review, PR gate, merge-ready, and #1510-#1515 planning may consume this minimal spec, plan, evidence map, task carrier, WI carriers, focused validation output, and PR evidence. recheck condition: require a full suite if #1509 expands into hosted workflow changes, PR template rewrite, new host writes, release mechanics, security/privacy behavior, migration behavior, or external visible actions.

## Objective

Make `loom gate freeze check` and `write` freeze PR body rendered/readback hash evidence and machine metadata block fingerprints, blocking stale PR body or carrier identity drift before hosted gate admission.

## Acceptance Scenarios

### S1: PR body hash evidence is pinned

Given `loom gate freeze check --body-file <rendered> --compare-body-file <readback>` runs, the snapshot records rendered body hash, readback body hash, machine metadata block raw excerpt hashes, and fingerprints from `pr metadata-preflight`.

### S2: Rendered/readback drift blocks freeze

Given rendered and readback PR body evidence differs, freeze readiness is `block`, identifies the PR body binding as stale, and tells the operator to re-run `gh pr edit --body-file`, read back the PR body, and rerun freeze.

### S3: Machine carrier identity drift blocks freeze

Given the PR body machine carrier disagrees with the expected Work Item, branch, or head SHA, freeze readiness is `block` and preserves the `pr metadata-preflight` mismatch messages.

### S4: Existing preflight remains the source of truth

Given `pr metadata-preflight` already classifies PR body and metadata mismatches, gate freeze consumes and pins its result without replacing its parser or weakening existing PR gate, review, merge-ready, or closeout checks.

### S5: Runtime copies and CLI contract coverage stay aligned

Given shared runtime edits are made, generated runtime copies and CLI contract tests reflect the same PR body pinning behavior.

## Non-Goals

- No PR template rewrite.
- No change to the human PR body display layer.
- No hosted gate admission workflow implementation.
- No carrier/shadow freshness implementation.
- No review/head drift policy implementation.
- No release/tag/npm/GitHub Release changes.
