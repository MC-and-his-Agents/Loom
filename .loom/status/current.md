# Current Status

## Derived Fact Chain View

- Item ID: WI-1899
- Goal: Update Loom runtime path resolution so `.loom/runtime/**` and `.loom/tmp/**` output artifacts are physically stored under the workstation cache `~/.loom/repos/<repo-id>/`.
- Scope: Add global runtime cache path helpers, update runtime artifact writers/readers in `loom_flow.py` and `tools/loom.py`, preserve logical `.loom/runtime/**` and `.loom/tmp/**` locators for CLI contracts, and update generated/plugin/example runtime copies plus focused contract fixtures.
- Execution Path: issue #1899 -> branch work/1899-global-runtime-paths -> PR -> review/merge-ready/closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1899.md
- Review Entry: .loom/reviews/WI-1899.json
- Validation Entry: python3 -m py_compile tools/loom.py tools/check_cli_contract.py tools/loom_flow.py skills/shared/scripts/runtime_paths.py skills/shared/scripts/loom_flow.py src/skills/shared/scripts/runtime_paths.py src/skills/shared/scripts/loom_flow.py plugins/loom/skills/shared/scripts/runtime_paths.py plugins/loom/skills/shared/scripts/loom_flow.py .loom/bin/runtime_paths.py .loom/bin/loom_flow.py examples/new-project/.loom/bin/runtime_paths.py examples/new-project/.loom/bin/loom_flow.py; python3 tools/check_cli_contract.py --surface runtime-paths --surface pr-metadata --surface runtime-upgrade --surface pr-gate-target-readback; python3 tools/check_cli_contract.py --surface governance-closeout; git diff --check
- Closing Condition: Runtime/tmp outputs default to global workstation cache, repo-local truth carriers remain repo-local, focused runtime path and gate/metadata fixtures pass, PR is merged, and #1899 is closed.
- Current Checkpoint: closed_out
- Current Stop: WI-1899 closed out by controlled merge: PR #1934 merged to main at 024ebb38488ca48fdb52ad465d58d24b0ec63d01, issue #1899 closed, and terminal carrier metadata is being finalized by closeout sync.
- Next Step: No further WI-1899 implementation work remains after closeout carrier sync merge.
- Blockers: None recorded.
- Latest Validation Summary: 2026-07-03T07:25Z local validation passed at head 49805a8e103d34268eb4b6f408d6ff9115157206: `python3 -m py_compile ...`; `git diff --check`; `python3 tools/loom_check.py --source-surface review-run .`; `python3 tools/loom_check.py --source-surface installed-runtime .`; `python3 tools/check_cli_contract.py --surface runtime-paths --surface pr-metadata --surface runtime-upgrade --surface pr-gate-target-readback`; `python3 tools/check_cli_contract.py --surface governance-closeout`; `python3 tools/check_npm_package.py`; `python3 tools/check_release_surface.py`; `make loom-demo-new-project-check`; `python3 tools/loom.py suite validate --target . --item WI-1899 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1899 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1899 --json`.
- Recovery Boundary: WI-1899 covers runtime/tmp output path resolution and focused consumers only. Repo carrier slimdown (#1900), gate independence validation beyond focused fixtures (#1901), workstation upgrade orchestration (#1902), and legacy migration (#1908) remain separate Work Items.
- Current Lane: post-merge-closeout-run

## Runtime Evidence

- Run Entry: 2026-07-03T06:14Z WI-1899 work is active in `/Users/mc/dev/Loom` on branch `work/1899-global-runtime-paths`.
- Logs Entry: Runtime path resolver and focused CLI contract fixtures were authored locally.
- Diagnostics Entry: WI-1899 changes runtime/tmp output placement only; repo carrier slimdown, full gate independence validation, workstation upgrade orchestration, and legacy migration remain out of scope.
- Verification Entry: 2026-07-03T07:42Z post-merge closeout check passed for WI-1899 after PR #1934 merged at 2026-07-03T07:40:27Z and issue #1899 closed at 2026-07-03T07:40:43Z; command: `python3 .loom/bin/loom_flow.py closeout check --target . --item WI-1899 --issue 1899 --pr 1934 --branch main`.
- Lane Entry: post-merge-closeout-run

## Sources

- Static Truth: .loom/work-items/WI-1899.md
- Dynamic Truth: .loom/progress/WI-1899.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
