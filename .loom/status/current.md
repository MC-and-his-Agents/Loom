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
- Current Checkpoint: closed_out
- Current Stop: PR #1676 was controlled-merged to main, issue #1675 is closed, and terminal closeout metadata is recorded for WI-1675.
- Next Step: not_applicable
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-21T09:34Z local validation passed for WI-1675: git diff --check; doc-sync check; release-doc-contract check; README badge/body link scan; Chinese README token scan; English/Chinese heading and maintainer-link readback; skills surface check; `loom skills check`; py_compile for loom_check mirrors; loom_check contract-only; installer regression including npm test and npm pack dry-run; demo bootstrap fixture sync followed by `make loom-demo-new-project-check`; root bootstrap hash sync followed by `.loom/bin/loom_init.py verify`, runtime parity, and adopt verify; suite evidence validate; suite carrier validate; suite validate; fact-chain; shadow parity; local PR gate passed for head d3d833067f929431ef247dfce9f362ca7258517a before fixture sync. Full local `python3 tools/loom_check.py` was run after the demo fixture sync and failed only on root-self-adoption because root bootstrap hash carriers were stale; targeted root self-governance checks now pass after hash sync. PR metadata, PR gate, hosted checks, and merge check will be rerun after the fixture implementation commit and review refresh.
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
