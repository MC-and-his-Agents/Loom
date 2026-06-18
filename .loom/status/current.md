# Current Status

## Derived Fact Chain View

- Item ID: WI-1578
- Goal: Fix PR metadata closeout surface rendering so closeout-only carrier PRs can be recognized by PR gate.
- Scope: Issue #1578 only: make `loom pr metadata-render/readback/preflight/update --surface closeout` emit and consume a `closeout` PR metadata machine surface while preserving `merge_ready` compatibility for review and pre-review consumers. Keep #1577 carrier content, hosted checks, controlled merge, release/no-release closeout, and one-shot closeout run out of scope.
- Execution Path: issue #1578 -> branch work/1578-pr-metadata-closeout-surface -> PR metadata closeout surface runtime -> focused pr-metadata contract check -> generated runtime parity -> PR
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1578.md
- Review Entry: .loom/reviews/WI-1578.json
- Validation Entry: PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata; PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift; git diff --check
- Closing Condition: PR for #1578 is merged, issue #1578 is closed, and PR #1577 can regenerate/readback closeout metadata with `surface=closeout`.
- Current Checkpoint: build
- Current Stop: Closeout surface metadata rendering now emits `surface=closeout`; focused pr-metadata contract, suite validate, suite evidence validate, suite carrier validate, py_compile, generated runtime parity, carrier refresh, and diff whitespace checks passed locally.
- Next Step: Record current-head review, update PR metadata after PR creation, run PR gate, then merge when hosted checks pass.
- Blockers: None
- Latest Validation Summary: 2026-06-18T11:51Z validation passed for WI-1578 branch work/1578-pr-metadata-closeout-surface: PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata; PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1578 --json; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1578 --json; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1578 --json; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1578 --write; git diff --check.
- Recovery Boundary: WI-1578/#1578 only. Do not modify #1577 closeout-only carrier files, hosted workflow semantics, controlled merge behavior, release/no-release closeout, or one-shot post-merge closeout run.
- Current Lane: milestone-12-pr-metadata-closeout-surface-fix

## Runtime Evidence

- Run Entry: 2026-06-18 WI-1578 PR metadata closeout surface fix
- Logs Entry: local command output retained in current Codex milestone/12 thread
- Diagnostics Entry: PR #1577 closeout-only gate exposed that `--surface closeout` metadata rendered/read back as `merge_ready`; WI-1578 isolates the wrapper/runtime metadata surface contract fix.
- Verification Entry: PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata; PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1578 --json; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1578 --json; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1578 --json; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1578 --write; git diff --check
- Lane Entry: milestone-12-pr-metadata-closeout-surface-fix

## Sources

- Static Truth: .loom/work-items/WI-1578.md
- Dynamic Truth: .loom/progress/WI-1578.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
