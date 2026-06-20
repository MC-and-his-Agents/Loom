# Current Status

## Derived Fact Chain View

- Item ID: WI-1486
- Goal: 更新 Codex 用户级 plugin payload 中的可执行技能，让恢复、构建、审查、merge-ready 和交接流程默认使用全局 `loom` CLI 的摘要与工件定位输出。
- Scope: #1486 skill payload only: update `src/skills`, generated `skills`, and `plugins/loom/skills` so executable command examples and output contracts use global `loom` CLI agent-safe summary/artifact locator defaults and explicit `--full-output` only for debugging. Do not update README, migration docs, ordinary help text, release evidence, package metadata, or downstream repository instructions.
- Execution Path: issue #1486 -> branch work/1486-agent-safe-skills -> PR pending -> merge -> issue closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1486.md
- Review Entry: .loom/reviews/WI-1486.json
- Validation Entry: python3 tools/skills_surface.py check --surface generated-tree-drift --surface plugin-payload-metadata --surface reference-integrity; targeted stale command rg; python3 -m py_compile src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py plugins/loom/skills/shared/scripts/loom_flow.py; python3 tools/loom.py suite validate --target . --item WI-1486 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1486 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1486 --json; python3 tools/loom.py fact-chain --target . --json; python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; git diff --check
- Closing Condition: PR merged after local/hosted gates prove the Codex user-level plugin skill payload calls global `loom` CLI agent-safe output paths by default, full diagnostics remain explicit, generated mirrors and plugin payload are synchronized, and #1486 closeout evidence is recorded without changing #1488/#1658/#1489 scope.
- Current Checkpoint: build checkpoint
- Current Stop: Source skills, generated mirrors, and Codex user plugin payload have been updated on branch work/1486-agent-safe-skills; targeted validation passed and review record is bound to implementation head 9d641431733b2e6c0a730fedace4da2d76b93c26.
- Next Step: Refresh carriers after review binding, open PR, update PR metadata, and proceed through PR gate.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-21 WI-1486 targeted validation passed on branch work/1486-agent-safe-skills: `python3 tools/skills_surface.py check --surface generated-tree-drift --surface plugin-payload-metadata --surface reference-integrity`; targeted `rg` for stale repo-local script / CLI JSON wording returned no matches; `python3 -m py_compile src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py plugins/loom/skills/shared/scripts/loom_flow.py`; `python3 tools/loom.py suite validate --target . --item WI-1486 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1486 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1486 --json`; `git diff --check`.
- Recovery Boundary: WI-1486 skill payload only. Do not update README/help/migration docs (#1488), release evidence (#1658), final regression closeout (#1489), downstream repositories, or old installer compatibility in this Work Item.
- Current Lane: milestone-11-agent-safe-skills

## Runtime Evidence

- Run Entry: 2026-06-21 WI-1486 skill payload update in progress.
- Logs Entry: local command output retained in current Codex milestone/11 thread.
- Diagnostics Entry: Skill payload now defaults to global `loom` CLI agent-safe summary/artifact locator output and explicit `--full-output` only for debugging; user docs/help/migration remain deferred to #1488.
- Verification Entry: `python3 tools/skills_surface.py check --surface generated-tree-drift --surface plugin-payload-metadata --surface reference-integrity`; targeted stale-command `rg`; `python3 -m py_compile src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py plugins/loom/skills/shared/scripts/loom_flow.py`; `python3 tools/loom.py suite validate --target . --item WI-1486 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1486 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1486 --json`; `git diff --check`.
- Lane Entry: milestone-11-agent-safe-skills

## Sources

- Static Truth: .loom/work-items/WI-1486.md
- Dynamic Truth: .loom/progress/WI-1486.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
