# WI-1717 Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1717 is a bounded regression coverage Work Item that consumes the already-frozen freshness contract and existing CLI/hash test surfaces. consumer boundary: suite validate, build, review, PR gate, hosted checks, and closeout may consume this minimal suite. recheck condition: require full suite if scope expands into new freshness schema, release execution, legacy installer tombstone behavior, or a broad fixture framework.
- Work Item locator: .loom/work-items/WI-1717.md
- Produces: S1-S3 and A1-A5 freshness regression coverage.
- Freshness rule: re-run after changes to `tools/loom.py`, `tools/check_cli_contract.py`, `tools/check_npm_package.py`, or plugin payload metadata/hash behavior.

## Goal

Add the smallest regression coverage that proves CLI/plugin freshness reporting does not drift after #1712-#1716.

## Scope

- In scope: `tools/check_cli_contract.py` adoption host metadata checks, existing plugin payload hash tests, WI-1717 carriers.
- Out of scope: v0.19.0 release closeout, npm publish, GitHub Release, installer tombstone behavior, broad fixture framework changes.

## Key Scenarios

### Scenario S1

Given CLI and Codex plugin payload metadata are current
When `loom version` or `loom version --json` is run
Then the output reports `already_current`, compatible plugin surface, and a host doctor readback command.

### Scenario S2

Given CLI latest, marketplace payload, or runtime cache drift
When `loom version --json`, `loom upgrade-plan`, or `loom host doctor` is run
Then the diagnostic reports the correct stale or missing metadata class and the shortest safe next action.

### Scenario S3

Given plugin surface versions diverge while payload metadata remains readable
When freshness is computed
Then `surface_compatibility.status` is `incompatible` and identifies the divergent layer.

## Acceptance Criteria

- [x] A1: CLI stale and already-current states are covered.
- [x] A2: Plugin payload stale and metadata-missing states are covered.
- [x] A3: Plugin surface incompatibility is covered.
- [x] A4: Short diagnostic/action output is covered.
- [x] A5: Payload hash stability coverage remains in the existing hash test.
