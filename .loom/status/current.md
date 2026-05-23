# Current Status

## Derived Fact Chain View

- Item ID: WI-871
- Goal: 彻底收口 FR #871 retained pr-gate / merge-gate result 与 controlled merge drift-only 消费。
- Scope: 在 `controlled-merge check|merge` 中支持 repo-relative retained `pr-gate` / `merge-gate` result locator；校验 retained result 的 Work Item、PR、head SHA、review approval、validation summary 与 merge checkpoint freshness；输出 drift-only readback；同步 harness / interop 合同、source skills references、generated skills surface 与 installer version metadata。
- Execution Path: harness/controlled-merge-retained-results
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-871.md
- Review Entry: .loom/reviews/WI-871.json
- Validation Entry: make py-compile; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source; node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main
- Closing Condition: PR #980 for #871 is merge-ready or merged with branch, worktree, PR head, retained gate result checks, required host checks, and review carriers aligned.
- Current Checkpoint: merge checkpoint
- Current Stop: WI-871 implementation and review carriers are locally validated through head 7191dc2b389bfbf409d879c0d2c67507c707feba; awaiting push, PR checks, pr-gate, merge-gate, controlled merge, and closeout.
- Next Step: Push the branch, update PR #980 workspace binding to the pushed head, rerun PR checks, then consume pr-gate / merge-gate results through controlled-merge drift-only readback.
- Blockers: None recorded.
- Latest Validation Summary: Head 7191dc2b389bfbf409d879c0d2c67507c707feba passed: make py-compile; python3 tools/skills_surface.py check; node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main; python3 tools/version_surface_check.py; git diff --check; python3 tools/loom_flow.py shadow-parity --target . --mode blocking; python3 tools/loom_flow.py adopt verify --target .; npm ci; npm test; npm pack --dry-run; python3 tools/loom_check.py --profile source. Initial source loom_check failure was traced to stale shadow evidence and npm install interruption; both were corrected and rerun successfully.
- Recovery Boundary: WI-871 owns retained pr-gate / merge-gate locator consumption, controlled-merge drift-only readback, harness / interop contract updates, generated skills surface updates, and required installer version metadata for this distribution change.
- Current Lane: pr-prep

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: make py-compile; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source; node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-871.md
- Dynamic Truth: .loom/progress/WI-871.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
