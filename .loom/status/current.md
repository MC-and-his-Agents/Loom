# Current Status

## Derived Fact Chain View

- Item ID: WI-1720
- Goal: 明确 CLI install/upgrade 与 host plugin refresh 的命令边界，让用户能区分目标仓库启用 Loom 与刷新本机 Codex 插件。
- Scope: Issue #1720 only. Update `tools/loom.py` target install/upgrade/upgrade-plan output wording and host guidance payload, targeted `tools/check_cli_contract.py` contract checks, minimal README / README.zh-CN / `src/skills/README.md` docs sync, and WI-1720 Loom carriers. Ownership: target install/upgrade wording, host guidance payload, targeted CLI contract checks, minimal docs sync, and WI-1720 carriers only. Non-goals: no #1715 freshness report, no #1714 hash semantics, no payload hash implementation, no `packages/loom-installer/**`, no release version, no npm publish/release files, no new parallel `loom plugin ...` command surface.
- Execution Path: issue #1720 -> branch `work/1720-host-command-boundary-v2` -> worktree `.loom/..` -> targeted validation -> PR -> controlled merge -> closeout.
- Workspace Entry: `.loom/..`
- Recovery Entry: `.loom/progress/WI-1720.md`
- Review Entry: `.loom/reviews/WI-1720.json`
- Validation Entry: `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface adoption-host-metadata`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`; `npm --prefix packages/loom-installer run check:distribution`; `git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py fact-chain --target . --item WI-1720 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1720 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1720 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1720 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 skills/loom-build/scripts/loom-build.py flow build --target . --item WI-1720 --build-evidence .loom/progress/WI-1720-build-evidence.json`.
- Closing Condition: PR for `work/1720-host-command-boundary-v2` is merged into `main`, issue #1720 is closed, and closeout consumes PR, issue, branch, target branch, hosted checks, and repo carrier readback.
- Current Checkpoint: merge checkpoint
- Current Stop: Spec review, implementation review, PR metadata readback, and local PR metadata preflight are recorded; PR gate and hosted checks remain.
- Next Step: Commit merge-checkpoint carrier update, refresh PR metadata for the new head, rerun PR gate, then wait for hosted checks before controlled merge.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-22T12:23Z local validation passed after adding `.loom/specs/WI-1720/implementation-contract.md` and regenerating skills payload README copies: `git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface adoption-host-metadata`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`; `npm --prefix packages/loom-installer run check:distribution`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py fact-chain --target . --item WI-1720 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1720 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1720 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1720 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 skills/loom-build/scripts/loom-build.py flow build --target . --item WI-1720 --build-evidence .loom/progress/WI-1720-build-evidence.json`.
- Recovery Boundary: WI-1720 owns only target install/upgrade wording and host guidance payload, targeted CLI contract checks, minimal docs sync, and WI-1720 carriers. It does not implement freshness reports, payload hash comparison, release/version changes, package publishing, `packages/loom-installer/**`, or host plugin source/cache readback.
- Current Lane: host-command-boundary

## Runtime Evidence

- Run Entry: 2026-06-22 WI-1720 build started in the issue-scoped worktree for branch `work/1720-host-command-boundary-v2`.
- Logs Entry: Local validation output retained in this Codex thread and summarized in `.loom/progress/WI-1720.md`.
- Diagnostics Entry: `loom install/upgrade --target <repo>` is target repository installed-state/adoption metadata only; `loom host doctor|install|register --host codex --scope user` owns Codex workstation plugin provider inspection, installation, registration, and refresh guidance.
- Verification Entry: 2026-06-22T12:36Z PR metadata readback and metadata preflight passed for WI-1720 on `work/1720-host-command-boundary-v2`; local PR gate reported review and suite inputs consumable but recovery checkpoint still needed promotion to merge checkpoint.
- Lane Entry: host-command-boundary

## Sources

- Static Truth: `.loom/work-items/WI-1720.md`
- Dynamic Truth: `.loom/progress/WI-1720.md`
- Locator Truth: `.loom/bootstrap/init-result.json`
- Fact Chain CLI: `python3 .loom/bin/loom_init.py fact-chain --target .`
