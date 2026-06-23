# Current Status

## Derived Fact Chain View

- Item ID: WI-1740
- Goal: 实现 review stale 分级与 generated-only drift 判定
- Scope: Issue #1740: classify post-review head drift as carrier-only, generated-only, carrier-and-generated-only, implementation-drift-only, or stale so generated drift does not create full semantic review friction while source and behavior drift still fail closed.
- Execution Path: issue #1740 -> branch work/1740-review-freshness -> PR pending -> controlled merge -> closeout
- Workspace Entry: .loom/..
- Recovery Entry: .loom/progress/WI-1740.md
- Review Entry: .loom/reviews/WI-1740.json
- Validation Entry: git diff --check; python3 -m py_compile skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group pr-metadata
- Closing Condition: PR merged and issue #1740 closed with review freshness classification evidence.
- Current Checkpoint: merge
- Current Stop: WI-1740 review freshness classifier, generated-only validation action payload, runtime copies, plugin payload, focused pr-metadata regression, spec review, and implementation review are ready for PR gate.
- Next Step: Push work/1740-review-freshness, open PR for issue #1740, read back PR metadata, run hosted checks, then merge and close out.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-23 local validation passed: git diff --check; python3 -m py_compile skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_flow.py plugins/loom/skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group pr-metadata; PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check; suite validate/evidence/carrier validate for WI-1740; spec review record .loom/reviews/WI-1740.spec.json allow; implementation review record .loom/reviews/WI-1740.json allow; checkpoint merge pass; carrier refresh --apply readback remaining_refresh=[]; shadow-parity all blocking passed.
- Recovery Boundary: WI-1740 owns review head binding freshness classification, generated-only drift diagnostics, focused regression coverage, and WI-1740 readiness carriers only.
- Current Lane: review-freshness

## Runtime Evidence

- Run Entry: 2026-06-23 WI-1738 ship inference lane continued in issue-scoped worktree `work/1738-ship-inference`.
- Logs Entry: Local validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1738.md`.
- Diagnostics Entry: Ship now records inferred branch/head/target bindings and passes effective bindings to delegated gates.
- Verification Entry: Targeted ship wrapper contract, suite validate, suite evidence validate, suite carrier validate, shadow parity, hosted checks, and controlled merge are consumed before merge.
- Lane Entry: ship-inference

## Sources

- Static Truth: .loom/work-items/WI-1740.md
- Dynamic Truth: .loom/progress/WI-1740.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
