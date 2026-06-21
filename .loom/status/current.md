# Current Status

## Derived Fact Chain View

- Item ID: WI-1675
- Goal: Improve the English and Chinese README entry experience so new users understand Loom's value, architecture, workflow model, and shortest supported install path.
- Scope: README documentation update plus release-surface and doc-sync README needle alignment for product positioning, problem statement, architecture overview, workflow model, badges, and quick start install wording. Do not change runtime behavior, package release surfaces, install implementation, or legacy migration contracts.
- Execution Path: issue #1675 -> branch work/1675-readme-install-clarity -> README update -> PR -> controlled merge -> issue #1675 closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1675.md
- Review Entry: .loom/reviews/WI-1675.json
- Validation Entry: `git diff --check`; README section alignment readback; Chinese README English-token scan; badge-link scan; `python3 tools/check_release_surface.py --surface release-doc-contract`; `npm --prefix packages/loom-installer run check:docs`; shadow parity.
- Closing Condition: PR for #1675 is merged, README changes are on `main`, and issue #1675 is closed with validation evidence.
- Current Checkpoint: merge
- Current Stop: README copy, doc-sync/release-surface checks, WI-1675 carriers, shadow parity, and fact-chain are refreshed for the next implementation commit on PR #1676.
- Next Step: Commit the doc-sync/carrier refresh, rerun workspace and PR gate readback, update review head and PR metadata, wait for hosted checks, run merge check, merge PR #1676, then close issue #1675.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-21T08:18Z local validation passed for WI-1675: git diff --check; doc-sync check; release-doc-contract check; README badge/body link scan; Chinese README token scan; English/Chinese heading and maintainer-link readback; suite evidence validate; suite carrier validate; suite validate; fact-chain; shadow parity. Workspace and PR gate readback will be rerun after the implementation commit.
- Recovery Boundary: WI-1675 owns README documentation, README doc-sync/release-surface needles, and Loom carrier metadata for this documentation change only. It does not modify runtime behavior, release packaging, install command behavior, legacy migration contracts, or downstream repository adoption.
- Current Lane: readme-install-clarity

## Runtime Evidence

- Run Entry: 2026-06-21 WI-1675 README documentation update in progress.
- Logs Entry: local command output retained in current Codex README thread.
- Diagnostics Entry: README documentation update plus release-surface and doc-sync README needle alignment; no runtime, install, package, or release behavior scope.
- Verification Entry: `git diff --check`; `python3 tools/check_release_surface.py --surface release-doc-contract`; `npm --prefix packages/loom-installer run check:docs`; `python3 tools/loom_flow.py shadow-parity --target . --blocking`; README section alignment readback; Chinese README English-token scan; badge-link scan.
- Lane Entry: readme-install-clarity

## Sources

- Static Truth: .loom/work-items/WI-1675.md
- Dynamic Truth: .loom/progress/WI-1675.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
