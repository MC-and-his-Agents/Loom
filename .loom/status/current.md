# Current Status

## Derived Fact Chain View

- Item ID: WI-1790
- Goal: Fix installed Loom CLI `loom init bootstrap --target ... --json` so packaged npm installs no longer look for a missing top-level `skills/shared/scripts/loom_init.py`.
- Scope: PR #1790 only: runtime wrapper entrypoint resolution, generated/runtime `loom_init.py` parity, npm package payload checks, package smoke coverage, v0.21.1 release metadata, demo bootstrap fixture sync, PR metadata, and Loom carriers for this repair. Ownership constraints are limited to `tools/runtime_wrapper.py`, wrapper entrypoints under `tools/`, `skills/shared/scripts/loom_init.py`, `src/skills/shared/scripts/loom_init.py`, `plugins/loom/skills/shared/scripts/loom_init.py`, `test/npm-package-smoke.test.mjs`, `tools/check_npm_package.py`, `VERSION`, `package.json`, `plugins/loom/.codex-plugin/plugin.json`, `examples/new-project/.loom/**`, `.loom/bootstrap/init-result.json`, `.loom/status/current.md`, `.loom/work-items/WI-1790.md`, `.loom/progress/WI-1790.md`, `.loom/reviews/WI-1790*.json`, and `.loom/specs/WI-1790/**`.
- Execution Path: user-reported installed CLI bootstrap failure -> branch `work/fix-init-bootstrap-entrypoint` -> source/package fix -> PR #1790 -> release v0.21.1 -> installed CLI and Codex plugin payload readback.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1790.md
- Review Entry: .loom/reviews/WI-1790.json
- Validation Entry: `python3 tools/py_compile_clean.py tools/loom.py tools/runtime_wrapper.py tools/loom_init.py tools/loom_flow.py tools/loom_check.py tools/loom_status.py tools/check_npm_package.py tools/check_release_surface.py tools/version_surface_check.py`; `python3 tools/version_surface_check.py`; `python3 tools/check_release_surface.py`; `python3 tools/skills_surface.py check --surface plugin-payload-metadata`; `python3 tools/check_npm_package.py`; `npm run test:package`; `python3 tools/check_demo_bootstrap_fixture.py --surface fixture-drift`; `git diff --check`; hosted PR checks; post-release installed CLI smoke.
- Closing Condition: PR #1790 merges, v0.21.1 is published to npm, Codex plugin payload metadata is refreshed, and installed `loom init bootstrap --target <fixture> --json` plus `loom init runtime-state --target <fixture> --json` pass from the released package.
- Current Checkpoint: closed_out
- Current Stop: WI-1790 closed out by closeout run: PR #1790 merged at 9668401faa7e334addc4dad6b42978656757b15e, issue #1790 closed, host reconciliation consumed, terminal carrier metadata written, status/shadow refresh completed, and final closeout check passed.
- Next Step: No further WI-1790 implementation work remains.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-29 closeout validation on branch `work/WI-1790-closeout-sync` head `26e3ea9c3a37e038890d9f70a39ed53e1866d9d3`: `python3 tools/loom.py release readback --target . --version v0.21.1 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --commit 9668401faa7e334addc4dad6b42978656757b15e --release-judgment release_required --json`; `CODEX_EXPORT_GH_TOKEN=1 python3 tools/loom.py closeout status --target . --item WI-1790 --issue 1790 --pr 1790 --pr-role release_pr --release-pr 1790 --branch main --owner MC-and-his-Agents --repo Loom --goal-completion .loom/progress/WI-1790-goal-completion.json --skip-metadata --skip-cleanup --json`; `python3 tools/loom.py fact-chain --target . --item WI-1790 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1790 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1790 --json`; `python3 -m json.tool .loom/progress/WI-1790-goal-completion.json >/dev/null`; `git diff --check HEAD~1..HEAD` passed.
- Recovery Boundary: WI-1790 owns only the installed package init/bootstrap entrypoint repair, v0.21.1 package/payload metadata, focused package smoke coverage, demo fixture sync caused by the runtime change, and current PR carriers. It does not redesign Loom initialization, change plugin surface version, publish legacy installer packages, or close unrelated v0.21.0 release carriers.
- Current Lane: post-merge-closeout-run

## Runtime Evidence

- Run Entry: 2026-06-29 WI-1790 repair started in repo-relative workspace `.` on branch `work/fix-init-bootstrap-entrypoint`.
- Logs Entry: Local reproduction and validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1790.md`.
- Diagnostics Entry: Installed package bootstrap failed because wrappers searched for missing top-level `skills/shared/scripts/loom_init.py`; PR gate currently requires WI-1790 metadata and review refresh.
- Verification Entry: Local source/package checks passed before carrier refresh; hosted checks, release publish, plugin payload refresh, and installed CLI readback remain required.
- Lane Entry: init-bootstrap-installed-entrypoint-release

## Sources

- Static Truth: .loom/work-items/WI-1790.md
- Dynamic Truth: .loom/progress/WI-1790.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
