# Current Status

## Derived Fact Chain View

- Item ID: WI-1284
- Goal: Validate and record repo-local-cli CI evidence and closeout expectations after the #1282 workflow split, using actual hosted output from PR #1385 and PR #1387.
- Scope: Own issue #1284 only: record WI-1284 evidence and closeout expectation carriers that consume the frozen #1282 repo-local-cli command group contract and actual post-merge/readback hosted output from PR #1385 and PR #1387. Preserve existing loom-check required checks and no-release classification. Excluded: .github/workflows/loom-check.yml changes, #1283 local validation aliases/docs, #1259 closeout, Round 5, Round 7+, Deferred roadmap, release/package behavior, generated runtime, high-cost scheduler gates, controlled merge, and issue closeout.
- Execution Path: issue #1284 -> branch work/1284-repo-local-cli-evidence-closeout -> activate WI-1284 -> consume WI-1282 command group contract and #1385/#1387 hosted output -> write evidence/closeout carriers -> local validation -> PR metadata/head binding -> hosted check readback -> scheduler-owned gate.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1284.md
- Review Entry: .loom/reviews/WI-1284.json
- Validation Entry: git diff --check; repo-local-cli workflow command group readback; #1385/#1387 hosted run/job/log readback; python3 tools/loom.py suite inspect/validate/evidence validate/carrier validate --target . --item WI-1284 --json; python3 .loom/bin/loom_init.py fact-chain --target .; python3 .loom/bin/loom_init.py verify --target .; python3 .loom/bin/loom_flow.py purity-check --target . --item WI-1284; python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1284; PR metadata preflight/readback; hosted checks.
- Closing Condition: PR for #1284 is reviewed and gated by scheduler, merged through scheduler-owned controlled merge, issue #1284 is closed only by scheduler closeout, and post-merge closeout consumes PR, issue, target branch, no-release judgment, hosted checks, and WI-1284 evidence without changing repo-local-cli workflow semantics.
- Current Checkpoint: merge
- Current Stop: PR #1388 exists on branch `work/1284-repo-local-cli-evidence-closeout`; WI-1284 evidence and carrier validation passed; the pre-correction hosted `repo-local-cli`, `py-compile`, `demo-bootstrap`, and aggregate `loom-check` checks passed where applicable; mechanical PR body/checkpoint readiness correction is in progress; scheduler-owned current-head semantic review, draft decision, gate rerun, controlled merge, and closeout remain pending.
- Next Step: Finish PR #1388 gate-input readiness by keeping checkpoint vocabulary legal, adding legacy-visible Branch/Head SHA/Workspace body fields, refreshing PR metadata/head binding after the correction commit, then stop at scheduler-owned review/gate.
- Blockers: Scheduler-owned current-head semantic review, PR draft decision, and gate rerun remain pending after mechanical gate inputs are clean.
- Latest Validation Summary: 2026-06-09 gate-input readiness correction for WI-1284: scheduler consumed T3 report T3-report-202606092323-waiting-scheduler-gate and found `flow review` blocked before semantic review by unknown checkpoint `local_validation_passed`; this writeback changes the recovery checkpoint to accepted value `merge` without changing WI-1284 evidence scope or repo-local-cli workflow semantics. Prior local validation passed: suite evidence validate, suite carrier validate, suite inspect, expected suite validate not_applicable/no blocking gaps, fact-chain, verify, purity-check, shadow-parity, adopt verify, and git diff --check. Post-merge/readback evidence remains explicit: PR #1385 run 27210093374 job 80336435486 and PR #1387 run 27212248994 job 80344176543 passed `repo-local-cli` steps 3-9 in frozen order. Current PR #1388 pre-correction hosted run 27215428746 has `repo-local-cli` job 80355564329, `py-compile`, `demo-bootstrap`, and aggregate `loom-check` passing; `root-self-governance` and `loom-pr-merge-gate` remain blocked on scheduler-owned review/draft/gate inputs, not repo-local-cli behavior. Official `carrier refresh --write` reports refresh-needed for `.loom/shadow/closeout-loom.json` and `.loom/shadow/merge-ready-loom.json` but blocks on stale review/non-carrier drift; T3 did not record semantic approval to bypass that scheduler-owned blocker.
- Recovery Boundary: WI-1284 evidence/closeout expectation carrier and PR metadata gate-input readiness only. Consume completed facts from #1282 / PR #1385 / PR #1387 and current PR #1388 hosted readback; do not change `.github/workflows/loom-check.yml`, repo-local-cli command group names/order, #1283 alias/docs ownership paths, #1259 closeout, Round 5, Round 7+, Deferred roadmap, release/package behavior, generated runtime, high-cost scheduler gates, controlled merge, semantic approval, draft state, or issue closeout.
- Current Lane: repo-local-cli-surfaces

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: local command outputs in worker thread 019eacce-75b3-7c83-85a8-549fe578cb7f
- Diagnostics Entry: WI-1284 is an evidence-only repo-local-cli closeout carrier update; no runtime, workflow semantics, package, release, permission, or external-visible behavior change is expected.
- Verification Entry: suite evidence/carrier passed; suite validate returned expected `not_applicable` with no blocking gaps; fact-chain, verify, purity, shadow-parity, adopt verify, and `git diff --check` passed; scheduler-owned review and gate remain pending.
- Lane Entry: repo-local-cli-surfaces

## Sources

- Static Truth: .loom/work-items/WI-1284.md
- Dynamic Truth: .loom/progress/WI-1284.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
