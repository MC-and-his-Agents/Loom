# Current Status

## Derived Fact Chain View

- Item ID: WI-1851
- Goal: v0.25.0 shift-left readiness and task-oriented CLI guidance
- Scope: Implement local readiness drift classification, write-after-readback/preflight, closeout/carrier-sync suite preservation, and task-oriented help/README/SKILL guidance for #1851/#1852/#1853/#1850/#1854.
- Execution Path: minimal suite; implementation PR then release PR
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1851.md
- Review Entry: .loom/reviews/WI-1851.json
- Validation Entry: python3 -m py_compile tools/loom.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py --surface aggregate; python3 tools/loom.py skills check --target . --json; python3 tools/check_npm_package.py --surface plugin-payload-hash
- Closing Condition: PR merged, no-release closeout evidence consumed for implementation, then v0.25.0 release/readback/terminal carrier closeout in #1855.
- Current Checkpoint: merge
- Current Stop: PR #1856 metadata readback is bound to final head ca122df590e8572c46e99f670e6c7eb8631feab6; review disposition and implementation contract carrier have been repaired for PR gate consumption.
- Next Step: Rerun PR metadata readback, PR gate, hosted checks, and merge-ready for PR #1856.
- Blockers: None recorded.
- Latest Validation Summary: Passed for implementation head 837b1db946bbb8578ed8f373a5d9d7cf1a2bd2b1: python3 -m py_compile tools/loom.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py --surface pr-metadata; python3 tools/loom.py skills check --target . --json; python3 tools/check_npm_package.py --surface plugin-payload-hash; python3 tools/check_cli_contract.py --surface aggregate; python3 tools/loom.py suite validate --target . --item WI-1851 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1851 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1851 --json; git diff --check; python3 .loom/bin/loom_init.py fact-chain --target .
- Recovery Boundary: .loom/reviews/WI-1851.json; .loom/specs/WI-1851/implementation-contract.md; .loom/work-items/WI-1851.md; .loom/progress/WI-1851.md; .loom/status/current.md
- Current Lane: merge-gate-prep

## Runtime Evidence

- Run Entry: 2026-07-01 WI-1844 release closeout-sync work is active in `/Users/mc/dev/Loom.worktrees/1845-v0.24.1-release` on branch `work/1845-v0.24.1-release`.
- Logs Entry: Validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1844.md`.
- Diagnostics Entry: Release closeout-sync dogfood dry-run passes against the WI-1834 main worktree; the same command correctly fail-closes when run from the WI-1844 worktree against WI-1834 because the fact-chain item does not match.
- Verification Entry: `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py tools/check_npm_package.py tools/stamp_plugin_payload_metadata.py tools/version_surface_check.py`, `python3 tools/version_surface_check.py`, `python3 tools/check_release_surface.py`, `python3 tools/check_npm_package.py`, `python3 tools/check_cli_contract.py --surface release-readback`, `python3 tools/check_cli_contract.py --surface aggregate`, `npm pack --dry-run --json --ignore-scripts`, suite validate/carrier/evidence, fact-chain, release readback, hosted gates, and loom merge check/run passed for implementation PR #1847.
- Lane Entry: release-pr

## Sources

- Static Truth: .loom/work-items/WI-1851.md
- Dynamic Truth: .loom/progress/WI-1851.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
