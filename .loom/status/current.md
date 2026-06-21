# Current Status

## Derived Fact Chain View

- Item ID: WI-1675
- Goal: Improve the English and Chinese README entry experience so new users understand Loom's value, architecture, workflow model, and shortest supported install path.
- Scope: README documentation update plus release-surface, doc-sync, and loom_check README needle alignment for product positioning, problem statement, architecture overview, workflow model, badges, and quick start install wording. Do not change runtime behavior, package release surfaces, install implementation, or legacy migration contracts.
- Execution Path: issue #1675 -> branch work/1675-readme-install-clarity -> README update -> PR -> controlled merge -> issue #1675 closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1675.md
- Review Entry: .loom/reviews/WI-1675.json
- Validation Entry: `git diff --check`; README section alignment readback; Chinese README English-token scan; badge-link scan; `python3 tools/check_release_surface.py --surface release-doc-contract`; `npm --prefix packages/loom-installer run check:docs`; `python3 tools/loom_check.py --profile source --source-surface contract-only .`; shadow parity.
- Closing Condition: PR for #1675 is merged, README changes are on `main`, and issue #1675 is closed with validation evidence.
- Current Checkpoint: merge
- Current Stop: README copy, doc-sync/release-surface/loom_check README contract checks, generated skills surface, installer regression, WI-1675 carriers, shadow parity, and fact-chain are refreshed for the next implementation commit on PR #1676.
- Next Step: Commit the checker/carrier refresh, push, update PR metadata to the new head, rerun workspace and PR gate readback, wait for hosted checks, run merge check, merge PR #1676, then close issue #1675.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-21T09:00Z local validation passed for WI-1675: git diff --check; doc-sync check; release-doc-contract check; README badge/body link scan; Chinese README token scan; English/Chinese heading and maintainer-link readback; skills surface check; `loom skills check`; py_compile for loom_check mirrors; loom_check contract-only; installer regression including npm test and npm pack dry-run; suite evidence validate; suite carrier validate; suite validate; fact-chain; shadow parity. Full local `python3 tools/loom_check.py` was run once before removing ignored install-status residue and failed only through generated skills surface parity; the targeted root-cause checks now pass. Workspace, PR gate, PR metadata, hosted checks, and merge check will be rerun after the implementation commit.
- Recovery Boundary: WI-1675 owns README documentation, README doc-sync/release-surface/loom_check README needles, and Loom carrier metadata for this documentation change only. It does not modify runtime behavior, release packaging, install command behavior, legacy migration contracts, or downstream repository adoption.
- Current Lane: readme-install-clarity

## Runtime Evidence

- Run Entry: 2026-06-21 WI-1675 README documentation update in progress.
- Logs Entry: local command output retained in current Codex README thread.
- Diagnostics Entry: README documentation update plus release-surface, doc-sync, and loom_check README needle alignment; no runtime, install, package, or release behavior scope.
- Verification Entry: `git diff --check`; `python3 tools/check_release_surface.py --surface release-doc-contract`; `npm --prefix packages/loom-installer run check:docs`; `python3 tools/loom_check.py --profile source --source-surface contract-only .`; `python3 tools/loom_flow.py shadow-parity --target . --blocking`; README section alignment readback; Chinese README English-token scan; badge-link scan.
- Lane Entry: readme-install-clarity

## Sources

- Static Truth: .loom/work-items/WI-1675.md
- Dynamic Truth: .loom/progress/WI-1675.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
