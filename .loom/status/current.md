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
- Current Checkpoint: review
- Current Stop: PR #1934 gate readback exposed stale bootstrap carrier hashes and missing spec review; bootstrap fact-chain/hash carrier has been repaired locally and suite validation is green.
- Next Step: Commit bootstrap carrier repair, record spec review, refresh implementation review and PR metadata, then rerun PR gate and hosted checks.
- Blockers: None recorded.
- Latest Validation Summary: 2026-07-03T06:14Z local validation passed: `python3 -m py_compile ...`; `python3 tools/check_cli_contract.py --surface runtime-paths --surface pr-metadata --surface runtime-upgrade --surface pr-gate-target-readback`; `python3 tools/check_cli_contract.py --surface governance-closeout`; `git diff --check`. 2026-07-03T06:18Z suite validate/evidence/carrier validate passed for WI-1899 after carrier mapping fixes. 2026-07-03T06:29Z bootstrap carrier repaired for WI-1899 current item and `.loom/bin` runtime hashes; `python3 tools/loom.py suite validate --target . --item WI-1899 --json`, `python3 tools/loom.py suite evidence validate --target . --item WI-1899 --json`, `python3 tools/loom.py suite carrier validate --target . --item WI-1899 --json`, and `git diff --check` passed.
- Recovery Boundary: WI-1899 covers runtime/tmp output path resolution and focused consumers only. Repo carrier slimdown (#1900), gate independence validation beyond focused fixtures (#1901), workstation upgrade orchestration (#1902), and legacy migration (#1908) remain separate Work Items.
- Current Lane: implementation-validation

## Runtime Evidence

- Run Entry: 2026-07-03T06:14Z WI-1899 work is active in `/Users/mc/dev/Loom` on branch `work/1899-global-runtime-paths`.
- Logs Entry: Runtime path resolver and focused CLI contract fixtures were authored locally.
- Diagnostics Entry: WI-1899 changes runtime/tmp output placement only; repo carrier slimdown, full gate independence validation, workstation upgrade orchestration, and legacy migration remain out of scope.
- Verification Entry: 2026-07-03T06:14Z local validation passed: py_compile for touched Python runtime copies; runtime-paths/pr-metadata/runtime-upgrade/pr-gate-target-readback surfaces; governance-closeout surface; git diff --check. 2026-07-03T06:18Z suite validate/evidence/carrier validate passed for WI-1899. 2026-07-03T06:29Z bootstrap carrier current item/hash repair validated with suite validate/evidence/carrier and git diff --check.
- Lane Entry: implementation-validation

## Sources

- Static Truth: .loom/work-items/WI-1899.md
- Dynamic Truth: .loom/progress/WI-1899.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
