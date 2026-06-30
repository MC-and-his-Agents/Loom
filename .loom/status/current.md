# Current Status

## Derived Fact Chain View

- Item ID: WI-1805
- Goal: Complete the v0.23.0 Host Governance Capability milestone by adding host governance diagnosis, explicit governance capability profiles, merge runtime consumption, governance mode evidence, and release convergence.
- Scope: Parent issue #1805 plus milestone children #1826-#1830. Implementation covers GitHub host governance capability diagnosis, `host-enforced` and `advisory/local-enforced` profile contracts, merge check/run profile enforcement, governance mode metadata/evidence/readback, v0.23.0 version/package/plugin metadata, release readiness evidence, tests, and Loom carriers for this work. Advisory/local-enforced remains a low-assurance fallback and must not be represented as strong governance.
- Execution Path: issue tree #1805 -> branch `work/1805-host-governance-capability` -> diagnosis/profile lanes #1826/#1827 -> merge runtime #1828 -> evidence/readback #1829 -> release convergence #1830 -> PR -> merge -> v0.23.0 publish/readback -> issue and milestone closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1805.md
- Review Entry: .loom/reviews/WI-1805.json
- Validation Entry: `python3 -m unittest test.host_governance_capability_test test.governance_capability_profiles_test test.governance_merge_profile_test test.output_envelope_test test.plugin_payload_hash_test`; `node --test test/npm-package-smoke.test.mjs`; `python3 tools/check_npm_package.py`; `python3 tools/check_release_surface.py`; `python3 tools/version_surface_check.py`; `python3 tools/check_cli_contract.py`
- Closing Condition: PR for #1805 merges to `main`, v0.23.0 is published to GitHub Release and npm with package/plugin readback, #1826-#1830 and #1805 are closed, the milestone is closed, and repo-local Loom carrier closeout consumes the release facts.
- Current Checkpoint: closed_out
- Current Stop: WI-1805 completed: PR #1831 merged to `main` at `70128780aee1f867f15245cb24f94bf73a043f53`, v0.23.0 GitHub Release and npm package were published/read back, release workflow `28465118633` passed, and terminal closeout metadata is recorded.
- Next Step: No further WI-1805 implementation or release work remains; close #1826-#1830, parent #1805, and milestone after host issue readback.
- Blockers: None recorded.
- Latest Validation Summary: Targeted unittest suite, npm package smoke, package/release/version checks, full CLI contract, suite evidence/carrier validate, fact-chain readback, carrier refresh, PR metadata preflight/readback for PR #1831, spec review, and semantic review passed for WI-1805.
- Recovery Boundary: WI-1805 owns #1826-#1830 implementation, v0.23.0 release readiness and release closeout only. It must not represent advisory/local-enforced as strong governance, must not bypass review/PR gate/head binding/CI rollup/release readback/closeout evidence, and must not expand into unrelated milestones or HotCP-specific core behavior.
- Current Lane: release-closeout-sync

## Runtime Evidence

- Run Entry: 2026-07-01 WI-1805 host governance capability work resumed in `/Users/mc/dev/Loom.worktrees/1805-host-governance-capability` on branch `work/1805-host-governance-capability`.
- Logs Entry: Lane summaries and validation output are retained in this Codex thread and summarized in `.loom/progress/WI-1805.md`.
- Diagnostics Entry: Runtime carrier hash drift was refreshed in `.loom/bootstrap/manifest.json` and `.loom/bootstrap/init-result.json`; `carrier refresh` now reports no refresh-needed actions and only correctly blocks on the expected pre-review stale-review state.
- Verification Entry: Targeted unittest suite, npm smoke, npm package check, release surface check, version surface check, full CLI contract, suite evidence/carrier validate, PR metadata preflight/readback, spec review, semantic review, hosted PR gates, merge, release workflow, GitHub Release readback, npm readback, and terminal carrier sync passed.
- Lane Entry: release-closeout-sync

## Sources

- Static Truth: .loom/work-items/WI-1805.md
- Dynamic Truth: .loom/progress/WI-1805.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
