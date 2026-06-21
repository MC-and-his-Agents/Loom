# Current Status

## Derived Fact Chain View

- Item ID: WI-1678
- Goal: Make the README immediately communicate Loom's product value and supported install path for coding-agent users.
- Scope: README.md and README.zh-CN.md product positioning, badge presentation, quick-start install prompt, and Loom carrier metadata for PR #1679 only. No runtime behavior, installer implementation, package release surface, or legacy migration contract changes.
- Execution Path: issue #1678 -> branch work/1678-agent-install-prompt -> README update -> PR #1679 -> controlled merge -> issue #1678 closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1678.md
- Review Entry: .loom/reviews/WI-1678.json
- Validation Entry: git diff --check; npm --prefix packages/loom-installer run check:docs; python3 tools/check_release_surface.py --surface release-doc-contract; PR gate; hosted checks
- Closing Condition: PR #1679 is merged into main, README changes are on main, and issue #1678 is closed with validation evidence.
- Current Checkpoint: review
- Current Stop: README product positioning, install prompt, suite path decision, and Loom carrier updates are committed at caa88d7ba5c7010f992750335edacb9121225a1b after local validation.
- Next Step: Record authored review for current head, update PR body head SHA, rerun PR gate and hosted checks, then controlled merge.
- Blockers: Awaiting authored review, PR body head refresh, PR gate, hosted checks, and controlled merge readback.
- Latest Validation Summary: 2026-06-21T12:10Z local validation passed for WI-1678 head caa88d7ba5c7010f992750335edacb9121225a1b: git diff --check; npm --prefix packages/loom-installer run check:docs; python3 tools/check_release_surface.py --surface release-doc-contract; python3 tools/loom_flow.py fact-chain --target . --item WI-1678.
- Recovery Boundary: WI-1678 owns README.md, README.zh-CN.md, PR #1679 metadata, and Loom carrier metadata for this documentation-only iteration. It does not modify runtime behavior, installer implementation, package release surfaces, install command behavior, or legacy migration contracts.
- Current Lane: readme-product-positioning

## Runtime Evidence

- Run Entry: 2026-06-21 WI-1678 README product positioning and install prompt iteration in progress.
- Logs Entry: local command output retained in current Codex README thread.
- Diagnostics Entry: README product narrative, badge, install prompt, release-surface, doc-sync, and loom_check README needle alignment; no runtime, install, package, or release behavior scope.
- Verification Entry: `git diff --check`; `npm --prefix packages/loom-installer run check:docs`; `python3 tools/check_release_surface.py --surface release-doc-contract`; `python3 tools/loom_flow.py fact-chain --target . --item WI-1678`; PR gate and hosted checks pending.
- Lane Entry: readme-product-positioning

## Sources

- Static Truth: .loom/work-items/WI-1678.md
- Dynamic Truth: .loom/progress/WI-1678.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
