# WI-1851 Implementation Contract

## Scope

- Runtime owner: `tools/loom.py`.
- Contract regression owner: `tools/check_cli_contract.py`.
- Documentation owners: `README.md`, `README.zh-CN.md`, `docs/methodology/harness/cli-command-matrix.md`, and `src/skills/route-matrix.md`.
- Generated surface owners: `skills/route-matrix.md`, `plugins/loom/skills/route-matrix.md`, and `plugins/loom/.codex-plugin/plugin.json`.
- Loom carrier owners: `.loom/work-items/WI-1851.md`, `.loom/progress/WI-1851.md`, `.loom/status/current.md`, `.loom/reviews/WI-1851.json`, and `.loom/specs/WI-1851/*`.

## Required Behavior

- PR intent prepare/check must emit `loom-shift-left-readiness/v1` with `ready_for_hosted_gate`, structured reasons, and one next command.
- PR intent prepare with `--apply` must run local PR metadata preflight after rendering the body artifact.
- closeout-only and carrier-sync-only profiles must preserve an existing valid `minimal` or `full` suite path instead of forcing formal-suite N/A.
- release closeout-sync may report local readiness and next metadata action, but must not publish, republish, merge, or replace hosted gates.
- `loom help --json`, README, Chinese README, CLI matrix, and generated route matrices must expose the same task-oriented entry paths while keeping low-level commands available.

## Non-Goals

- No hosted gate scheduler.
- No multi-repository upgrade orchestration.
- No command rename or large policy DSL.
- No weakening of review, PR gate, hosted checks, release readback, or closeout evidence.
