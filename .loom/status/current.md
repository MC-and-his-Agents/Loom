# Current Status

## Derived Fact Chain View

- Item ID: WI-1280
- Goal: Complete issue #1280 by splitting source-self installed route, flow, runtime parity, and install-layout dependent fixtures into a stable named `installed-runtime` source surface while preserving embedded runtime and repo-local compatibility, aggregate `source-self-fixture` behavior, and the #1276/#1277/#1278/#1279 `--source-surface` runner contract.
- Scope: Allowed: `loom_check.py` source-surface registry/runner contract and generated skills runtime parity for installed-runtime fixtures; WI-1280 progress/status/spec/evidence carriers; PR metadata for the #1280 PR. Excluded: #1258 parent closeout, Round 4/Round 6+/Deferred roadmap work, #1276/#1277/#1278/#1279 implementation or closeout changes except read-only contract reference, release/package/workflow behavior, and scheduler-owned review/guardian/loom_check gate consumption, controlled merge, post-merge readback, and closeout.
- Execution Path: issue #1280 -> branch `work/1280-source-self-installed-runtime-fixtures-r2` -> named `installed-runtime` source surface -> generated skills runtime parity -> focused installed-runtime validation -> aggregate source-self-fixture validation -> PR metadata/head binding -> scheduler-owned gate.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1280.md
- Review Entry: .loom/reviews/WI-1280.json
- Validation Entry: `git diff --check`; `python3 tools/py_compile_clean.py tools/loom_check.py src/skills/shared/scripts/loom_check.py skills/shared/scripts/loom_check.py skills/loom-*/.loom-runtime/shared/scripts/loom_check.py`; `python3 tools/loom.py skills check --target . --json`; `python3 tools/loom_check.py --profile source --source-surface contract-only .`; `python3 tools/loom_check.py --profile source --source-surface installed-runtime .`; `python3 tools/loom_check.py --profile source --source-surface source-self-fixture .`; suite/fact-chain/carrier/shadow/PR metadata preflight/readback checks; hosted PR checks.
- Closing Condition: PR for #1280 is current-head reviewed and merged through scheduler-owned gate; issue #1280 is closed/completed; parent #1258 remains open until all children close and closeout is consumed.
- Current Checkpoint: build
- Current Stop: T5R is stopped at `waiting-scheduler-gate` for PR #1382; scheduler-authored semantic/spec review artifacts have been produced for implementation head `3156322650b4e80352adea60d0e1348f74f035b9` and consumed as carrier-only drift on current head `a2ebe3d7f1cb654d46d30b0a777dd61c599770d9`.
- Next Step: Complete scheduler-owned merge-ready/pr-gate/loom_check gate consumption for PR #1382, then run controlled merge and post-merge readback for #1280.
- Blockers: None
- Latest Validation Summary: 2026-06-09 worker validation on branch `work/1280-source-self-installed-runtime-fixtures-r2`: `git diff --check` passed; `python3 tools/py_compile_clean.py tools/loom_check.py src/skills/shared/scripts/loom_check.py skills/shared/scripts/loom_check.py skills/loom-adopt/.loom-runtime/shared/scripts/loom_check.py skills/loom-build/.loom-runtime/shared/scripts/loom_check.py skills/loom-handoff/.loom-runtime/shared/scripts/loom_check.py skills/loom-init/.loom-runtime/shared/scripts/loom_check.py skills/loom-merge-ready/.loom-runtime/shared/scripts/loom_check.py skills/loom-pre-review/.loom-runtime/shared/scripts/loom_check.py skills/loom-resume/.loom-runtime/shared/scripts/loom_check.py skills/loom-retire/.loom-runtime/shared/scripts/loom_check.py skills/loom-review/.loom-runtime/shared/scripts/loom_check.py skills/loom-spec-review/.loom-runtime/shared/scripts/loom_check.py skills/loom-story/.loom-runtime/shared/scripts/loom_check.py` passed; `python3 tools/loom.py skills sync --target . --apply --json` passed; `python3 tools/loom.py skills check --target . --json` passed; `python3 tools/loom_check.py --profile source --help` exposes `installed-runtime`; `python3 tools/loom_check.py --profile source --source-surface contract-only .` passed; `python3 tools/loom_check.py --profile source --source-surface installed-runtime .` passed with elapsed 113.55s and failures=0; aggregate `python3 tools/loom_check.py --profile source --source-surface source-self-fixture .` consumed and passed `merge-gate`, `closeout-reconciliation`, `retire-workspace`, new `installed-runtime` with elapsed 81.29s, and subsequent source-self fixture steps, but finished with 4 unrelated `review-run-fixture` failures listed in Blockers; `python3 .loom/bin/loom_flow.py work-item update --target . --item WI-1280 --activate` passed; `python3 .loom/bin/loom_init.py fact-chain --target .` passed; `python3 tools/loom.py suite validate --target . --item WI-1280 --json` passed; `python3 tools/loom.py suite evidence validate --target . --item WI-1280 --json` passed; `python3 tools/loom.py suite carrier validate --target . --item WI-1280 --json` passed; `python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1280 --write` passed; `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking` passed.
- Recovery Boundary: Do not implement #1258 parent closeout, Round 4/Round 6+/Deferred roadmap, #1276/#1277/#1278/#1279 implementation or closeout changes, release/package/workflow behavior, scheduler-owned semantic/spec review artifacts, guardian/loom_check high-cost gate consumption, controlled merge, post-merge readback, or closeout in this worker branch.
- Current Lane: source-self-installed-runtime-fixtures

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: local command outputs in worker thread 019eab0f-b79e-7ab1-856e-205b0a288c41
- Diagnostics Entry: `installed-runtime` source surface added through canonical runtime and generated skills sync; no release/package/workflow behavior changes expected.
- Verification Entry: focused `installed-runtime`, `contract-only`, skills parity, compile, and diff checks passed; aggregate `source-self-fixture` consumed and passed `installed-runtime`; non-#1280 `review-run-fixture` residue is classified outside the WI-1280 blocker path.
- Lane Entry: source-self-installed-runtime-fixtures

## Sources

- Static Truth: .loom/work-items/WI-1280.md
- Dynamic Truth: .loom/progress/WI-1280.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
