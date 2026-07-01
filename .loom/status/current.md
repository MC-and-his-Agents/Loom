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
- Current Checkpoint: closed_out
- Current Stop: WI-1876 release closeout synced for v0.26.2: release PR #1878 merged at c0a25a6ab52782b6bb87c0dfd14e2a6028cf1840; published release readback consumed into terminal repo carrier state.
- Next Step: None.
- Blockers: None recorded.
- Latest Validation Summary: 2026-07-01 implementation validation passed at PR head `15828345b56250b9e7b662b3d0e1089a3bfff839`: focused output envelope / target resolution tests, py-compile-clean, controlled-merge, governance-closeout, aggregate CLI contract, version/release/package checks, suite validators, build evidence, skills surface, source contract-only loom_check, checkpoint merge, shadow parity, PR gate, merge check, and git diff checks passed. Post-merge release readback passed for `v0.26.2` at `c0a25a6ab52782b6bb87c0dfd14e2a6028cf1840`: tag, GitHub Release, npm `@mc-and-his-agents/loom@0.26.2` with `latest=0.26.2`, release workflow run `28545028638`, package surface, #1878 merge, #1876 CLOSED/COMPLETED, and terminal carrier closeout all read back consistently.
- Recovery Boundary: WI-1876 owns only the Loom CLI runtime artifact emission/readback contract and v0.26.2 release closeout for this fix. It does not add downstream repository-specific behavior, change authored truth carrier semantics, or reopen v0.26.1 closeout recovery.
- Current Lane: release-closeout-sync

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
