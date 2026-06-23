# Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1715 is a bounded CLI diagnostic reporting change with issue-level acceptance and focused contract coverage. consumer boundary: suite validate, build, review, PR gate, hosted checks, and closeout may consume this minimal suite. recheck condition: require full suite if scope expands into plugin refresh apply behavior, broad fixture catalogs, legacy installer behavior, or v0.19.0 release closeout.
- Consumes:
  - Work Item / FR locator: issue #1715
  - Story Readiness: not required; this is a CLI diagnostic Work Item under parent FR #1711.
  - Story scenario: issue #1715 acceptance bullets.
  - Story Business Confirmation: not required; no product business semantic change beyond CLI diagnostics.
- Produces:
  - Scenario ids / locators: S1, S2, S3
  - Acceptance ids / locators: A1-A5
  - Behavior evidence expectation: CLI JSON and short output expose actionable freshness state.
- Locator:
  - Spec locator: .loom/specs/WI-1715/spec.md
- Provenance:
  - Source issue: https://github.com/MC-and-his-Agents/Loom/issues/1715
  - Freshness rule: Recheck when `tools/loom.py` version, doctor, host doctor, or upgrade-plan output changes.

## Goal

Users and agents can tell whether the root Loom CLI and Codex plugin payload are current, stale, missing metadata, or unreadable without manually diffing plugin cache contents.

## Scope

- In scope: `loom version --json`, default `loom version` action line, `loom doctor`, `loom host doctor`, `loom upgrade-plan`, and focused CLI contract tests.
- Out of scope: applying plugin refresh, releasing v0.19.0, deprecating npm packages, or changing legacy installer behavior.

## Key Scenarios

### Scenario S1

Given a current CLI and current Codex plugin payload

When an agent runs `loom version --json`, `loom host doctor --host codex --scope user --json`, or `loom upgrade-plan --target . --host codex --json`

Then the output reports `already_current` or a current `cli-plugin-freshness` action.

### Scenario S2

Given the CLI is behind npm latest

When an agent runs `loom version --json`

Then the output reports `upgrade_cli` and points to `npm install -g @mc-and-his-agents/loom@latest`.

### Scenario S3

Given the Codex plugin payload is stale or missing metadata

When an agent runs `loom version --json`

Then the output reports `refresh_plugin`, includes plugin payload readback, and preserves surface compatibility status.

## Behavior Evidence

- Scenario coverage:
  - S1 -> `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - S2 -> `LOOM_TEST_NPM_LATEST_VERSION=99.0.0 python3 tools/loom.py version --json`
  - S3 -> `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
- Expected evidence locator: .loom/specs/WI-1715/evidence-map.md
- Freshness rule: Evidence must bind to branch `work/1715-freshness-reporting` and current PR head before merge-ready.
- Execution ledger acceptance locator: issue #1715

## Exceptions And Boundaries

- Failure modes: npm latest unreadable reports `npm_unreadable`; host readback failure reports plugin refresh action without mutating user state.
- Operational boundaries: Diagnostics may read npm and user-level Codex plugin metadata; they must not write host state.
- Rollback expectation: Revert this PR to remove the aggregate freshness block.

## Acceptance Criteria

- [x] A1: `loom version --json` reports installed CLI, latest CLI, plugin payload freshness, and surface compatibility.
- [x] A2: `loom doctor` and `loom host doctor` expose the same freshness block.
- [x] A3: `loom upgrade-plan` emits a machine-readable `cli-plugin-freshness` action.
- [x] A4: Current, stale CLI, stale plugin, missing metadata, and npm-unreadable cases are covered by focused checks.
- [x] A5: Default `loom version` prints a short actionable next step.
