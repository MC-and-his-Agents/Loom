# Current Status

## Derived Fact Chain View

- Item ID: WI-1509
- Goal: Pin PR body rendered/readback hashes and machine metadata block fingerprints inside the gate freeze snapshot so stale PR body races block before hosted gate admission.
- Scope: Issue #1509 only: consume existing `pr metadata-preflight` body-file evidence, record rendered body hash, readback body hash, machine metadata block raw excerpt hashes and fingerprints in `loom-gate-freeze/v1`, make `loom gate freeze check` block on rendered/readback mismatch and PR Work Item/head/branch carrier mismatch, surface a precise next action to re-run `gh pr edit --body-file`, read back the PR body, and rerun freeze. Do not rewrite the PR template, change the human PR body display layer, replace `pr metadata-preflight`, implement carrier/shadow freshness (#1510), review/head drift policy (#1511), hosted admission consumption (#1512), broad classifier expansion (#1513), docs milestone sweep (#1514), or release/no-release closeout (#1515).
- Execution Path: issue #1509 -> branch `work/1509-pr-body-hash-pin` -> PR -> CLI/runtime contract checks -> local validation -> PR metadata/readback -> review/merge-ready.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1509.md
- Review Entry: .loom/reviews/WI-1509.json
- Validation Entry: `git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/loom.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py gate freeze check --target . --item WI-1509 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1509 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1509 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1509 --json`
- Closing Condition: PR for #1509 is merged, issue #1509 is closed/completed, and gate freeze snapshots expose and enforce PR body hash/readback pins before hosted admission can consume stale PR body metadata.
- Current Checkpoint: build
- Current Stop: WI-1509 runtime implementation and local contract validation completed on branch `work/1509-pr-body-hash-pin`.
- Next Step: Prepare PR metadata/readback, review, merge-ready, hosted checks, and closeout for issue #1509.
- Blockers: None
- Latest Validation Summary: 2026-06-16T22:21Z WI-1509 local validation passed: `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/loom.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py` passed all 6 surfaces in 243.34s and covered PR body pin pass, rendered/readback hash drift block, and carrier binding drift block; `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift` passed; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .` passed; suite validate, suite evidence validate, and suite carrier validate for WI-1509 passed. `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py gate freeze check --target . --item WI-1509 --json` emitted `loom-gate-freeze/v1` and `pr_body_pin` but correctly remained blocked because review, shadow freshness, release metadata, and live PR metadata are not yet established for the pending PR.
- Recovery Boundary: WI-1509/#1509 only. Do not implement #1510 carrier/shadow freshness, #1511 review/head policy, #1512 hosted admission consumption, #1513 milestone-wide classifier expansion, #1514 docs/skills sweep, #1515 release/no-release closeout, or unrelated runtime changes.
- Current Lane: milestone-12-wi-1509-pr-body-hash-pin

## Runtime Evidence

- Run Entry: 2026-06-17 WI-1509 branch and carrier initialization
- Logs Entry: local command output retained in current Codex thread
- Diagnostics Entry: WI-1509 is active locally; runtime implementation and local contract validation are complete, while PR/review/merge-ready evidence is pending.
- Verification Entry: `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/loom.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1509 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1509 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1509 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py gate freeze check --target . --item WI-1509 --json` emitted the new `pr_body_pin` binding and blocked only on expected pending PR/review/shadow/release inputs.
- Lane Entry: milestone-12-wi-1509-pr-body-hash-pin

## Sources

- Static Truth: .loom/work-items/WI-1509.md
- Dynamic Truth: .loom/progress/WI-1509.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
