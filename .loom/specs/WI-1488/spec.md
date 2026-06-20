# WI-1488 Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1488 is a bounded documentation/help/migration update that consumes already implemented runtime and skill behavior. consumer boundary: suite validate, review, PR gate, #1658 release readiness, #1489 final closeout, and issue closeout may consume this minimal suite plus focused documentation checks. recheck condition: require full suite artifacts if scope expands into runtime behavior, release execution, package metadata, downstream repository migration, or external-visible host writes.
- Consumes:
  - Work Item / FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1488
  - Story Readiness confirmed locator, blocking locator, or skip rationale: issue #1488 body and milestone/11 v0.17.0 baseline are sufficient for this docs-only item.
  - Story scenario locator, or skip rationale: scenarios are defined below.
  - Story Business Confirmation confirmed locator, blocking locator, or skip rationale: not_applicable; no external business semantics.
- Produces:
  - Scenario ids / locators: S1-S3 in this file.
  - Acceptance ids / locators: A1-A5 in this file.
  - Behavior evidence expectation: docs and help-facing contracts describe safe output use, metadata-only adoption, and unsupported legacy install surfaces without recommending inline full output.
- Locator:
  - Spec locator: .loom/specs/WI-1488/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: issue #1488.
  - Freshness rule: recheck after changes to docs/adoption, README, CLI command matrix/help descriptions, or output-mode wording.

## Goal

- Make the public docs and help-facing contracts match the shipped context-safe runtime behavior.
- Make the v0.17.0 support boundary explicit: downstream repositories keep adoption metadata and work fact carriers, while runtime execution is the global `loom` CLI and skill discovery is the Codex user-level plugin.

## Scope

- In scope: README, adoption docs, CLI command matrix/help-facing documentation, and WI-1488 carriers.
- Out of scope: release/tag/npm/GitHub Release work (#1658), final regression closeout (#1489), downstream repository migration, skill payload implementation (#1486), runtime output implementation (#1481-#1485), repo-local plugin/runtime/skills installs, single-skill package distribution, and old installer compatibility.

## Key Scenarios

### Scenario S1

Given a downstream operator reads Loom installation or migration docs
When they follow the documented path
Then the docs point to global `loom` CLI plus Codex user-level plugin and metadata-only repository adoption, not repo-local runtime/plugin/skills installation.

### Scenario S2

Given an agent or operator needs Loom command diagnostics
When they read docs or help-facing contracts
Then default output is described as agent-safe summary or direct JSON within budget, complete diagnostics require explicit `--full-output`, and artifact locators are preferred over inline full logs.

### Scenario S3

Given a release operator prepares #1658
When they consume #1488 docs as release input
Then the docs already explain the v0.17.0 support boundary and no longer recommend single-skill packages, old installer paths, or repo-local plugin/runtime/skills payloads as current adoption.

## Behavior Evidence

- Scenario coverage:
  - S1 -> README and docs/adoption migration/install guidance.
  - S2 -> docs/adoption output guidance and docs/methodology/harness/cli-command-matrix.md.
  - S3 -> docs/adoption release/migration references and absence of current-path legacy recommendations.
- Expected evidence locator: .loom/specs/WI-1488/evidence-map.md
- Freshness rule: evidence must be rerun after any docs/help-facing text change.

## Exceptions And Boundaries

- Source-repository mirrors under `skills/` and `plugins/loom/skills/` may still be documented as Loom source/release artifacts; they must not be described as target repository install paths.
- Full diagnostics may be used for explicit debugging, audit, or blocker classification; docs must prefer artifact locators and must not instruct users to paste full JSON or long stdout into threads by default.
- Legacy installer references may remain only as deprecated historical evidence or checker anchors, not as compatible current install commands.

## Acceptance Criteria

- [x] A1: Docs describe global CLI plus Codex user-level plugin as the only supported downstream runtime/plugin surface.
- [x] A2: Docs describe metadata-only host repository adoption and work fact carriers without installing repo-local runtime/plugin/skills payloads.
- [x] A3: Docs/help-facing contracts describe summary, artifact locator, and explicit full diagnostics modes.
- [x] A4: Current-path docs do not recommend repo-local plugin/runtime/skills installs, single-skill packages, or old installer paths.
- [x] A5: Validation evidence is identified for docs/help consistency and release-readiness consumption.
