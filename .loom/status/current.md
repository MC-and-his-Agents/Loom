# Current Status

## Derived Fact Chain View

- Item ID: WI-1513
- Goal: Add a stable gate failure classifier vocabulary and next-action contract for gate freeze and downstream hosted/closeout consumers.
- Scope: Implement the #1513 milestone/12 slice by mapping existing gate freeze and validation failure kinds into stable classifier categories, including PR metadata drift, carrier refresh needed, shadow stale, review stale, host API unreadable, permission, hosted snapshot mismatch, suite evidence contract invalid, task carrier contract invalid, unsupported command surface, and release evidence phase errors. Write ownership is limited to WI-1513 carriers/specs, shared `loom_flow.py` runtime copies, and `tools/check_cli_contract.py`; keep hosted admission, closeout gate behavior, PR metadata rendering, and release/no-release closeout out of scope.
- Execution Path: issue #1513 -> branch work/1513-failure-classifier-v2 -> failure classifier vocabulary -> gate freeze payload normalization -> focused CLI contract checks -> PR metadata/readback -> review/merge-ready
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1513.md
- Review Entry: .loom/reviews/WI-1513.json
- Validation Entry: PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface aggregate; failure classifier targeted import check; git diff --check
- Closing Condition: PR #1564 is merged, issue #1513 is closed after hosted/closeout consumers can rely on the stable classifier vocabulary and next-action fields, and #1512/#1533/#1534 can consume #1513 without inventing a duplicate schema.
- Current Checkpoint: closed_out
- Current Stop: WI-1513 is closed out after PR #1564 merged into main at 01ab9e167985d9afb9b84fa544bfde1192dc15a9 and GitHub issue #1513 closed at 2026-06-17T22:37:29Z.
- Next Step: Consume #1513 as complete in #1512/#1533/#1514/#1534/#1515 milestone/12 convergence readback.
- Blockers: None
- Latest Validation Summary: 2026-06-17T22:21Z validation passed for PR #1564 head 25a6efa21ba1f29911cff031a7c4b9d59b211751: PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface aggregate; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py status --target . --json; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; PR body metadata preflight/readback for head 25a6efa21ba1f29911cff031a7c4b9d59b211751.
- Recovery Boundary: Current closeout sync only consumes completed #1513 facts and updates repo carriers. It does not implement hosted freeze admission #1512, closeout-specific gate #1533, PR metadata render/update #1541, Work Item startup audit #1542, one-shot closeout run #1555, or milestone release closeout #1515.
- Current Lane: milestone-12-wave0-failure-classifier-closeout

## Runtime Evidence

- Run Entry: 2026-06-17 WI-1513 gate failure classifier vocabulary and next-action implementation slice
- Logs Entry: local command output retained in current Codex thread
- Diagnostics Entry: WI-1513 adds stable `loom-failure-classifier/v1` categories and classifier-owned `next_action` output for gate freeze consumers, while leaving hosted admission and closeout gate behavior unchanged.
- Verification Entry: `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface aggregate`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_demo_bootstrap_fixture.py --surface fixture-drift`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_demo_bootstrap_fixture.py --surface canonicalization`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_demo_bootstrap_fixture.py --surface generation`; direct failure_classifier_payload next_action override check; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py status --target . --json`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`; PR body metadata preflight/readback for head 25a6efa21ba1f29911cff031a7c4b9d59b211751; `git diff --check`.
- Lane Entry: milestone-12-wave0-failure-classifier

## Sources

- Static Truth: .loom/work-items/WI-1513.md
- Dynamic Truth: .loom/progress/WI-1513.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
