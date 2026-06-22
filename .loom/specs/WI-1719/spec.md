# Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1719 is a bounded legacy installer behavior slice with explicit issue scope, focused installer regression coverage, and no new product workflow or host mutation design. consumer boundary: suite validate, build checkpoint, review, merge-ready, PR/CI, and issue closeout may consume this minimal suite plus Work Item evidence without full-path artifacts. recheck condition: require full suite artifacts if scope expands into current CLI provider behavior, host command boundary behavior, release mechanics, npm publish, external host writes, migration policy beyond diagnostics, or new product/API contracts.
- Consumes:
  - Work Item / FR locator: GitHub issue #1719
  - Story Readiness: not required; #1719 is a bounded installer hardening issue with acceptance criteria in the issue body.
  - Story Business Confirmation: not required; product boundary is fixed by #1719.
- Produces:
  - Scenario ids / locators: S1, S2, S3 in this spec.
  - Acceptance ids / locators: A1-A5 in this spec.
  - Behavior evidence expectation: installer version context and upgrade planning no longer treat single SKILL package version as freshness.
- Locator:
  - Spec locator: `.loom/specs/WI-1719/spec.md`
- Provenance:
  - Source issue: https://github.com/MC-and-his-Agents/Loom/issues/1719
  - Freshness rule: recheck if installer version context, payload manifest skill metadata, docs wording, or single-skill upgrade checks change.

## Goal

Retire per-skill distribution version semantics from the legacy installer so a single SKILL only exposes behavior contract compatibility through `contract_version` / `skill_contract_version`, while legacy `skill_package_version` metadata can remain readable as migration diagnostics and must not drive upgrade freshness.

## Scope

- In scope:
  - `packages/loom-installer` payload skill metadata, version context, upgrade-plan / verify-upgrade freshness comparison, and installer regression tests.
  - Installer docs or adoption docs directly needed to preserve the #1719 behavior boundary.
  - WI-1719 Loom carriers and minimal suite evidence.
- Out of scope:
  - Restoring or recommending single SKILL install as a current install path.
  - Recommending legacy installer or full-repo clone as a current install path.
  - Changing `tools/check_npm_package.py`, `test/plugin_payload_hash_test.py`, host command boundary docs/skills, release versions, npm publish, or release files.
  - Forcing skill contract version to match CLI, plugin, registry, installer, or release versions.

## Key Scenarios

### Scenario S1

Given a single-skill install result is produced by the legacy installer

When version context is rendered for the named skill

Then it includes `skill_contract_version` and omits `skill_package_version` as a distribution version.

### Scenario S2

Given an installed single-skill status file contains legacy `version_context.skill_package_version`

When `upgrade-plan skill <skill-id>` compares installed and available version context

Then the legacy field is ignored for freshness and does not produce `upgrade-available`.

### Scenario S3

Given the installer payload manifest is generated from the plugin SKILLS payload

When the manifest records public skill metadata

Then the per-skill public metadata uses `contract_version` for compatibility and does not emit `skill_package_version`.

## Behavior Evidence

- Scenario coverage:
  - S1 -> `packages/loom-installer/test/installer.test.ts` single-skill install assertions.
  - S2 -> `packages/loom-installer/test/installer.test.ts` legacy per-skill metadata upgrade-plan regression.
  - S3 -> `packages/loom-installer/test/installer.test.ts` payload manifest public skill assertions.
- Expected evidence locator: `.loom/specs/WI-1719/evidence-map.md`
- Freshness rule: rerun installer tests and docs checks after changes to installer metadata, payload build, or README sync.
- Execution ledger acceptance locator: `.loom/progress/WI-1719.md`

## Exceptions And Boundaries

- Failure modes: missing or inconsistent installed status metadata still fails closed; payload file hash drift still reports drift; legacy single-skill install remains historical behavior only.
- Operational boundaries: no target repository mutation from `upgrade-plan` or `verify-upgrade`; no high-cost guardian run in this build slice.
- Rollback expectation: revert the bounded installer source/test changes and remove WI-1719 carriers if #1719 is abandoned before PR creation.

## Acceptance Criteria

- [x] A1: Single-skill install version context no longer exposes `skill_package_version`.
- [x] A2: Legacy installed `skill_package_version` does not affect upgrade freshness.
- [x] A3: Generated payload skill records use `contract_version` and omit per-skill package version.
- [x] A4: Installer regression tests cover the behavior.
- [x] A5: Loom carriers identify ownership, non-goals, validation, and forbidden surfaces.
