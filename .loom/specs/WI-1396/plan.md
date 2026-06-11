# WI-1396 Plan

- Suite path: minimal
- Work Item: WI-1396

## Implementation

1. Update `docs/adoption/loom-cli-release-surface.md` to reference targetable release/package surfaces and retained aggregate commands.
2. Update `docs/evidence/validations/validation-release-validation-evidence-contract.md` to record the #1393/#1394/#1395 surface split readback and aggregate validation commands.
3. Update `docs/methodology/harness/closeout-gate.md` so closeout can consume named surfaces or aggregate evidence only when label/head/run locator/consumer boundary are retained.
4. Add WI-1396 work-item, progress, minimal suite, evidence map, and task carrier files.
5. Validate local commands, PR metadata/head readback, and hosted checks, then stop at `waiting-scheduler-gate`.

## Validation Mapping

- S1 -> automated validation evidence: `python3 tools/check_release_surface.py --list-surfaces`.
- S2 -> automated validation evidence: `python3 tools/check_release_surface.py --surface aggregate-release-surface --show-surface-evidence`.
- S3 -> automated validation evidence: `python3 tools/check_npm_package.py --list-surfaces` and `python3 tools/check_npm_package.py`.
- S4 -> structural validation evidence: focused diff/readback of `docs/adoption/loom-cli-release-surface.md`, `docs/evidence/validations/validation-release-validation-evidence-contract.md`, and `docs/methodology/harness/closeout-gate.md`.

## Acceptance Mapping

- AC-1 -> structural validation strategy: release surface doc readback lists targetable release/package surfaces and aggregate compatibility commands.
- AC-2 -> automated and structural validation strategy: evidence record readback plus aggregate release/package validation commands.
- AC-3 -> structural validation strategy: closeout gate guidance includes named surfaces, aggregate command conditions, and evidence field requirements.
- AC-4 -> automated validation strategy: aggregate release and package commands pass.
- AC-5 -> structural validation strategy: `git diff --check` and `git diff --name-only origin/main...HEAD`.

## Commands

- `git diff --check`
- `python3 tools/check_release_surface.py --help`
- `python3 tools/check_release_surface.py --list-surfaces`
- `python3 tools/check_release_surface.py --surface aggregate-release-surface --show-surface-evidence`
- `python3 tools/check_npm_package.py --help`
- `python3 tools/check_npm_package.py --list-surfaces`
- `python3 tools/check_npm_package.py`
- `npm run test:package`
- `python3 tools/loom.py suite inspect --target . --item WI-1396 --json`
- `python3 tools/loom.py suite validate --target . --item WI-1396 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1396 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1396 --json`

## Boundaries

- No `tools/check_release_surface.py` or `tools/check_npm_package.py` behavior changes.
- No `VERSION`, tags, GitHub Releases, npm publish, workflow behavior, runtime smoke semantic, or package payload changes.
- No `.loom/reviews/**`, `.loom/status/current.md`, `.loom/shadow/**`, parent #1260 closeout, umbrella #1255 closeout, guardian/formal review, controlled merge, or release execution.
- Parent #1260 and umbrella #1255 closeout remain scheduler-owned/out of scope. Statement: deferred is not completed.
