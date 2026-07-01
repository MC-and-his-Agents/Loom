# WI-1859 Implementation Contract

## Scope

- Runtime owner: `tools/loom.py`.
- Contract regression owner: `tools/check_cli_contract.py`.
- Documentation owners: `README.md`, `README.zh-CN.md`, `docs/methodology/harness/cli-command-matrix.md`, and `src/skills/route-matrix.md`.
- Generated surface owners: `skills/route-matrix.md`, `plugins/loom/skills/route-matrix.md`, and `plugins/loom/.codex-plugin/plugin.json`.
- Loom carrier owners: `.loom/work-items/WI-1859.md`, `.loom/progress/WI-1859.md`, `.loom/status/current.md`, `.loom/reviews/WI-1859.json`, and `.loom/specs/WI-1859/*`.

## Required Behavior

- `loom runtime-upgrade pr` must render maintenance PR metadata, optionally create/update the host PR only under explicit `--create`/`--update`, read back metadata when a PR exists, and keep hosted gate readiness false until readback is available.
- `loom runtime-upgrade closeout` must use issue readback for issue state/closedAt and Loom host-binding PR readback for PR merge state/merge commit/target branch/status check URL.
- `loom runtime-upgrade closeout --sync` may write only repo carrier/recovery/shadow surfaces and must not publish, republish, merge, or close unrelated product issues.
- Carrier-only review guidance must explicitly say it covers terminal carrier metadata drift only and does not approve product implementation.
- README, Chinese README, CLI matrix, and generated route matrices must expose the same runtime-upgrade lane order: status -> prepare -> pr -> check -> closeout.

## Non-Goals

- No multi-repository batch mode.
- No default automatic merge.
- No default product issue closeout.
- No hosted gate scheduler.
- No large policy DSL or broad command rename.
- No weakening of review, PR gate, hosted checks, release readback, or closeout evidence.
