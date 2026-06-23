# Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1716 is a bounded CLI guidance refinement that consumes the already-frozen payload freshness contract. consumer boundary: suite validate, build, review, PR gate, hosted checks, and closeout may consume this minimal suite. recheck condition: require full suite if scope expands into host cache mutation, legacy installer behavior, release execution, or broad fixture catalogs.
- Consumes:
  - Work Item / FR locator: issue #1716 under FR #1711
  - Story Readiness: not required; this is an issue-scoped CLI guidance Work Item.
  - Story scenario: issue #1716 acceptance bullets.
  - Story Business Confirmation: not required; product semantics are constrained to existing CLI diagnostics.
- Produces:
  - Scenario ids / locators: S1, S2, S3
  - Acceptance ids / locators: A1-A4
  - Behavior evidence expectation: CLI JSON exposes executable plugin refresh guidance and readback commands.
- Locator:
  - Spec locator: .loom/specs/WI-1716/spec.md
- Provenance:
  - Source issue: https://github.com/MC-and-his-Agents/Loom/issues/1716
  - Freshness rule: Recheck when `tools/loom.py` freshness action output, host doctor output, or upgrade-plan action fields change.

## Goal

Users and agents can move from a stale Codex plugin payload diagnosis to the correct next action without guessing whether to upgrade the CLI, refresh the user plugin source, register the plugin, or reload Codex.

## Scope

- In scope: structured refresh guidance in `version_freshness`, `cli-plugin-freshness` upgrade-plan action fields, focused contract checks, and the Codex user plugin adoption contract.
- Out of scope: direct writes to Codex-owned runtime cache, npm release, legacy installer behavior, single SKILL install, or v0.20.0 ship command work.

## Key Scenarios

### Scenario S1

Given the Codex plugin marketplace source is stale or missing payload metadata

When an agent runs `loom upgrade-plan --target <repo> --host codex --json`

Then the `cli-plugin-freshness` action includes executable `loom host install` and `loom host register` apply commands plus a host doctor readback command.

### Scenario S2

Given the Codex-owned runtime cache is stale or missing payload metadata

When an agent runs `loom version --json`

Then the plugin payload guidance marks reload required, does not claim Loom can write the runtime cache directly, and includes host doctor readback.

### Scenario S3

Given plugin refresh or simulated host reload has completed

When an agent runs `loom host doctor --host codex --scope user --json`

Then the version freshness block reports the plugin payload as `already_current`.

## Behavior Evidence

- Scenario coverage:
  - S1 -> `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - S2 -> `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - S3 -> `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
- Expected evidence locator: .loom/specs/WI-1716/evidence-map.md
- Freshness rule: Evidence must bind to branch `work/1716-plugin-refresh-guidance` and current PR head before merge-ready.
- Execution ledger acceptance locator: issue #1716

## Exceptions And Boundaries

- Failure modes: source payload metadata missing may require CLI upgrade first; marketplace source drift is repaired by `loom host install/register`; runtime cache drift requires Codex reload/readback.
- Operational boundaries: Diagnostics may read npm and user-level Codex plugin metadata; they must not mutate host state unless the user runs explicit `loom host ... --apply`.
- Rollback expectation: Revert this PR to remove the guidance fields and documentation addition.

## Acceptance Criteria

- [x] A1: Stale marketplace plugin payload guidance includes `loom host install --host codex --scope user --apply --json`.
- [x] A2: Stale marketplace plugin payload guidance includes `loom host register --host codex --scope user --apply --json`.
- [x] A3: Runtime cache stale guidance uses reload/readback and exposes no runtime-cache write command.
- [x] A4: After host install/register or simulated host reload, `loom host doctor` reports plugin payload freshness as `already_current`.
