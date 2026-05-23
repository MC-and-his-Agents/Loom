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
- Current Stop: WI-866 formal reviews are recorded against implementation head 75c913de38db70dcee9d7eede44ec5988ffb02ef; preparing merge-ready evidence and full gate rerun.
- Next Step: Run merge-ready, commit carrier-only evidence, rerun make loom-check/make check, update PR body, push, and consume PR checks.
- Blockers: None recorded.
- Latest Validation Summary: Head 75c913de38db70dcee9d7eede44ec5988ffb02ef passed: py_compile_clean for loom_flow/loom_check/tools/check_demo_bootstrap_fixture scripts; skills_surface check; node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main (0.1.138 -> 0.1.139); git diff --check. Pending: formal review records, merge-ready evidence, make loom-check, make check, PR checks, post-merge closeout.
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
