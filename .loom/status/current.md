# Current Status

## Derived Fact Chain View

- Item ID: WI-1641-1630-1632
- Goal: 完成 milestone #14 PR2：让 Codex plugin payload 成为唯一 skills 发布形态，删除 single-skill package 分发语义，并把 plugin manifest/skills payload 改成用户级 provider 语义。
- Scope: issue #1641、#1630、#1632；允许修改 skills 生成/校验工具、`plugins/loom` payload、npm package surface、相关 adoption 文档、generated skills mirror，以及本 Work Item carrier。
- Execution Path: issue #1641/#1630/#1632 -> branch `work/1641-plugin-payload-only` -> PR2 -> targeted checks -> hosted gate -> merge -> issue closeout。
- Workspace Entry: .
- Recovery Entry: `.loom/progress/WI-1641-1630-1632.md`
- Review Entry: `.loom/reviews/WI-1641-1630-1632.json`
- Validation Entry: `python3 tools/skills_surface.py check`; `python3 tools/version_surface_check.py`; `python3 tools/check_npm_package.py`; `python3 tools/host_adapter_check.py`; `python3 tools/check_release_surface.py`; `python3 tools/check_cli_contract.py --surface aggregate`; `make py-compile`; `git diff --check`
- Closing Condition: PR2 merges into `main`, issues #1641/#1630/#1632 are closed or linked to the merged PR, and repo carriers consume the merge/head/check evidence without starting PR3.
- Current Checkpoint: build checkpoint
- Current Stop: PR2 implementation is locally complete on `work/1641-plugin-payload-only`; generated skill package metadata and package-internal `.loom-runtime` payloads have been removed from generated surfaces, and `plugins/loom/skills/` is generated as the Codex user plugin payload.
- Next Step: Commit, push, open PR2, bind PR metadata, run hosted gate, review, merge-ready, and close issues #1641/#1630/#1632 after merge evidence is consumed.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-20 local PR2 validation passed: `python3 tools/skills_surface.py check`; `python3 tools/version_surface_check.py`; `python3 tools/check_npm_package.py`; `python3 tools/host_adapter_check.py`; `python3 tools/check_release_surface.py`; `python3 tools/loom.py skills package --json`; `python3 tools/loom.py skills release-check --json`; `make py-compile`; `python3 tools/check_cli_contract.py --surface adoption-host-metadata`; `python3 tools/check_cli_contract.py --surface aggregate`; `python3 tools/loom.py suite validate --target . --item WI-1641-1630-1632 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1641-1630-1632 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1641-1630-1632 --json`; `git diff --check`; generated payload scan found no `loom-package.json` or `.loom-runtime` under `skills` or `plugins/loom/skills`.
- Recovery Boundary: PR2 only. Do not implement PR3 user-level plugin install/register, PR4 CLI command deletion, PR5 migration/gate convergence, or v0.17.0 release execution in this lane.
- Current Lane: milestone-14-pr2-plugin-payload

## Runtime Evidence

- Run Entry: 2026-06-20 PR2 plugin payload implementation lane
- Logs Entry: local command output retained in current Codex milestone/14 thread
- Diagnostics Entry: PR2 carrier activated after PR1 closeout left repository in `no_active_item` idle state; plugin payload generation, package surface, and installed runtime fixtures now consume `plugins/loom/skills` rather than single-skill package metadata.
- Verification Entry: `python3 tools/skills_surface.py check`; `python3 tools/version_surface_check.py`; `python3 tools/check_npm_package.py`; `python3 tools/host_adapter_check.py`; `python3 tools/check_release_surface.py`; `python3 tools/loom.py skills package --json`; `python3 tools/loom.py skills release-check --json`; `make py-compile`; `python3 tools/check_cli_contract.py --surface adoption-host-metadata`; `python3 tools/check_cli_contract.py --surface aggregate`; suite validate/evidence/carrier; `git diff --check`.
- Lane Entry: milestone-14-pr2-plugin-payload

## Sources

- Static Truth: `.loom/work-items/WI-1641-1630-1632.md`
- Dynamic Truth: `.loom/progress/WI-1641-1630-1632.md`
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
