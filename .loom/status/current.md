# Current Status

## Derived Fact Chain View

- Item ID: WI-1696
- Goal: Execute milestone #15 release closeout for the intensity-aware ship path and publish Loom CLI v0.18.0.
- Scope: Bump root CLI release authority to v0.18.0, add release readiness evidence, validate package/release surfaces, publish through the existing main-push release workflow, terminalize stale milestone #15 carrier WI-1687, refresh shadow evidence for the active status surface, then close issue #1696 and phase #1680 after readback. Ownership: main executor owns VERSION, package.json, WI-1696 carriers, release evidence, PR metadata, release readback, milestone #15 carrier closeout cleanup, and host closeout. Non-goals: no new ship path implementation, no release workflow semantic change, no plugin surface version bump, no installer release.
- Execution Path: issue #1696 -> branch work/1696-release-closeout -> PR -> controlled merge -> release workflow -> release readback -> issue/phase closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1696.md
- Review Entry: .loom/reviews/WI-1696.json
- Validation Entry: release readback; version surface; release surface; npm package check; npm package smoke; npm pack dry-run; suite validate/evidence/carrier; fact-chain; state-check; git diff --check.
- Closing Condition: PR is merged into main, v0.18.0 tag/GitHub Release/npm package publish successfully, issue #1696 is closed, phase #1680 is closed, and milestone #15 has no open issues.
- Current Checkpoint: merge checkpoint
- Current Stop: Release PR #1709 is merged at `4b90a8e317b2a46d2d735670327986132c678f8e`; v0.18.0 is published on GitHub Releases and npm; closeout carrier PR is being prepared on branch `work/1696-release-closeout-carrier`.
- Next Step: Merge the final closeout carrier PR, then close issue #1696, close phase #1680, and close milestone #15 after readback.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-22 post-merge release readback passed: PR #1709 merged at `4b90a8e317b2a46d2d735670327986132c678f8e`; tag `v0.18.0`, GitHub Release, npm package `@mc-and-his-agents/loom@0.18.0`, `loom-cli-release` run `27929615490`, and post-merge `loom-check` run `27929615493` are successful. Carrier closeout sync dry-run and apply passed for WI-1696.
- Recovery Boundary: Work Item #1696 closeout carrier is active in `/Users/mc/dev/Loom-WI-1696` on branch `work/1696-release-closeout-carrier`; no work is performed in `/Users/mc/dev/Loom`.
- Current Lane: milestone-15-release-closeout

## Runtime Evidence

- Run Entry: 2026-06-22 WI-1696 release closeout started in issue-scoped worktree `/Users/mc/dev/Loom-WI-1696`.
- Logs Entry: Local command output retained in current Codex milestone #15 thread; concise validation commands will be listed in the Latest Validation Summary.
- Diagnostics Entry: `v0.18.0` is the release target for the completed intensity-aware ship path; `v0.18.0` was unoccupied before release PR preparation.
- Verification Entry: 2026-06-22 post-merge validation passed for release readback, GitHub Release, npm package, release workflow run `27929615490`, post-merge loom-check run `27929615493`, and WI-1696 carrier closeout sync.
- Lane Entry: milestone-15-release-closeout

## Sources

- Static Truth: .loom/work-items/WI-1696.md
- Dynamic Truth: .loom/progress/WI-1696.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
