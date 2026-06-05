# Current Status

## Derived Fact Chain View

- Item ID: WI-1315
- Goal: Define a project-neutral change governance intensity model.
- Scope: Add the generic governance methodology contract for risk dimensions, `light` / `standard` / `reinforced` intensity tiers, upgrade triggers, minimum evidence for light paths, downgrade prohibitions, and project mapping boundaries. Link it from governance landing docs. Do not implement Loom gate behavior, CLI metadata, fixtures, generated skills, runtime behavior, release behavior, or AGENTS.md rules.
- Execution Path: issue #1315 -> branch work/1315-generic-governance-intensity -> PR #1325 -> docs review -> CI/review -> merge to main.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1315.md
- Review Entry: .loom/reviews/WI-1315.json
- Validation Entry: git diff --check; docs contract review; Loom-specific term scan; suite validate not_applicable; PR CI.
- Closing Condition: PR #1325 is merge-ready, merged to main, #1315 is closed with validation and no-release evidence, and #1316/#1317 can reference the frozen generic model without redefining its tiers.
- Current Checkpoint: merge_ready
- Current Stop: PR #1325 head b2afe02139e066e132f3042a48f38a6480015bf8 contains the frozen generic change governance intensity model, WI-1315 portable workspace evidence, and latest-main WI-1255 closeout artifacts required for target-branch compatibility.
- Next Step: Wait for hosted checks on head b2afe02139e066e132f3042a48f38a6480015bf8; if they pass, run controlled-merge check and merge through the Loom wrapper.
- Blockers: None
- Latest Validation Summary: Head b2afe02139e066e132f3042a48f38a6480015bf8 passed `git diff --check`; `python3 tools/loom.py fact-chain --target . --json` passed for WI-1315 with portable workspace entry `.`; `python3 tools/loom.py suite validate --target . --item WI-1315 --json` returned result `not_applicable` with zero blocking gaps and locator `.loom/specs/WI-1315/spec.md`; latest-main merge conflict resolution preserves WI-1315 as the active current item while retaining target-main WI-1255 closeout artifacts; refreshed WI-1315 implementation and spec review records bind to b2afe02139e066e132f3042a48f38a6480015bf8; docs review verified risk dimensions, `light` / `standard` / `reinforced` tiers, upgrade triggers, minimum light-path evidence, downgrade prohibitions, and project mapping boundaries; Loom-specific term scan found no `.loom`, `Work Item`, `pr-gate`, `loom_check`, `guardian`, `suite validate`, or `git worktree` terms in the generic model body; PR body records no-release evidence and head b2afe02139e066e132f3042a48f38a6480015bf8.
- Recovery Boundary: This Work Item only owns #1315 generic governance methodology docs, landing links, and WI-1315 readiness carriers. Do not implement Loom gate behavior, CLI metadata, fixtures, generated skills, runtime behavior, release behavior, or AGENTS.md rules here.
- Current Lane: merge-ready

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: local docs review, `git diff --check`, Loom-specific term scan, suite validate not_applicable, and PR #1325 hosted checks
- Lane Entry: merge-ready

## Sources

- Static Truth: .loom/work-items/WI-1315.md
- Dynamic Truth: .loom/progress/WI-1315.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
