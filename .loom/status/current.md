# Current Status

## Derived Fact Chain View

- Item ID: WI-1486
- Goal: 更新 Codex 用户级 plugin payload 中的可执行技能，让恢复、构建、审查、merge-ready 和交接流程默认使用全局 `loom` CLI 的摘要与工件定位输出。
- Scope: #1486 skill payload only: update `src/skills`, generated `skills`, and `plugins/loom/skills` so executable command examples and output contracts use global `loom` CLI agent-safe summary/artifact locator defaults and explicit `--full-output` only for debugging. Ownership constraints are limited to `src/skills`, generated `skills`, `plugins/loom/skills`, `tools/check_cli_contract.py`, demo bootstrap fixture files under `examples/new-project/.loom`, `.loom/work-items/WI-1486.md`, `.loom/progress/WI-1486.md`, `.loom/progress/WI-1486-build-evidence.json`, `.loom/reviews/WI-1486.json`, `.loom/reviews/WI-1486.spec.json`, `.loom/status/current.md`, `.loom/shadow/merge-ready-loom.json`, `.loom/shadow/closeout-loom.json`, `.loom/specs/WI-1486`, and PR #1667 metadata. Do not update README, migration docs, ordinary help text, release evidence, package metadata, or downstream repository instructions.
- Execution Path: issue #1486 -> branch work/1486-agent-safe-skills -> PR pending -> merge -> issue closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1486.md
- Review Entry: .loom/reviews/WI-1486.json
- Validation Entry: python3 tools/skills_surface.py check --surface generated-tree-drift --surface plugin-payload-metadata --surface reference-integrity; targeted stale command rg; python3 tools/py_compile_clean.py tools/check_cli_contract.py tools/loom.py skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_flow.py plugins/loom/skills/shared/scripts/loom_flow.py; python3 tools/loom.py suite validate --target . --item WI-1486 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1486 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1486 --json; python3 tools/loom.py fact-chain --target . --json; python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1486 --write; python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; python3 tools/loom.py pr metadata-preflight --surface merge_ready --body-file .loom/tmp/pr/WI-1486-pr-body.md --compare-body-file .loom/tmp/pr/WI-1486-pr-readback.md --json; python3 tools/check_demo_bootstrap_fixture.py --surface fixture-drift; python3 tools/check_cli_contract.py; git diff --check
- Closing Condition: PR merged after local/hosted gates prove the Codex user-level plugin skill payload calls global `loom` CLI agent-safe output paths by default, full diagnostics remain explicit, generated mirrors and plugin payload are synchronized, and #1486 closeout evidence is recorded without changing #1488/#1658/#1489 scope.
- Current Checkpoint: merge checkpoint
- Current Stop: PR #1667 is at head c26d5e7bde48da85998daa7af6b3dcbd72702332 with skill payload, CLI contract, demo fixture, build evidence, review, shadow, and PR metadata carriers aligned for merge-ready validation.
- Next Step: Run build with .loom/progress/WI-1486-build-evidence.json, refresh current-head review binding if needed, rerun carrier/fact/shadow/PR gate, then wait for hosted checks.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-21 WI-1486 validation passed on branch work/1486-agent-safe-skills after PR #1667 gate blocker fixes: python3 tools/skills_surface.py check --surface generated-tree-drift --surface plugin-payload-metadata --surface reference-integrity; targeted rg for stale repo-local script / CLI JSON wording returned no matches; python3 tools/py_compile_clean.py tools/check_cli_contract.py tools/loom.py skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_flow.py plugins/loom/skills/shared/scripts/loom_flow.py; python3 tools/loom.py suite validate --target . --item WI-1486 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1486 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1486 --json; python3 tools/loom.py fact-chain --target . --json; python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1486 --write; python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; python3 tools/loom.py pr metadata-preflight --surface merge_ready --body-file .loom/tmp/pr/WI-1486-pr-body.md --compare-body-file .loom/tmp/pr/WI-1486-pr-readback.md --json; python3 tools/check_demo_bootstrap_fixture.py --surface fixture-drift; python3 tools/check_cli_contract.py; git diff --check.
- Recovery Boundary: WI-1486 skill payload only. Do not update README/help/migration docs (#1488), release evidence (#1658), final regression closeout (#1489), downstream repositories, or old installer compatibility in this Work Item.
- Current Lane: milestone-11-agent-safe-skills

## Runtime Evidence

- Run Entry: 2026-06-21 WI-1486 skill payload update in progress.
- Logs Entry: local command output retained in current Codex milestone/11 thread.
- Diagnostics Entry: Skill payload now defaults to global `loom` CLI agent-safe summary/artifact locator output and explicit `--full-output` only for debugging; user docs/help/migration remain deferred to #1488.
- Verification Entry: `python3 tools/skills_surface.py check --surface generated-tree-drift --surface plugin-payload-metadata --surface reference-integrity`; targeted stale-command `rg`; `python3 tools/py_compile_clean.py tools/check_cli_contract.py tools/loom.py skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_flow.py plugins/loom/skills/shared/scripts/loom_flow.py`; `python3 tools/loom.py suite validate --target . --item WI-1486 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1486 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1486 --json`; `python3 tools/loom.py fact-chain --target . --json`; `python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1486 --write`; `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`; `python3 tools/loom.py pr metadata-preflight --surface merge_ready --body-file .loom/tmp/pr/WI-1486-pr-body.md --compare-body-file .loom/tmp/pr/WI-1486-pr-readback.md --json`; `python3 tools/check_demo_bootstrap_fixture.py --surface fixture-drift`; `python3 tools/check_cli_contract.py`; `git diff --check`.
- Lane Entry: milestone-11-agent-safe-skills

## Sources

- Static Truth: .loom/work-items/WI-1486.md
- Dynamic Truth: .loom/progress/WI-1486.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
