# Current Status

## Derived Fact Chain View

- Item ID: WI-1554
- Goal: Harden the top-level Loom CLI wrapper to runtime argument contract for high-risk operator gates.
- Scope: Reopened #1554 regression slice: pass `--surface` through `loom pr gate`, let runtime `pr-gate` consume explicit or PR-body metadata surface for terminal closeout carrier PRs, refresh generated/demo runtime surfaces, and add focused wrapper plus governance-closeout regressions. Do not implement #1555 one-shot closeout run, hosted admission, release/no-release closeout, classifier taxonomy, or closeout profile semantics.
- Execution Path: issue #1554 -> branch work/1554-pr-gate-closeout-surface -> pr-gate surface passthrough/runtime consumption -> generated/demo runtime sync -> focused merge-wrapper/pr-metadata/governance-closeout contract surfaces -> PR #1570 metadata/readback -> review/merge-ready
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1554.md
- Review Entry: .loom/reviews/WI-1554.json
- Validation Entry: PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py skills/loom-adopt/.loom-runtime/shared/scripts/loom_flow.py skills/loom-build/.loom-runtime/shared/scripts/loom_flow.py skills/loom-handoff/.loom-runtime/shared/scripts/loom_flow.py skills/loom-init/.loom-runtime/shared/scripts/loom_flow.py skills/loom-merge-ready/.loom-runtime/shared/scripts/loom_flow.py skills/loom-pre-review/.loom-runtime/shared/scripts/loom_flow.py skills/loom-resume/.loom-runtime/shared/scripts/loom_flow.py skills/loom-retire/.loom-runtime/shared/scripts/loom_flow.py skills/loom-review/.loom-runtime/shared/scripts/loom_flow.py skills/loom-spec-review/.loom-runtime/shared/scripts/loom_flow.py skills/loom-story/.loom-runtime/shared/scripts/loom_flow.py tools/loom.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper --surface pr-metadata; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout; PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift; make loom-demo-new-project-check; git diff --check
- Closing Condition: PR #1570 is merged, issue #1554 is closed after PR gate surface contract evidence and closeout carrier sync are read back, and #1514/#1534/#1515 can consume #1554 as complete.
- Current Checkpoint: merge
- Current Stop: PR #1571 is open at carrier-aligned head d14c3af49f949401356f44c0244407eb609bd17a for the reopened closeout runtime `--item` contract slice: repo-local closeout parser, retained-item lookup, bootstrap manifest hash, review evidence, and focused governance-closeout regressions are updated; PR metadata readback is fresh.
- Next Step: Refresh review evidence for PR #1571 current head, then wait for hosted checks and run merge gate before controlled merge.
- Blockers: None
- Latest Validation Summary: 2026-06-18T02:53Z targeted validation passed for PR #1571 carrier-aligned head d14c3af49f949401356f44c0244407eb609bd17a: PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile .loom/bin/loom_flow.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py runtime-state --target .; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py verify --target .; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .; PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py pr metadata-readback 1571 --surface merge_ready --readback-file .loom/runtime/pr/WI-1554-closeout-item-runtime-contract-readback.md --json; CODEX_EXPORT_GH_TOKEN=1 PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py closeout check --target . --item WI-1554 --issue 1554 --pr 1570 --branch work/1554-pr-gate-closeout-surface reached expected business closeout blocker instead of runtime crash; git diff --check.
- Recovery Boundary: Current reopened #1554 slice is limited to CLI wrapper/runtime PR gate surface contract and generated/demo runtime sync. It does not implement #1555 one-shot post-merge closeout run, hosted admission, release/no-release closeout, classifier taxonomy, closeout freeze/profile behavior, or closeout gate semantic changes.
- Current Lane: milestone-12-wave0-cli-wrapper-closeout-item-runtime

## Runtime Evidence

- Run Entry: 2026-06-18 WI-1554 closeout runtime item contract regression slice; PR #1571
- Logs Entry: local command output retained in current Codex thread
- Diagnostics Entry: WI-1554 reopened to fix pr-gate metadata surface consumption after #1542 closeout carrier PR exposed merge_ready preflight drift for closeout-only PR bodies.
- Verification Entry: `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile .loom/bin/loom_flow.py tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py runtime-state --target .`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py verify --target .`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py pr metadata-readback 1571 --surface merge_ready --readback-file .loom/runtime/pr/WI-1554-closeout-item-runtime-contract-readback.md --json`; `CODEX_EXPORT_GH_TOKEN=1 PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py closeout check --target . --item WI-1554 --issue 1554 --pr 1570 --branch work/1554-pr-gate-closeout-surface`; `git diff --check`.
- Lane Entry: milestone-12-wave0-cli-wrapper-closeout-item-runtime

## Sources

- Static Truth: .loom/work-items/WI-1554.md
- Dynamic Truth: .loom/progress/WI-1554.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
