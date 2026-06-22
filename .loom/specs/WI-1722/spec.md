# Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1722 is a bounded legacy installer behavior slice with explicit issue acceptance, focused installer regression coverage, and no new host plugin freshness/readback design, release process, or external-visible host write beyond the existing deprecated installer package. consumer boundary: suite validate, build checkpoint, review, PR gate, hosted checks, and issue handoff may consume this minimal suite plus Work Item evidence without full-path artifacts. recheck condition: require full suite artifacts if scope expands into host freshness/reporting, plugin metadata/hash/release metadata, root CLI provider behavior, release mechanics, npm publish, external host writes, or a new distribution contract.
- Consumes:
  - Work Item / FR locator: GitHub issue #1722
  - Story Readiness: not required; #1722 is a bounded installer hardening issue with acceptance criteria in the issue body.
  - Story Business Confirmation: not required; product boundary is fixed by #1722.
- Produces:
  - Scenario ids / locators: S1, S2, S3 in this spec.
  - Acceptance ids / locators: A1-A5 in this spec.
  - Behavior evidence expectation: legacy single-skill installer operations fail closed and do not produce current distribution success.
- Locator:
  - Spec locator: `.loom/specs/WI-1722/spec.md`
- Provenance:
  - Source issue: https://github.com/MC-and-his-Agents/Loom/issues/1722
  - Freshness rule: recheck if installer skill-mode behavior, distribution layer vocabulary, legacy metadata diagnostics, tests, or package README copy change.

## Goal

Retire user-visible legacy `loom-installer add skill ...` and related single-skill upgrade success semantics. Single-skill requests must fail closed, old `generated-single-skill` metadata may only be read as migration diagnostics, and `skill_package_version` must remain outside freshness or upgrade success decisions.

## Scope

- In scope:
  - `packages/loom-installer` skill-mode add / upgrade-plan / verify-upgrade behavior.
  - Direct host-specific single-skill installer exports in `codex.ts` and `claude.ts`.
  - Installer result distribution-layer vocabulary and tests.
  - Minimal package README/package description sync for the deprecated installer surface.
  - WI-1722 Loom carriers and minimal suite evidence.
- Out of scope:
  - #1713, #1721, #1715, host freshness/reporting, plugin metadata/hash/release metadata, root README broad marketing/install copy, release version bump, npm publish, GitHub release, and unrelated legacy compatibility read-path deletion.

## Key Scenarios

### Scenario S1

Given a user invokes legacy `loom-installer add skill <skill-id>`

When the installer resolves the request

Then it returns a blocked migration diagnostic and does not create `.agents/skills` or `.claude/skills` payloads.

### Scenario S2

Given a target contains old single-skill `.loom-install-status.json` metadata with `installed_layer: generated-single-skill` and `skill_package_version`

When `upgrade-plan skill <skill-id>` runs

Then it reports incompatible migration diagnostics, does not compare payload paths, and does not produce `current` or `upgrade-available`.

### Scenario S3

Given library consumers call host-specific single-skill installer exports directly

When the direct Codex or Claude function is used

Then it returns a blocked diagnostic and does not copy single-skill payloads.

## Behavior Evidence

- Scenario coverage:
  - S1 -> `packages/loom-installer/test/installer.test.ts` Codex and Claude single-skill add fail-closed assertions.
  - S2 -> `packages/loom-installer/test/installer.test.ts` legacy per-skill metadata diagnostic assertion.
  - S3 -> `packages/loom-installer/src/codex.ts` and `packages/loom-installer/src/claude.ts` direct export behavior plus TypeScript compile in installer tests.
- Expected evidence locator: `.loom/specs/WI-1722/evidence-map.md`
- Freshness rule: rerun installer tests and docs checks after changes to installer skill-mode behavior, package README, or legacy status handling.
- Execution ledger acceptance locator: `.loom/progress/WI-1722.md`

## Exceptions And Boundaries

- Failure modes: unknown skill IDs still fail closed through manifest skill resolution; missing target paths still fail closed through existing target validation.
- Operational boundaries: no target repository mutation from skill-mode add, upgrade-plan, or verify-upgrade; no high-cost guardian run in this worker lane.
- Rollback expectation: revert the bounded installer source/test/docs changes and remove WI-1722 carriers if #1722 is abandoned before PR creation.

## Acceptance Criteria

- [x] A1: Legacy single-skill add no longer succeeds for Codex or Claude.
- [x] A2: `generated-single-skill` is no longer emitted as current installer output.
- [x] A3: Old single-skill metadata only produces migration diagnostics and no upgrade success.
- [x] A4: `skill_package_version` remains diagnostic-only and outside freshness success.
- [x] A5: Installer regression tests cover fail-closed and no-mutation behavior.
