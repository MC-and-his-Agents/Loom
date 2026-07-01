# Current Status

## Derived Fact Chain View

- Item ID: WI-1876
- Goal: 修复 target 绑定的 full_output artifact locator，并作为 v0.26.2 发布线交付。
- Scope: Loom CLI target-aware command output artifact emission/readback contract: bind default relative artifact output to resolved `--target` root, preserve `LOOM_OUTPUT_ARTIFACT_DIR` explicit override, cover `build` and `fact-chain` plus npm/global wrapper regression, then complete PR #1878, review/gate, v0.26.2 release readback, and closeout. Ownership is limited to the runtime contract, focused tests, contract helper, CLI command matrix documentation, WI-1876 carriers, PR #1878 metadata, and v0.26.2 closeout for this fix.
- Execution Path: issue #1876 -> branch work/1876-target-output-artifacts -> PR #1878 -> implementation review/gate -> merge -> v0.26.2 release -> release readback -> terminal closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1876.md
- Review Entry: .loom/reviews/WI-1876.json
- Validation Entry: output envelope and target resolution tests, real Node wrapper build/fact-chain readback probes, CLI contract aggregate, PR gate, release readback.
- Closing Condition: PR #1878 merged, v0.26.2 tag/GitHub Release/npm package read back consistently, and #1876/#1878 terminal carrier closeout is synced.
- Current Checkpoint: merge
- Current Stop: implementation review is recorded in `.loom/reviews/WI-1876.json`, PR #1878 metadata is read back at head `e2efc09e9d696d29649c4b191124edd276980c04`, and the branch is ready for PR gate and controlled merge.
- Next Step: run PR gate and controlled merge for PR #1878, publish v0.26.2 after merge, read back tag/GitHub Release/npm, then sync terminal closeout carriers.
- Blockers: None recorded.
- Latest Validation Summary: 2026-07-01 local validation passed for `python3 -m unittest test.output_envelope_test test.target_resolution_test`, `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py test/output_envelope_test.py test/target_resolution_test.py`, real `node bin/loom.mjs build --target <tmp> --item WI-test --json` and `node bin/loom.mjs fact-chain --target <tmp> --json` artifact readback probes, `python3 tools/check_cli_contract.py --surface aggregate`, `python3 tools/loom.py suite validate --target . --item WI-1876 --json`, `python3 tools/loom.py build --target . --item WI-1876 --build-evidence .loom/progress/WI-1876-build-evidence.json --json --full-output`, `python3 tools/skills_surface.py check`, `python3 tools/loom_check.py --profile source --source-surface contract-only .`, and `git diff --check`.
- Recovery Boundary: WI-1876 owns only the Loom CLI runtime artifact emission/readback contract and v0.26.2 release closeout for this fix. It does not add downstream repository-specific behavior, change authored truth carrier semantics, or reopen v0.26.1 closeout recovery.
- Current Lane: runtime-contract-fix

## Runtime Evidence

- Run Entry: 2026-07-01 WI-1876 work is active in `/Users/mc/dev/Loom` on branch `work/1876-target-output-artifacts`.
- Logs Entry: Validation output is retained in this Codex thread and will be summarized in `.loom/progress/WI-1876.md`.
- Diagnostics Entry: Branch starts from main after v0.26.1 closeout terminal state and targets #1876/#1878 plus v0.26.2 only.
- Verification Entry: focused output envelope/target resolution tests, real Node wrapper readback probes, aggregate CLI contract, and diff checks passed locally before PR metadata update.
- Lane Entry: runtime-contract-fix

## Sources

- Static Truth: .loom/work-items/WI-1876.md
- Dynamic Truth: .loom/progress/WI-1876.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
