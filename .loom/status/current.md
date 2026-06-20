# Current Status

## Derived Fact Chain View

- Item ID: WI-1488
- Goal: Update user documentation, command-help descriptions, and migration guidance so downstream operators use context-safe Loom output and the v0.17.0 global CLI plus Codex user-level plugin support boundary.
- Scope: Issue #1488 documentation/help/migration only. Update README and adoption / CLI command documentation to describe agent-safe summary output, artifact locators, explicit `--full-output`, configurable output budgets, metadata-only host repository adoption, global `loom` CLI, and Codex user-level plugin usage. Do not publish a release, change runtime behavior, alter skill payload implementation, migrate downstream repositories, restore repo-local plugin/runtime/skills installs, single-skill package distribution, or old installer compatibility paths.
- Execution Path: issue #1488 -> branch work/1488-docs-migration -> PR #1669 -> merge -> issue closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1488.md
- Review Entry: .loom/reviews/WI-1488.json
- Validation Entry: python3 tools/loom.py help --json; python3 tools/loom.py fact-chain --target . --json; python3 tools/loom.py suite validate --target . --item WI-1488 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1488 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1488 --json; python3 tools/skills_surface.py check --surface docs-reference-sync; npm --prefix packages/loom-installer run check:docs; python3 tools/check_cli_contract.py; python3 tools/loom_check.py --profile source --source-surface contract-only; python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; PR metadata render/preflight/readback compare for #1669; targeted rg for unsupported repo-local install recommendations; git diff --check
- Closing Condition: PR merged after docs/help/migration guidance consistently points to metadata-only repository adoption, global `loom` CLI, Codex user-level plugin, agent-safe summary/artifact locator output by default, and explicit full diagnostics only for debugging/audit.
- Current Checkpoint: build
- Current Stop: WI-1488 docs/help/migration update is implemented on branch work/1488-docs-migration and PR #1669; final build-level fact-chain, suite validate, suite evidence validate, suite carrier validate, shadow parity, contract-only source check, diff check, focused docs checks, CLI help readback, docs reference sync, installer docs sync, PR metadata preflight/readback, full CLI contract checks, and pre-review passed.
- Next Step: Record current-head review for PR #1669, then refresh PR gate metadata after the review carrier commit.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-21 WI-1488 documentation/help/migration validation passed on branch work/1488-docs-migration / PR #1669 head 92ca545afd3f10a765d6d847998b0aa5ddad88be: `python3 tools/loom.py help --json`; `python3 tools/loom.py fact-chain --target . --json`; `python3 tools/loom.py suite validate --target . --item WI-1488 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1488 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1488 --json`; `python3 tools/skills_surface.py check --surface docs-reference-sync`; `npm --prefix packages/loom-installer run check:docs`; `python3 tools/check_cli_contract.py`; `python3 tools/loom_check.py --profile source --source-surface contract-only`; `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`; `python3 .loom/bin/loom_flow.py flow pre-review --target . --item WI-1488 --pr 1669 --branch work/1488-docs-migration`; PR metadata render/preflight/readback compare for #1669; targeted legacy recommendation `rg`; `git diff --check`.
- Recovery Boundary: WI-1488 owns docs/help/migration guidance only. It does not publish #1658, run final #1489 closeout, implement downstream migration, or change runtime/plugin behavior.
- Current Lane: docs-migration

## Runtime Evidence

- Run Entry: 2026-06-21 WI-1488 docs/help/migration update in progress.
- Logs Entry: local command output retained in current Codex milestone/11 thread; full CLI contract check completed in 564.72s.
- Diagnostics Entry: Documentation and help-facing contracts now prefer global `loom` CLI, metadata-only repository adoption, Codex user-level plugin, agent-safe summary/artifact locator output, and explicit `--full-output` only for debugging/audit.
- Verification Entry: `python3 tools/loom.py help --json`; `python3 tools/loom.py fact-chain --target . --json`; `python3 tools/loom.py suite validate --target . --item WI-1488 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1488 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1488 --json`; `python3 tools/skills_surface.py check --surface docs-reference-sync`; `npm --prefix packages/loom-installer run check:docs`; `python3 tools/check_cli_contract.py`; `python3 tools/loom_check.py --profile source --source-surface contract-only`; `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`; `python3 .loom/bin/loom_flow.py flow pre-review --target . --item WI-1488 --pr 1669 --branch work/1488-docs-migration`; PR metadata render/preflight/readback compare for #1669; targeted legacy recommendation `rg`; `git diff --check`.
- Lane Entry: milestone-11-docs-migration

## Sources

- Static Truth: .loom/work-items/WI-1488.md
- Dynamic Truth: .loom/progress/WI-1488.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
