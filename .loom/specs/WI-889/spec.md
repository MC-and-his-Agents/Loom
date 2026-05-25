# WI-889 Spec

## Goal

Make the #885 CLI-first phase expose the delivery, scenario, and installer compatibility surfaces through the top-level Loom CLI.

## Acceptance

- `loom install`, `loom upgrade-plan`, `loom upgrade`, `loom rollback`, and `loom verify` are declared implemented in the CLI command contract.
- Delivery commands emit stable JSON contracts and fail closed when mutation authority or host inputs are missing.
- `install` writes installed state only with `--apply`; read-only planning paths do not mutate project state.
- `upgrade-plan` classifies current, repair, mixed-legacy, and legacy surfaces without mutating the target.
- `upgrade` requires `--apply` and blocks when installed state is invalid or legacy surfaces remain unresolved.
- `rollback` remains non-mutating and fail-closed until rollback/delete ownership has an authored artifact.
- `loom story`, `loom spec`, `loom plan`, `loom build`, `loom pre-review`, `loom closeout`, `loom handoff`, and `loom retire` are declared implemented and route through CLI-backed flow or carrier locators.
- Scenario commands preserve existing flow/checkpoint semantics instead of creating new host behavior.
- `loom-installer` remains the compatibility shim under the host adapter while top-level CLI owns command semantics.
- `tools/check_cli_contract.py` verifies #910-#914, #924-#928, and #944-#947 command contracts.

## Non-Goals

- Do not consume #897 legacy repository migration validation in this batch.
- Do not consume #996 release readiness, npm publish, tag, or release judgment in this batch.
- Do not implement mutating rollback/delete ownership.
- Do not broaden into profile finalization, bottom-layer GitHub/CI/review/worktree rewrites, or repo-specific guardian replacement.
