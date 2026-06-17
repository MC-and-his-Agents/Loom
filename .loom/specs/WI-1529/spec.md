# WI-1529 Spec

## Suite Path

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts `suite-index.md`, `research.md`, `contracts.md`, and `readiness-checklist.md`; rationale: WI-1529 is a bounded local skills surface implementation with scope, behavior, validation, and consumer boundaries fully carried by `spec.md`, `plan.md`, `evidence-map.md`, and `task-carrier.md`; it does not introduce new host behavior, external API contracts, security/privacy decisions, release mechanics, or cross-work-item schema ownership. consumer boundary: suite validate, review, merge-ready, PR gate, hosted CI, closeout, and #1515 release/no-release readback may consume this minimal suite and must not treat skipped full-path artifacts as completed work. recheck condition: require a full suite if #1529 expands into new release workflow semantics, review/merge-ready/gate freeze behavior, hosted admission, closeout profile behavior, external host mutation, security/privacy behavior, or shared schema/failure vocabulary ownership beyond the skills surface checker.

## Objective

Productize SKILL reference integrity as an executable skills surface so missing references, wrong path-base assumptions, install package omissions, and runtime copy drift fail before release or milestone closeout review.

## Acceptance Scenarios

### S1: Relative reference diagnostics identify the base

Given a generated skill package contains a relative markdown or JSON reference, the checker resolves it from the package file and reports whether the target is inside the install package, inside the runtime copy, missing under that base, or outside both allowed roots.

### S2: Runtime copy parity is enforced

Given shared package assets such as registry, install layout, upgrade contract, route matrix, or distribution adapter contract drift between source, install, and runtime copies, the `reference-integrity` surface fails closed with a file-specific diagnostic.

### S3: Non-file links do not produce false positives

Given a SKILL package contains anchors or scheme-based links, the reference scanner ignores those non-file links and only validates local relative references that imply an on-disk file.

### S4: Release/skills surface consumes the check

Given `python3 tools/skills_surface.py check` runs before release or closeout, the `reference-integrity` surface is included with generated-tree drift, package metadata, cache artifact, and launcher smoke checks.

## Non-Goals

- No change to review, merge-ready, gate freeze, PR gate, hosted admission, closeout profile, or release/no-release semantics.
- No migration of skill directories or external source layouts.
- No rewrite of SKILL content unless the checker exposes a true broken reference.
- No change to #1510, #1512, #1513, #1531, #1532, #1533, #1534, or #1515 behavior.
