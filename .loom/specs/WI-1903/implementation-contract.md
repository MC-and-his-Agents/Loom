# WI-1903 Implementation Contract

## CLI Contract

- `loom workstation upgrade --plan --to <version> --json` is the only implemented upgrade sub-surface in this WI.
- Missing `--plan` or missing `--to` fails before reading or writing registry state.
- The output schema is `loom-workstation-upgrade-plan/v1`.
- `plan_only` is `true` and `mutates` is `false`.

## Machine Plan Contract

- The machine plan classification is `machine_only`.
- It may include commands for npm CLI refresh, Codex plugin install/register, and host doctor readback.
- These commands are future apply guidance only; this command does not execute them.

## Repository Plan Contract

- `repo_noop`: opted-out repositories or metadata-only repositories already at the requested target version.
- `repo_auto_commit_candidate`: metadata-only repositories below the requested target version.
- `repo_pr_required`: `repo-local-wrapper` or `legacy-embedded` repositories.
- `blocked`: blocking registry drift, unsupported schema/entry shape, missing path, remote hash drift, duplicate id, or unknown adoption mode.

## Runtime Fixture Contract

- Execution-attempt missing-evidence fixture must delete both the resolved runtime latest locator and the legacy repo-local fallback latest file before asserting missing state.
- Runtime copy hash carriers must be refreshed whenever the demo `.loom/bin/loom_check.py` copy changes.
