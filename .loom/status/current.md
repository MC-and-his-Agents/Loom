# Current Status

## Derived Fact Chain View

- Item ID: WI-763
- Goal: Host-enforce Loom semantic review approval before PR merge
- Scope: Add a PR-specific merge gate, host workflow, controlled merge wrapper, PR #762 regression evidence, generated skill surfaces, and validation proving raw review evidence cannot satisfy approval.
- Execution Path: self-governance/pr-semantic-review-gate/763
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-763.md
- Review Entry: .loom/reviews/WI-763.json
- Validation Entry: python3 tools/loom_check.py . && make skills-check && git diff --check
- Closing Condition: PR gate is implemented and required by host branch protection or ruleset; this branch has a fresh authored review record for the PR head; controlled merge consumes only the authored Loom review record and required-check readback; #763 and child issues contain proof; implementation is merged; main readback proves loom-pr-merge-gate is required.
- Current Checkpoint: merge checkpoint
- Current Stop: Local implementation, ruleset fixture support, review record, merge checkpoint, adopt verify, shadow parity, and full loom_check validation are complete on branch harden-pr-semantic-review-gate.
- Next Step: Open the PR, require loom-pr-merge-gate on main, prove live PR-head check and host readback, then merge through controlled-merge.
- Blockers: None recorded.
- Latest Validation Summary: 2026-05-16 final local validation passed for WI-763: PYTHONPYCACHEPREFIX=/tmp/loom-pycache python3 -m py_compile for touched Loom runtime entrypoints -> OK; make skills-check -> OK; python3 tools/loom_flow.py adopt verify --target . --item WI-763 -> pass; python3 tools/loom_flow.py shadow-parity --target . -> pass; python3 tools/loom_flow.py checkpoint merge --target . --item WI-763 -> pass before final validation refresh; MISE_NO_CONFIG=1 LOOM_INSTALLER_TEST_PYTHON_BIN=/Users/claw/.local/share/mise/installs/python/3.12.13/bin/python3.12 python3 tools/loom_check.py . -> OK (36 surfaces); git diff --check -> OK. Covered default review engine drift, strict OpenAI output schema, no formal review timeout, PR gate fail-closed cases, raw evidence bypass boundary, ruleset required-check fixture, and status-shadow carrier drift.
- Recovery Boundary: Branch harden-pr-semantic-review-gate; parent issue #763; active Work Item WI-763; raw review evidence remains runtime evidence only and never approval truth.
- Current Lane: self-governance / #763 semantic review host enforcement

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-763.md
- Dynamic Truth: .loom/progress/WI-763.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
