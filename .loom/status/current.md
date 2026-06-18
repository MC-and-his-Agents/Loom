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
- Current Checkpoint: merge
- Current Stop: PR #1579 is open at head 9ed1fc07 with PR metadata readback, refreshed code/spec review evidence, and full local loom-check passing.
- Next Step: Wait for hosted checks for PR #1579 at head 9ed1fc07, then rerun local PR gate/merge check if hosted status is green before merge-ready.
- Blockers: None
- Latest Validation Summary: 2026-06-18T12:42Z validation passed for WI-1578 head 9ed1fc07: make loom-demo-new-project-check; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata; direct closeout metadata render/readback/preflight fixture; PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/check_cli_contract.py; make loom-check; PR #1579 metadata readback surface merge_ready head_sha 9ed1fc07; code/spec review records refreshed to 9ed1fc07.
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
