# Current Status

## Derived Fact Chain View

- Item ID: WI-1140
- Goal: Make scenario skills consume full spec suite CLI JSON instead of reimplementing suite rules.
- Scope: #1140 only: update `src/skills/`, generated `skills/`, `.loom/bin/loom_flow.py`, `.loom/bootstrap/manifest.json`, `.loom/specs/WI-1138/task-carrier.md`, `tools/check_cli_contract.py`, full suite CLI docs, Loom carriers, and Loom-owned shadow evidence hashes for `.loom/status/current.md` so scenario skills consume `loom suite ... --json` outputs; ownership constraints are limited to these declared files. Do not implement consistency analyze, closeout reconciliation, host writes, new Work Items, `/speckit.*`, or `.specify/` surfaces.
- Execution Path: issue #1140 -> branch work/1140-suite-skills -> worktree /Users/mc/dev/Loom-worktrees/1140-suite-skills -> PR pending.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1140.md
- Review Entry: .loom/reviews/WI-1140.json
- Validation Entry: python3 tools/check_cli_contract.py; git diff --check; focused rg; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Closing Condition: #1140 PR is merged to main, closeout evidence records PR/head/merge/target branch/validation/Project state, #1140 is closed completed, and #1136 can consume the evidence.
- Current Checkpoint: merge
- Current Stop: Local implementation, review records, and merge checkpoint inputs are complete on branch work/1140-suite-skills; Project `Loom` remains In Progress and PR creation is next.
- Next Step: Push #1140, open the issue-scoped PR, run PR/merge-ready gates against the PR head, merge, closeout, and reconcile Project state.
- Blockers: None
- Latest Validation Summary: Local #1140 validation passed: `python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py tools/check_cli_contract.py`; `python3 tools/check_cli_contract.py`; `python3 tools/skills_surface.py check`; `git diff --check`; focused `rg` for suite consumption and forbidden `/speckit` / `.specify` surfaces; `python3 tools/check_release_surface.py`; `python3 tools/version_surface_check.py`; `python3 tools/check_npm_package.py`; `python3 tools/loom_check.py --profile source --source-surface contract-only .`; `python3 tools/loom.py suite validate --target . --item WI-1140 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1140 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1140 --json`; `python3 .loom/bin/loom_flow.py state-check --target . --item WI-1140`; `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`; `python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1140`; `python3 tools/loom.py gate spec-review --target . --item WI-1140 --json`; `python3 tools/loom.py gate review --target . --item WI-1140 --json`; `python3 tools/loom.py pre-review --target . --item WI-1140 --json`; `python3 tools/loom.py build --target . --item WI-1140 --build-evidence .loom/progress/WI-1140-build-evidence.json --json`; pre-PR `python3 tools/loom.py merge-ready --target . --item WI-1140 --json` consumed suite evidence/carrier CLI JSON and fell back only because the merge checkpoint and PR head are not yet present.
- Recovery Boundary: #1140 owns scenario skill consumption of suite CLI JSON only, plus Loom-owned shadow evidence hash refresh for `.loom/status/current.md` caused by this Work Item's status carrier update. It must not implement consistency analyze, closeout reconciliation, host writes, new truth carriers outside the Work Item suite, or any `/speckit.*` / `.specify/` surfaces.
- Current Lane: full-spec-suite-cli/scenario-skills-json-consumption

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: python3 tools/loom.py build --target . --item WI-1140 --json
- Verification Entry: .loom/progress/WI-1140.md
- Lane Entry: full-spec-suite-cli/scenario-skills-json-consumption

## Sources

- Static Truth: .loom/work-items/WI-1140.md
- Dynamic Truth: .loom/progress/WI-1140.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
