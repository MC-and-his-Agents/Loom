# Spec

## Suite Contract

- Suite path: minimal
- Consumes: Work Item [#2012](https://github.com/MC-and-his-Agents/Loom/issues/2012) and merged source repairs #2026/#2028.
- Story readiness and business confirmation: not_applicable; this is a patch distribution correction with no new product behavior.
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-2012 distributes already-merged CLI repair semantics through a bounded patch release and does not introduce a new research, API, product, or readiness contract beyond the release evidence below. consumer boundary: suite validate, review, PR gate, controlled merge, release workflow, release readback, and downstream Harbor #246 hosted-gate evidence consume this minimal spec, plan, Work Item carrier, and focused package validation. recheck condition: require full-suite artifacts if scope expands into release workflow semantics, npm publishing mechanics, credentials or host permissions, a new package/API contract, or any WebEnvoy product behavior.
- Produces: v0.28.1 root CLI package release metadata and release evidence.
- Freshness: revalidate after any version, package payload, or carrier change.

## Goal

Distribute the already-merged metadata-only carrier refresh repair so hosted gates install a CLI that contains it.

## Scope

- In scope: root CLI patch version, package/plugin payload metadata, release carrier, package validation, and tag/npm/release readback.
- Out of scope: carrier refresh semantics, WebEnvoy product code, browser behavior, gate weakening, and external product actions.

## Key Scenarios

### Scenario S1

Given `v0.28.0` is already published on an earlier commit,
when the v0.28.1 release PR merges,
then the root npm package, matching tag, and GitHub Release identify the release commit.

### Scenario S2

Given Harbor PR #246 runs its hosted gate,
when its runner installs the latest Loom CLI,
then metadata-only carrier refresh does not require an intentionally absent bootstrap manifest.

## Evidence

- S1: `tools/version_surface_check.py`, `tools/check_npm_package.py --surface aggregate`, release workflow, and post-merge registry/tag readback.
- S2: Harbor PR #246 hosted `loom-pr-merge-gate` after the release is published.

## Acceptance Criteria

- [ ] A1: `VERSION`, `package.json`, and plugin payload metadata agree on `0.28.1`.
- [ ] A2: The package payload and installed-global CLI smoke pass.
- [ ] A3: The release creates matching npm, tag, and GitHub Release evidence.
- [ ] A4: Harbor PR #246's hosted gate consumes the published repair without manifest fabrication.
