# Current Status

## Derived Fact Chain View

- Item ID: WI-1713
- Goal: 在 Codex 插件 payload manifest 中写入 release 绑定 metadata，让安装态能读出来源 package、payload version、payload hash 和 release commit 绑定状态。
- Scope: Issue #1713 only. Update `plugins/loom/.codex-plugin/plugin.json`, plugin payload hash validation, version surface checks, `loom` version context, targeted tests, and WI-1713 carriers. Ownership: plugin release metadata fields, deterministic hash self-reference normalization, package/version contract checks, and WI-1713 carriers only. Non-goals: no #1721 source/cache readback, no #1715 freshness reporting, no #1716 refresh guidance, no #1722 legacy installer retirement, no version bump, no npm publish, no GitHub release.
- Execution Path: issue #1713 -> branch `work/1713-plugin-release-metadata` -> worktree `.loom/..` -> targeted validation -> PR -> controlled merge -> closeout.
- Workspace Entry: `.loom/..`
- Recovery Entry: `.loom/progress/WI-1713.md`
- Review Entry: `.loom/reviews/WI-1713.json`
- Validation Entry: `PYTHONDONTWRITEBYTECODE=1 python3 test/plugin_payload_hash_test.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/version_surface_check.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/check_npm_package.py tools/version_surface_check.py tools/loom.py`; `npm --prefix packages/loom-installer run check:versions`; `npm --prefix packages/loom-installer run check:distribution`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_release_surface.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`; `npm run test:package`; Loom fact-chain, suite, and build validations.
- Closing Condition: PR for `work/1713-plugin-release-metadata` is merged into `main`, issue #1713 is closed, and closeout consumes PR, issue, branch, target branch, hosted checks, and repo carrier readback.
- Current Checkpoint: review checkpoint
- Current Stop: Metadata/hash implementation, suite validation, build evidence, CLI contract aggregate check, and `make loom-check` classification are complete for the implementation head.
- Next Step: Commit the implementation head, record spec and implementation review carriers, refresh shadow evidence, then run PR metadata and controlled merge gates.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-22 local validation passed for WI-1713 implementation scope: `PYTHONDONTWRITEBYTECODE=1 python3 test/plugin_payload_hash_test.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py --surface plugin-payload-hash`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/version_surface_check.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/check_npm_package.py tools/version_surface_check.py tools/loom.py`; `npm --prefix packages/loom-installer run check:versions`; `npm --prefix packages/loom-installer run check:distribution`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_release_surface.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`; `npm run test:package`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py fact-chain --target . --item WI-1713 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1713 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1713 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1713 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py version --json`; `PYTHONDONTWRITEBYTECODE=1 python3 skills/loom-build/scripts/loom-build.py flow build --target . --item WI-1713 --build-evidence .loom/progress/WI-1713-build-evidence.json`; `npm --prefix packages/loom-installer run check:docs`; `npm --prefix packages/loom-installer run check:hosts`; `npm --prefix packages/loom-installer run check:payload`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface aggregate`; `git diff --check`. `make loom-check` completed all surfaces except root-self-adoption, which correctly blocked on missing WI-1713 review artifacts and stale status-derived shadow hashes before review carrier refresh.
- Recovery Boundary: WI-1713 owns release metadata fields, plugin payload hash self-reference normalization, and local package/version checks. It does not implement source/cache runtime freshness comparison or plugin refresh commands.
- Current Lane: plugin-release-metadata

## Runtime Evidence

- Run Entry: 2026-06-22 WI-1713 build started in issue-scoped worktree `work/1713-plugin-release-metadata`.
- Logs Entry: Local validation output retained in this Codex thread and summarized in `.loom/progress/WI-1713.md`.
- Diagnostics Entry: `x-loom.plugin_payload_hash` is normalized during digest computation; other plugin manifest metadata remains part of the payload evidence.
- Verification Entry: Targeted checks, suite validation, build flow, version readback, package checks, and CLI contract aggregate checks passed before review carrier generation.
- Lane Entry: plugin-release-metadata

## Sources

- Static Truth: `.loom/work-items/WI-1713.md`
- Dynamic Truth: `.loom/progress/WI-1713.md`
- Locator Truth: `.loom/bootstrap/init-result.json`
- Fact Chain CLI: `python3 .loom/bin/loom_init.py fact-chain --target .`
