# Implementation Contract

## Scope

- Retire `packages/loom-installer` as a tombstone package.
- Remove active plugin, single-skill, upgrade, verify, payload build, payload drift, and version bump behavior from the installer package.
- Keep only fail-closed CLI output, tombstone README guidance, package regression checks, CI/release guard updates, and root self-plugin source payload validation.

## Required Behavior

- Every `loom-installer` CLI invocation exits non-zero.
- JSON output reports `status: blocked`, `distribution_layer: tombstone-package`, `failed_layer: legacy-installer`, and migration commands for `@mc-and-his-agents/loom` plus `loom host ...`.
- Text output points users to the same root Loom CLI and Codex host plugin commands.
- `packages/loom-installer` must not install plugin payloads, install single skills, write host state, write target repo state, calculate payload freshness, or declare upgrade success.
- CI and release checks must not require active installer behavior tests or installer behavior version bumps.
- `npm deprecate @mc-and-his-agents/loom-installer` remains outside this PR and requires separate release-closeout confirmation.

## Allowed Paths

- `packages/loom-installer/**`
- `.github/workflows/node-installer-pr.yml`
- `.github/workflows/node-installer-release.yml`
- `tools/check_release_surface.py`
- `skills/shared/scripts/loom_check.py`
- `src/skills/shared/scripts/loom_check.py`
- `plugins/loom/skills/shared/scripts/loom_check.py`
- `.loom/**/WI-1732*`

## Validation Binding

- `npm --prefix packages/loom-installer run check:release`
- `node packages/loom-installer/scripts/run-regression.mjs`
- `python3 tools/check_loom_check_runtime_regressions.py --surface installer-regression-lock-output`
- `python3 tools/check_release_surface.py --surface installer-sunset-guard`
- `python3 tools/skills_surface.py check --surface generated-tree-drift`
- `python3 tools/py_compile_clean.py skills/shared/scripts/loom_check.py src/skills/shared/scripts/loom_check.py plugins/loom/skills/shared/scripts/loom_check.py`
- `git diff --check`
- Loom suite, evidence, carrier, and fact-chain validation for `WI-1732`
