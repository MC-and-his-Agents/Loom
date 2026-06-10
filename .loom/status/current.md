# Current Status

## Derived Fact Chain View

- Item ID: WI-1251
- Goal: Make Codex App fallback fixtures deterministic by isolating them from workstation/session discovery drift unless a scenario explicitly opts into that dependency.
- Scope: Issue #1251 / PR #1413 only: Codex App fallback fixture environment isolation, synchronized loom_check runtime copies, demo metadata hash refresh, and focused validation evidence; no #1249 label ownership, no #1250 fixture group rename, no #1252 snapshot/bootstrap reuse, no #1253 fast/full validation policy.
- Execution Path: issue #1251 -> branch work/1251-codex-app-fallback-fixtures -> PR #1413 -> scheduler-owned review/pr-gate/controlled merge/closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1251.md
- Review Entry: .loom/reviews/WI-1251.json
- Validation Entry: git diff --check; py_compile_clean touched loom_check.py copies; skills_surface.py check; check_loom_check_runtime_regressions.py; focused #1251 fallback env validation; PR metadata preflight/readback; hosted checks readback
- Closing Condition: PR #1413 is reviewed/gated by the scheduler on the current head, merged through the controlled path, and #1251 closeout is consumed without weakening fallback isolation, repository truth boundaries, fail-closed behavior, or required coverage.
- Current Checkpoint: build
- Current Stop: PR #1413 branch is rebased onto origin/main dba1f55690150336211c767069c9189df90c000a and now includes a review-run fixture env helper fix for the hosted NameError while preserving #1251 Codex App fallback fixture isolation and WI-1251 not_applicable suite metadata. Local focused validation and review-run source surface pass; carrier refresh and shadow parity remain blocked only by scheduler-owned current-head review/shadow drift.
- Next Step: Scheduler should record or authorize current-head semantic review for PR #1413 after the refreshed head is pushed, then run scheduler-owned PR gate / controlled merge / closeout if gates pass.
- Blockers: Scheduler-owned current-head semantic review is missing: .loom/reviews/WI-1251.json remains a stale scaffold for reviewed head a9d6dfdb2c84e7761f457657a004283a48dfa00c, so carrier refresh and shadow-parity cannot be treated as gate-ready evidence by T4.
- Latest Validation Summary: After rebase onto origin/main dba1f55690150336211c767069c9189df90c000a and the review_run_fixture_env helper fix, focused validation passed: git diff --check; git diff --check origin/main...HEAD; PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py over canonical/generated/runtime/demo loom_check.py copies plus tools/check_loom_check_runtime_regressions.py; python3 tools/skills_surface.py check; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_loom_check_runtime_regressions.py; make loom-demo-new-project-check; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface review-run .; suite inspect passed with Suite path: not_applicable at .loom/specs/WI-1251/spec.md; suite validate exits 1 with result=not_applicable and blocking_gaps=[]; fact-chain and verify pass. carrier refresh --dry-run and shadow-parity remain blocked by scheduler-owned stale review scaffold/shadow drift.
- Recovery Boundary: WI-1251 only: Codex App fallback fixture isolation, synchronized loom_check runtime copies, demo metadata hash refresh, focused fallback validation, PR metadata/head binding, and minimal WI-1251 Loom carriers. No #1249 label ownership, #1250 fixture group rename, #1252 implementation ownership, #1253 fast/full entrypoint policy, merge, release, or closeout.
- Current Lane: daily-cli-codex-app-fallback-fixtures

## Runtime Evidence

- Run Entry: PR #1413 implementation head a9d6dfdb2c84e7761f457657a004283a48dfa00c passed scoped #1251 local validation and PR metadata readback before scheduler-owned review/gate.
- Logs Entry: worker thread 019eb12d-aba6-7392-8dd1-26bb4d81b393 and scheduler thread 019eaf94-f0bd-79a3-a396-83d6428b2777 command readbacks for WI-1251.
- Diagnostics Entry: WI-1251 isolates Codex App fallback fixtures from ambient workstation/session discovery by using controlled fake HOME/CODEX_HOME/temp roots and explicit fake app-server fallback inputs; no #1249 label ownership, #1250 group rename, #1252 snapshot/bootstrap reuse, or #1253 fast/full policy is included.
- Verification Entry: local validation passed for #1251 implementation and carrier activation: git diff --check, py_compile_clean for touched loom_check.py copies, skills_surface.py check, check_loom_check_runtime_regressions.py, focused fallback env probe, fact-chain readback, verify, and PR metadata readback; full review-run/current-head review/pr-gate remain scheduler-owned.
- Lane Entry: daily-cli-codex-app-fallback-fixtures

## Sources

- Static Truth: .loom/work-items/WI-1251.md
- Dynamic Truth: .loom/progress/WI-1251.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
