# WI-1486 Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1486 is a bounded executable-skill payload text update with no new runtime behavior, external host contract, research, or readiness discovery need. consumer boundary: suite validate, review, PR gate, merge-ready, dependent docs issue #1488, and issue closeout may consume this minimal suite plus focused skills surface validation only. recheck condition: require full suite artifacts if scope expands into CLI implementation, user documentation migration, release execution, package metadata, or external-visible host writes.
- Consumes:
  - Work Item / FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1486
  - Story Readiness confirmed locator, blocking locator, or skip rationale: issue #1486 body and milestone/11 v0.17.0 baseline are sufficient for this contract-only skill payload item.
  - Story scenario locator, or skip rationale: scenarios are defined below.
  - Story Business Confirmation confirmed locator, blocking locator, or skip rationale: not_applicable; no external business semantics.
- Produces:
  - Scenario ids / locators: S1-S3 in this file.
  - Acceptance ids / locators: A1-A4 in this file.
  - Behavior evidence expectation: source, generated mirror, and Codex user plugin payload skill text all default to global `loom` CLI agent-safe summary/artifact locator usage.
- Locator:
  - Spec locator: .loom/specs/WI-1486/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: issue #1486.
  - Freshness rule: recheck after changes to skill command examples, output contracts, shared skill references, or plugin payload mirrors.

## Goal

- Update the Codex user-level plugin skill payload so executable skills default to global `loom` CLI agent-safe output and artifact locators.
- Prevent skills and cross-thread handoff from encouraging inline full reports, full status tables, full command JSON, long stdout, old full thread turns, repo-local runtime/plugin/skills install paths, single-skill packages, or old installer compatibility.

## Scope

- In scope: `src/skills`, generated `skills`, `plugins/loom/skills`, and minimal WI-1486 carriers.
- Out of scope: CLI runtime behavior already owned by #1484/#1485, user docs/help/migration owned by #1488, release evidence owned by #1658, final closeout matrix owned by #1489, downstream repository migration, and old installer compatibility.

## Key Scenarios

### Scenario S1

Given an operator enters a Loom scenario skill from the Codex user-level plugin
When the skill references an executable command
Then the example calls the global `loom` CLI with default agent-safe `--json` output rather than repo-local scripts.

### Scenario S2

Given a skill needs details beyond a bounded summary
When the skill consumes command output
Then full diagnostics are read only through explicit artifact locators or `--full-output` debugging, not copied inline.

### Scenario S3

Given a handoff or thread rotation package is produced
When a new thread consumes it
Then it receives summary and authoritative locators first, and does not replay complete logs, full command JSON, or old thread turns by default.

## Behavior Evidence

- Scenario coverage:
  - S1 -> `src/skills/route-matrix.md` and scenario `SKILL.md` command examples.
  - S2 -> scenario output contracts and shared review execution reference.
  - S3 -> `loom-handoff` output contract and route-matrix agent-safe boundary.
- Expected evidence locator: .loom/specs/WI-1486/evidence-map.md
- Freshness rule: evidence must be rerun after any source skill, generated mirror, plugin payload, or shared skill reference change.

## Exceptions And Boundaries

- Full diagnostics may be read explicitly for debugging, audit, or blocker classification, but only by locator or explicit full-output mode.
- Artifacts are diagnostic evidence, not authored truth carriers.
- Host repositories remain metadata-only adoption and work fact carrier surfaces.
- Rollback is reverting the skill payload text, generated mirrors, and WI-1486 carriers.

## Acceptance Criteria

- [x] A1: Executable skill command examples use global `loom` CLI instead of repo-local script paths.
- [x] A2: Skill contracts state that default output is agent-safe summary / artifact locator.
- [x] A3: Cross-thread handoff prohibits inline full reports, full status tables, full command JSON, long stdout, and old full thread turns by default.
- [x] A4: The Codex user-level plugin payload stays synchronized with source skills and does not restore repo-local plugin/runtime/skills, single-skill package, or old installer paths.
