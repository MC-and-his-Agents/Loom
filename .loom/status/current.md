# Current Status

## Derived Fact Chain View

- Item ID: WI-1509
- Goal: Pin PR body rendered/readback hashes and machine metadata block fingerprints inside the gate freeze snapshot so stale PR body races block before hosted gate admission.
- Scope: Issue #1509 only: consume existing `pr metadata-preflight` body-file evidence, record rendered body hash, readback body hash, machine metadata block raw excerpt hashes and fingerprints in `loom-gate-freeze/v1`, make `loom gate freeze check` block on rendered/readback mismatch and PR Work Item/head/branch carrier mismatch, surface a precise next action to re-run `gh pr edit --body-file`, read back the PR body, and rerun freeze. Do not rewrite the PR template, change the human PR body display layer, replace `pr metadata-preflight`, implement carrier/shadow freshness (#1510), review/head drift policy (#1511), hosted admission consumption (#1512), broad classifier expansion (#1513), docs milestone sweep (#1514), or release/no-release closeout (#1515).
- Execution Path: issue #1509 -> branch `work/1509-pr-body-hash-pin` -> PR -> CLI/runtime contract checks -> local validation -> PR metadata/readback -> review/merge-ready.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1509.md
- Review Entry: .loom/reviews/WI-1509.json
- Validation Entry: git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/loom.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py gate freeze check --target . --item WI-1509 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1509 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1509 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1509 --json
- Closing Condition: PR for #1509 is merged, issue #1509 is closed/completed, and gate freeze snapshots expose and enforce PR body hash/readback pins before hosted admission can consume stale PR body metadata.
- Current Checkpoint: merge
- Current Stop: PR #1526 is open and ready on branch `work/1509-pr-body-hash-pin`; the hosted merge-gate timing failure was classified as stale PR body readback, then fixed locally by removing the high-frequency `gh pr view` suggestion from runtime gate guidance and refreshing root/demo runtime carriers.
- Next Step: Commit the refreshed validation carrier, record implementation review for the current head, update PR #1526 body to the final reviewed head, rerun local gate freeze/PR gate, then consume hosted required checks before merge.
- Blockers: None
- Latest Validation Summary: 2026-06-16T23:07Z WI-1509 post-CI validation passed: `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/loom.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py tools/check_cli_contract.py`; `git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py verify --target .`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py runtime-parity validate --target .`; `PYTHONDONTWRITEBYTECODE=1 python3 examples/new-project/.loom/bin/loom_init.py verify --target examples/new-project`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface distribution-regression .`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .`. The earlier hosted `loom-pr-merge-gate` failure on run 27653279714 was classified as PR body update/check-start timing drift; rerun job 81782191725 passed. The earlier hosted `loom-check` failure was classified as github-api-budget guard on a literal `gh pr view` recommendation in `loom_flow.py`; replacing it with host-API readback wording cleared local distribution-regression and contract-only checks.
- Recovery Boundary: WI-1509/#1509 only. Do not implement #1510 carrier/shadow freshness, #1511 review/head policy, #1512 hosted admission consumption, #1513 milestone-wide classifier expansion, #1514 docs/skills sweep, #1515 release/no-release closeout, or unrelated runtime changes.
- Current Lane: milestone-12-wi-1509-pr-body-hash-pin

## Runtime Evidence

- Run Entry: 2026-06-17 WI-1509 branch and carrier initialization
- Logs Entry: local command output retained in current Codex thread
- Diagnostics Entry: WI-1509 is active locally; runtime implementation, PR #1526 metadata readback, source contract-only, and local contract validation are complete, while review and shadow freshness are pending.
- Verification Entry: `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/loom.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`; `git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile consumer examples/new-project`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1509 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1509 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1509 --json`; PR body rendered/readback metadata preflight for PR #1526; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py gate freeze check --target . --item WI-1509 --pr 1526 --branch work/1509-pr-body-hash-pin --body-file .loom/runtime/pr/WI-1509-pr-body.md --compare-body-file .loom/runtime/pr/WI-1509-pr-body-readback.md --json` emitted `pr_body_pin.result=pass` and blocked only on pending review/shadow freshness inputs.
- Lane Entry: milestone-12-wi-1509-pr-body-hash-pin

## Sources

- Static Truth: .loom/work-items/WI-1509.md
- Dynamic Truth: .loom/progress/WI-1509.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
