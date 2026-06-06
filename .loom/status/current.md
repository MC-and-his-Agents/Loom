# Current Status

## Derived Fact Chain View

- Item ID: WI-1230-1231
- Goal: Complete WI-1230 and WI-1231 by adding structured terminal closeout metadata to progress carriers and splitting local retire, host closeout sync, and carrier closeout sync command responsibilities.
- Scope: CLI/runtime source, schema/docs/tests/fixtures, generated runtime copies, and Loom carriers for issues #1230 and #1231. Preserve local-only workspace retire, host closeout/reconciliation sync, and explicit versioned carrier closeout sync boundaries.
- Execution Path: issues #1230/#1231 -> branch work/1230-1231-idle-closeout-command-foundation -> PR -> CI/review -> controlled merge -> post-merge closeout for both issues.
- Workspace Entry: ./././.
- Recovery Entry: .loom/progress/WI-1230-1231.md
- Review Entry: .loom/reviews/WI-1230-1231.json
- Validation Entry: git diff --check; py_compile_clean targeted runtime; tools/check_cli_contract.py targeted/full as feasible; loom_check contract/source surfaces; PR gate; hosted checks.
- Closing Condition: Implementation PR is merged through the controlled wrapper, terminal metadata and command responsibility split are consumed by review and closeout gates, and #1230/#1231 are closed with post-merge closeout evidence.
- Current Checkpoint: merge
- Current Stop: PR #1338 is open at head d641cbb0bbdb7cf76bf888013ec8223b0a76cae1 after implementation, demo fixture sync, PR body readback, metadata preflight, and authored review were recorded; local PR gate consumed review approval and is being rerun after workspace carrier isolation from WI-1269.
- Next Step: Rerun local PR gate, wait for hosted checks, merge through controlled wrapper, then complete post-merge closeout for #1230/#1231.
- Blockers: None recorded.
- Latest Validation Summary: Validation passed for WI-1230-1231 on 2026-06-06 after demo fixture sync and implementation-contract refresh: `git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/loom.py tools/check_cli_contract.py src/skills/shared/scripts/fact_chain_support.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/fact_chain_support.py skills/shared/scripts/loom_flow.py .loom/bin/fact_chain_support.py .loom/bin/loom_flow.py`; runtime parity cmp across src/skills/shared, skills/shared, .loom/bin, and all skills/loom-* runtime copies; `python3 tools/loom.py skills check --target /Users/mc/.codex/worktrees/df54/Loom --json`; `python3 tools/loom.py suite validate --target /Users/mc/.codex/worktrees/df54/Loom --item WI-1230-1231 --json`; `python3 tools/loom.py suite carrier validate --target /Users/mc/.codex/worktrees/df54/Loom --item WI-1230-1231 --json`; `python3 tools/loom.py suite evidence validate --target /Users/mc/.codex/worktrees/df54/Loom --item WI-1230-1231 --json`; `python3 tools/loom.py carrier closeout-sync --target /Users/mc/.codex/worktrees/df54/Loom --item WI-1230-1231 --terminal-state not_applicable --issue 1230 --pr not_applicable --merge-commit not_applicable --target-branch main --closed-at not_applicable --evidence-locator not_applicable --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py` -> `cli contract checks passed`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface aggregate` passed in 186.19s after merging origin/main; `make loom-demo-new-project-check` -> `demo bootstrap fixture: OK (examples/new-project)`; `python3 tools/loom.py closeout --target /Users/mc/.codex/worktrees/df54/Loom --json` -> `result=pass` before PR creation. Hosted checks for PR #1338 initially failed because demo bootstrap fixture drift was present before this sync; rerun is required for head 2cc5405625b74ea74cda2a3a82c895a67191dafa.
- Recovery Boundary: Keep scope limited to #1230/#1231 terminal metadata and command responsibility split. Do not change unrelated closeout behavior, unsafe host mutation semantics, repair/apply flows, or main workspace state.
- Current Lane: implementation-merge-ready

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: git diff --check; py_compile; runtime parity; skills check; suite validate; suite carrier validate; suite evidence validate; carrier closeout-sync dry-run; tools/check_cli_contract.py
- Lane Entry: implementation

## Sources

- Static Truth: .loom/work-items/WI-1230-1231.md
- Dynamic Truth: .loom/progress/WI-1230-1231.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
