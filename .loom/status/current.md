# Current Status

## Derived Fact Chain View

- Item ID: WI-866
- Goal: 收口 FR #866 分层 closeout 本地 gate 与 evidence 回链消费。
- Scope: 定义 closeout gate 分层合同；实现 closeout retained evidence backlink 消费、gate profile/fixture 输入和 subcheck 输出；同步 generated skills surface；验证 PR #981 达到 merge-ready、合并后 closeout 可验证一致；不改变 GitHub required checks、ProjectV2、review engine 或底层 host 能力。
- Execution Path: harness/closeout-layered-gate
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-866.md
- Review Entry: .loom/reviews/WI-866.json
- Validation Entry: py_compile_clean; skills_surface check; targeted closeout fixtures; make loom-check; make check; PR checks; post-merge closeout check/sync
- Closing Condition: PR #981 merged to main; #867-#870 closed or have closing evidence; #866 consumes PR, merge commit, target branch, Project, and reconciliation evidence consistently.
- Current Checkpoint: merge checkpoint
- Current Stop: Merged origin/main through 456773e4bd05, resolved WI-966 terminal predecessor state, refreshed demo bootstrap fixture hashes, and prepared WI-866 review refresh for current head.
- Next Step: Record refreshed implementation review, refresh carrier/shadow evidence, rerun merge checkpoint and make check, push, consume PR checks, merge, and run post-merge closeout.
- Blockers: None recorded.
- Latest Validation Summary: Head 6a1db5ba0860 after merging origin/main passed: git diff --check; python3 tools/check_demo_bootstrap_fixture.py; node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main (0.1.140 -> 0.1.141). Earlier merged-main validation also passed py_compile_clean for loom_flow/loom_check and installed scripts, skills_surface check, and carrier refresh. WI-966 predecessor confirmed merged via PR #983 and issue #966 closed. Pending: refreshed implementation review binding, carrier/shadow refresh, make check, PR checks, post-merge closeout.
- Recovery Boundary: WI-866 owns #866/#867-#870 closeout gate layering, retained evidence backlink consumption, generated skills surface refresh, installer package bump for distributed runtime drift, and PR #981 closeout evidence. It excludes GitHub required checks, ProjectV2, review engine, and low-level host capability changes.
- Current Lane: pr-prep

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/loom_check.py --profile source .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-866.md
- Dynamic Truth: .loom/progress/WI-866.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
