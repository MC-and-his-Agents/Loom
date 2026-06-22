# Implementation Contract

## Scope

- Owns `tools/loom.py` delivery-command wording and Codex host refresh guidance for target `install`, `upgrade-plan`, and `upgrade`.
- Owns `tools/check_cli_contract.py` targeted assertions for the target repository install/upgrade versus Codex workstation plugin provider boundary.
- Owns README, README.zh-CN, source skills README, generated skills README, and plugin payload skills README wording needed to keep the same command-boundary guidance consistent.
- Owns WI-1720 fact-chain, progress, suite, evidence, task-carrier, review, status, and bootstrap carriers.

## Non-goals

- Do not implement #1714 payload hash generation or comparison.
- Do not implement #1715 source/cache freshness reporting, `loom version --json` plugin freshness output, or upgrade-plan freshness decisions.
- Do not implement #1721 source / marketplace / runtime cache readback.
- Do not implement #1722 legacy single-skill installer retirement.
- Do not change `packages/loom-installer/**`, release version files, npm publish metadata, GitHub release state, or tag state.
- Do not introduce a new parallel `loom plugin ...` command surface.

## Invariants

- `loom install --target <repo>` and `loom upgrade --target <repo>` manage target repository installed-state / adoption metadata only.
- Codex workstation plugin provider inspection, install, registration, and refresh guidance remains on `loom host doctor|install|register --host codex --scope user`.
- `--host codex` may add a separate host refresh guidance action to target install/upgrade output, but that action must not imply the target repository command refreshes the Codex runtime cache.
- Generated `skills/` and `plugins/loom/skills/` payload copies must remain byte-for-byte synchronized with `src/skills/` for files in this scope.
- #1720 must not claim release, payload hash, plugin payload version, or source/cache freshness behavior that belongs to later Work Items.

## Validation Contract

- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface adoption-host-metadata`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`
- `npm --prefix packages/loom-installer run check:distribution`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py fact-chain --target . --item WI-1720 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1720 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1720 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1720 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 skills/loom-build/scripts/loom-build.py flow build --target . --item WI-1720 --build-evidence .loom/progress/WI-1720-build-evidence.json`

## Review Boundary

- Review must consume the current PR head, PR metadata readback, generated skills surface check, installer distribution check, targeted CLI contract evidence, suite evidence, and forbidden-surface diff.
- Re-run review if CLI output, contract checks, README guidance, generated skills payload copies, WI-1720 carriers, PR metadata, or head SHA changes after the review record is written.
