# Current Status

## Derived Fact Chain View

- Item ID: WI-1658
- Goal: Publish the post-v0.17.0 context-safe runtime release so downstream operators can adopt the global `loom` CLI and Codex user-level plugin output boundary.
- Scope: Issue #1658 release preparation, version bump to `v0.17.1`, release readiness evidence, package/plugin payload validation, and release closeout evidence after the publish workflow runs on `main`. Do not restore repo-local plugin/runtime/skills install paths, single-skill package distribution, old installer compatibility, or downstream repository migration.
- Execution Path: issue #1658 -> branch work/1658-release -> release PR -> controlled merge -> `loom-cli-release` main-push workflow -> tag/npm/GitHub Release readback -> issue closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1658.md
- Review Entry: .loom/reviews/WI-1658.json
- Validation Entry: `python3 tools/loom.py release readback --target . --version v0.17.1 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --release-judgment release_required --json`; `python3 tools/version_surface_check.py`; `python3 tools/check_release_surface.py`; `python3 tools/check_npm_package.py`; `npm run test:package`; `npm pack --dry-run --json --ignore-scripts`; `python3 test/output_envelope_test.py`; `python3 tools/loom.py help --json`; `python3 tools/loom.py suite validate --target . --item WI-1658 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1658 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1658 --json`; `python3 tools/loom.py fact-chain --target . --json`; `git diff --check`
- Closing Condition: v0.17.1 release evidence points to the actual tag, main merge commit, GitHub Release, npm package readback, workflow run, installed/global CLI smoke, and #1658 issue closeout.
- Current Checkpoint: merge
- Current Stop: WI-1658 release PR #1671 is open on branch work/1658-release. Release-prep validation, spec review, implementation review, PR metadata readback, and review-readiness checks have passed locally; PR gate and hosted checks are the next merge-ready inputs.
- Next Step: Rerun PR gate for PR #1671 at the current head, consume hosted check readback, then controlled merge to trigger the v0.17.1 publish workflow.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-21T03:20Z release-prep validation passed on branch work/1658-release / PR #1671: `python3 tools/loom.py release readback --target . --version v0.17.1 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --release-judgment release_required --json` passed and classified `v0.17.1` as unpublished with missing tag, GitHub Release, npm version, and target workflow run; `git diff --check`; `python3 tools/version_surface_check.py`; `python3 tools/check_release_surface.py`; `python3 tools/check_npm_package.py`; `npm run test:package`; `npm pack --dry-run --json --ignore-scripts`; `python3 test/output_envelope_test.py`; `python3 tools/loom.py help --json`; `python3 tools/loom.py suite validate --target . --item WI-1658 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1658 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1658 --json`; `python3 tools/loom.py fact-chain --target . --json`; `python3 tools/skills_surface.py check`; `python3 tools/loom_check.py --profile source --source-surface contract-only`; PR metadata update/readback for #1671.
- Recovery Boundary: WI-1658 owns release preparation, publish evidence, and #1658 closeout. It does not implement new runtime behavior, restore repo-local install surfaces, perform downstream migration, or complete final milestone regression closeout (#1489).
- Current Lane: release

## Runtime Evidence

- Run Entry: 2026-06-21 WI-1658 release preparation in progress.
- Logs Entry: local command output retained in current Codex milestone/11 thread.
- Diagnostics Entry: `v0.17.1` release slot is unoccupied before merge; support boundary is global CLI plus Codex user-level plugin plus metadata-only host repositories.
- Verification Entry: release readback, version surface, release surface, npm package, npm package smoke, npm pack dry-run, output envelope tests, help JSON, suite validate/evidence/carrier, fact-chain, and diff check.
- Lane Entry: milestone-11-release

## Sources

- Static Truth: .loom/work-items/WI-1658.md
- Dynamic Truth: .loom/progress/WI-1658.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
