# Current Status

## Derived Fact Chain View

- Item ID: WI-1541
- Goal: Add a PR metadata machine carrier render, update, and readback CLI surface so operators stop hand-editing PR bodies before review, merge-ready, and closeout gates.
- Scope: Implement the #1541 milestone/12 slice by adding `loom pr metadata-render`, `loom pr metadata-readback`, and `loom pr metadata-update` wrapper/runtime paths, focused CLI contract coverage, PR template guidance, and generated runtime copy parity. Write ownership is limited to WI-1541 carriers/specs, PR metadata runtime/wrapper code, generated `loom_flow.py` runtime copies, `tools/check_cli_contract.py`, and `.github/PULL_REQUEST_TEMPLATE.md`; keep hosted admission #1512, closeout-specific gate #1533, one-shot closeout run #1555, and release/no-release closeout #1515 out of scope.
- Execution Path: issue #1541 -> branch work/1541-pr-metadata-update-v2 -> PR metadata render/readback/update runtime -> focused contract checks -> PR metadata self-consumption -> review/merge-ready
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1541.md
- Review Entry: .loom/reviews/WI-1541.json
- Validation Entry: PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata; PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift; git diff --check
- Closing Condition: PR for #1541 is merged, issue #1541 is closed after render/update/readback host evidence is read back, and #1514/#1534 can consume the PR metadata surface without hand-editing PR body machine blocks.
- Current Checkpoint: build
- Current Stop: PR metadata render, readback, and update surfaces are implemented on branch work/1541-pr-metadata-update-v2 at head 5086086d88fca72e31a51f5660df483cc797bb5d and are ready for review carrier recording.
- Next Step: Record spec and implementation review, then use `loom pr metadata-update` on the #1541 PR to gather live host readback evidence.
- Blockers: None
- Latest Validation Summary: 2026-06-17T23:11Z validation passed for #1541 head 5086086d88fca72e31a51f5660df483cc797bb5d: PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata; PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift; git diff --check.
- Recovery Boundary: This slice only productizes PR metadata render/update/readback. It does not implement hosted freeze admission #1512, closeout-specific gate #1533, one-shot post-merge closeout run #1555, Work Item startup audit UX #1542, docs convergence #1514/#1534, or release/no-release closeout #1515.
- Current Lane: milestone-12-wave0-pr-metadata-update

## Runtime Evidence

- Run Entry: 2026-06-17 WI-1541 PR metadata render/update/readback implementation slice
- Logs Entry: local command output retained in current Codex thread
- Diagnostics Entry: WI-1541 adds `loom pr metadata-render`, `metadata-readback`, and `metadata-update` for the repo-specific PR metadata machine carrier, while leaving hosted admission and closeout gate behavior unchanged.
- Verification Entry: `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py pr --help`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`; `git diff --check`.
- Lane Entry: milestone-12-wave0-pr-metadata-update

## Sources

- Static Truth: .loom/work-items/WI-1541.md
- Dynamic Truth: .loom/progress/WI-1541.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
