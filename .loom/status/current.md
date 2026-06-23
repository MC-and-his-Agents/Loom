# Current Status

## Derived Fact Chain View

- Item ID: WI-1741
- Goal: 按 changed paths 为 ship 选择最小验证 profile
- Scope: Issue #1741: make loom ship select and report the smallest useful validation profile from PR changed paths while preserving explicit full validation override.
- Execution Path: issue #1741 -> branch work/1741-validation-profile -> PR pending -> controlled merge -> closeout
- Workspace Entry: .loom/..
- Recovery Entry: .loom/progress/WI-1741.md
- Review Entry: .loom/reviews/WI-1741.json
- Validation Entry: git diff --check; PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/loom.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper; PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py --surface plugin-payload-hash
- Closing Condition: PR merged and issue #1741 closed with ship validation profile selection evidence.
- Current Checkpoint: closed_out
- Current Stop: PR #1766 merged at ac5308d241dcdfd1901a7b329584dadecf1efeac; closeout PR #1767 records terminal metadata for WI-1741.
- Next Step: After closeout PR #1767 merges, close issue #1741 and allow dependent #1739/#1742 work to consume WI-1741 as closed out.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-23 closeout validation passed: git diff --check; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py fact-chain --target . --json --full-output; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group closeout-wrapper; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py carrier closeout-sync --target . --item WI-1741 --terminal-state merged --issue 1741 --pr 1766 --merge-commit ac5308d241dcdfd1901a7b329584dadecf1efeac --target-branch main --closed-at 2026-06-23T08:17:56Z --evidence-locator github.com/MC-and-his-Agents/Loom/pull/1766 --apply; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py carrier refresh --target . --item WI-1741 --apply; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py shadow-parity --target . --surface all --blocking.
- Recovery Boundary: WI-1741 owns ship validation profile selection, docs for the ship main path, and issue-scoped Loom carriers only; it does not implement repair chain, closeout e2e, or release behavior.
- Current Lane: validation-profile-closeout

## Runtime Evidence

- Run Entry: 2026-06-23 WI-1741 validation profile lane continued in issue-scoped worktree `work/1741-validation-profile`.
- Logs Entry: Local validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1741.md`.
- Diagnostics Entry: Ship now reports changed-path validation profile selection, selected source surface, reasons, and validation command hints.
- Verification Entry: Targeted ship wrapper contract, suite validate, suite evidence validate, suite carrier validate, carrier refresh readback, shadow parity, skills surface, and npm package checks are consumed before PR.
- Lane Entry: validation-profile

## Sources

- Static Truth: .loom/work-items/WI-1741.md
- Dynamic Truth: .loom/progress/WI-1741.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
