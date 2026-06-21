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
- Current Checkpoint: closed_out
- Current Stop: WI-1658 closed out by closeout run: PR #1671 merged at 3e17dd73fb4ccb260ede68e5518b83aa904fb682, issue #1658 closed, host reconciliation consumed, terminal carrier metadata written, status/shadow refresh completed, and final closeout check passed.
- Next Step: No further WI-1658 implementation work remains.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-21T03:20Z release-prep validation passed on branch work/1658-release / PR #1671: `python3 tools/loom.py release readback --target . --version v0.17.1 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --release-judgment release_required --json` passed and classified `v0.17.1` as unpublished with missing tag, GitHub Release, npm version, and target workflow run; `git diff --check`; `python3 tools/version_surface_check.py`; `python3 tools/check_release_surface.py`; `python3 tools/check_npm_package.py`; `npm run test:package`; `npm pack --dry-run --json --ignore-scripts`; `python3 test/output_envelope_test.py`; `python3 tools/loom.py help --json`; `python3 tools/loom.py suite validate --target . --item WI-1658 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1658 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1658 --json`; `python3 tools/loom.py fact-chain --target . --json`; `python3 tools/skills_surface.py check`; `python3 tools/loom_check.py --profile source --source-surface contract-only`; PR metadata update/readback for #1671.
- Recovery Boundary: WI-1658 owns release preparation, publish evidence, and #1658 closeout. It does not implement new runtime behavior, restore repo-local install surfaces, perform downstream migration, or complete final milestone regression closeout (#1489).
- Current Lane: post-merge-closeout-run

## Runtime Evidence

- Run Entry: 2026-06-21 WI-1658 post-merge release closeout completed.
- Logs Entry: local command output retained in current Codex milestone/11 thread.
- Diagnostics Entry: `v0.17.1` is published and read back from git tag, GitHub Release, npm, and workflow run; support boundary is global CLI plus Codex user-level plugin plus metadata-only host repositories.
- Verification Entry: release readback, closeout run apply, final closeout check, carrier refresh, and GitHub dependency readback.
- Lane Entry: milestone-11-release-closeout

## Sources

- Static Truth: .loom/work-items/WI-1658.md
- Dynamic Truth: .loom/progress/WI-1658.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
