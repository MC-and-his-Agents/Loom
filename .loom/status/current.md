# Current Status

## Derived Fact Chain View

- Item ID: WI-1884
- Goal: Publish the host `AGENTS.md` execution-entry guidance fix as `v0.26.3`.
- Scope: bump root Loom CLI release authority to `v0.26.3`, align npm package and Codex plugin payload metadata/hash, add release readiness evidence, prepare and merge the release PR, then read back GitHub Release/npm/tag/workflow and close out #1881/#1882/#1884. Consumes #1883 / PR #1885 as the already-merged implementation input.
- Execution Path: issue #1884 -> branch work/1884-v0.26.3-release -> release readiness evidence -> release PR -> main push release workflow -> release readback -> #1881/#1882/#1884 closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1884.md
- Review Entry: .loom/reviews/WI-1884.json
- Validation Entry: release readback, release/package checks, CLI contract checks, npm package dry-run, suite/fact-chain, hosted checks, and post-merge release readback.
- Closing Condition: v0.26.3 tag, GitHub Release, npm @mc-and-his-agents/loom@0.26.3, plugin payload metadata/hash, and #1881/#1882/#1884 closeout evidence are consistent.
- Current Checkpoint: release_candidate
- Current Stop: WI-1884 release candidate validation passed locally on 2026-07-02; the release branch is ready for PR metadata, review, hosted gates, and controlled merge.
- Next Step: Open the release PR, pass hosted gates, merge, wait for main-push publication, run release readback, then close #1881/#1882/#1884.
- Blockers: None recorded.
- Latest Validation Summary: 2026-07-02T12:43:25Z local pre-release validation passed for `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py tools/check_npm_package.py tools/stamp_plugin_payload_metadata.py tools/version_surface_check.py`, `python3 tools/version_surface_check.py`, `python3 tools/check_release_surface.py`, `python3 tools/check_npm_package.py --surface aggregate`, `npm pack --dry-run --json --ignore-scripts`, `python3 tools/check_cli_contract.py --surface release-readback`, `python3 tools/check_cli_contract.py --surface aggregate`, `python3 tools/loom.py suite validate --target . --item WI-1884 --json`, `python3 tools/loom.py suite evidence validate --target . --item WI-1884 --json`, `python3 tools/loom.py suite carrier validate --target . --item WI-1884 --json`, `python3 .loom/bin/loom_init.py fact-chain --target .`, `python3 tools/loom.py skills release-check --json`, and `python3 tools/check_demo_bootstrap_fixture.py`; pre-merge release readback for `v0.26.3` passed with expected verdict `missing` and gaps `tag_missing`, `github_release_missing`, `npm_version_missing`, and `workflow_run_not_success`.
- Recovery Boundary: WI-1884 owns only release metadata/evidence and terminal closeout for the host `AGENTS.md` guidance fix. It does not change runtime behavior beyond merged PR #1885, does not bump plugin surface compatibility, does not publish the legacy installer, and does not close parent issues before release readback.
- Current Lane: release-pr

## Runtime Evidence

- Run Entry: 2026-07-02 WI-1884 work is active in `/Users/mc/dev/Loom` on branch `work/1884-v0.26.3-release`.
- Logs Entry: main-push `loom-cli-release` run `28589788160` failed at Resolve CLI release state with reason `version-already-published-on-different-commit` for `v0.26.2`; release/version/CLI/package dry-run stages passed before that fail-closed state.
- Diagnostics Entry: Failure classified as release version authority drift, not a code/package regression; resolution is to bump to unpublished `v0.26.3`.
- Verification Entry: Local release candidate validation passed at 2026-07-02T12:43:25Z; aggregate CLI contract passed in 379.54s and pre-merge release readback returned expected `missing`.
- Lane Entry: release-pr

## Sources

- Static Truth: .loom/work-items/WI-1884.md
- Dynamic Truth: .loom/progress/WI-1884.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
