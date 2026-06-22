# Current Status

## Derived Fact Chain View

- Item ID: WI-1718
- Goal: 执行插件 payload 新鲜度能力的 v0.19.0 release closeout。
- Scope: bump root Loom CLI release authority to `v0.19.0`, align root npm package and Codex plugin payload release metadata, add publish-time `source_git_sha` stamping before npm publish, retain release readiness evidence, and close out #1711 after release readback. Ownership constraints are limited to v0.19.0 release authority, plugin payload release metadata/hash, release workflow stamping, release readiness evidence, and WI-1718 carriers. Do not bump plugin surface version, skills registry version, skill contract versions, or legacy `@mc-and-his-agents/loom-installer`.
- Execution Path: issue #1718 -> branch work/1718-v0.19.0-release-closeout -> release readiness evidence -> release PR -> main push release workflow -> release readback -> #1718/#1711 closeout.
- Workspace Entry: .loom/..
- Recovery Entry: .loom/progress/WI-1718.md
- Review Entry: .loom/reviews/WI-1718.json
- Validation Entry: release readback, release/package checks, stamp script check, npm package smoke, suite/fact-chain, hosted checks, and post-merge release readback.
- Closing Condition: v0.19.0 tag, GitHub Release, npm `@mc-and-his-agents/loom@0.19.0`, plugin payload metadata/hash, and #1711/#1718 closeout evidence read back consistently.
- Current Checkpoint: closed_out
- Current Stop: WI-1718 terminal closeout consumed: PR #1757 merged into main at 2026-06-22T23:12:56Z with merge commit f7c853209057732c56a163a02d022c71e90717f1; v0.19.0 GitHub Release, tag, npm package, plugin payload metadata/hash, #1718 closeout, and parent #1711 closeout read back consistently.
- Next Step: No further WI-1718 implementation work remains; retire release and closeout-sync worktrees after carrier closeout PR merges and main/codegraph readback pass.
- Blockers: none
- Latest Validation Summary: 2026-06-22T22:49Z local release/package validation passed at pre-commit branch head: release readback classified v0.19.0 as unpublished/unoccupied; `stamp_plugin_payload_metadata.py --source-git-sha unreleased --json`, `version_surface_check.py`, `check_release_surface.py`, `check_npm_package.py`, `npm run test:package`, `npm pack --dry-run --json --ignore-scripts`, suite validate/evidence/carrier, fact-chain, state-check, and `git diff --check` passed.
- Recovery Boundary: WI-1718 terminal closeout sync only: versioned carrier/status/shadow evidence for v0.19.0 release and #1711/#1718 closeout. Do not restore legacy installer behavior, publish or bump legacy installer, change plugin surface compatibility version, execute npm deprecate without separate confirmation, or add new product scope.
- Current Lane: release-closeout-sync

## Runtime Evidence

- Run Entry: 2026-06-23 WI-1718 build started in issue-scoped worktree `work/1718-v0.19.0-release-closeout`.
- Logs Entry: Local validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1718.md`.
- Diagnostics Entry: Release readiness evidence records candidate occupancy, plugin payload metadata/hash, publish boundary, and npm deprecate boundary.
- Verification Entry: Local release/package checks, suite validation, fact-chain, state-check, diff check, build gate, spec review, implementation review, PR metadata readback, and local PR gate input validation passed; hosted checks, controlled merge, and post-merge release readback remain pending.
- Lane Entry: release-closeout

## Sources

- Static Truth: .loom/work-items/WI-1718.md
- Dynamic Truth: .loom/progress/WI-1718.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
