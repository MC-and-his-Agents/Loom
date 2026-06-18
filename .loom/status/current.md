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
- Current Checkpoint: closed_out
- Current Stop: Host readback consumed: PR #1579 merged into main at 6dd205e70b2dd49517b5fb0c1454a4736568030d, and issue #1578 is closed.
- Next Step: No further action for this carrier; retained as terminal evidence for milestone/12 convergence.
- Blockers: None
- Latest Validation Summary: 2026-06-18T12:42Z validation passed for WI-1578 head 9ed1fc07: make loom-demo-new-project-check; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata; direct closeout metadata render/readback/preflight fixture; PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/check_cli_contract.py; make loom-check; PR #1579 metadata readback surface merge_ready head_sha 9ed1fc07; code/spec review records refreshed to 9ed1fc07.
- Recovery Boundary: WI-1578/#1578 only. Do not modify #1577 closeout-only carrier files, hosted workflow semantics, controlled merge behavior, release/no-release closeout, or one-shot post-merge closeout run.
- Current Lane: milestone-12-pr-metadata-closeout-surface-fix

## Runtime Evidence

- Run Entry: 2026-06-18 WI-1533 closeout-specific gate implementation
- Logs Entry: local command output retained in current Codex milestone/12 thread
- Diagnostics Entry: #1533 inventory confirmed existing closeout freeze and PR gate behavior were present; the remaining stable surface was the machine-readable closeout-specific verdict/escalation contract.
- Verification Entry: targeted closeout/pr-gate contract fixtures, generated runtime drift check, py_compile, suite evidence/carrier validation, fact-chain, and shadow parity.
- Lane Entry: milestone-12-closeout-specific-gate

## Sources

- Static Truth: .loom/work-items/WI-1578.md
- Dynamic Truth: .loom/progress/WI-1578.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
