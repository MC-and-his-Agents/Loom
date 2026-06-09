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
- Current Checkpoint: closed_out
- Current Stop: WI-1280 is closed out: PR #1382 merged into `main` at 2026-06-09T08:28:35Z with merge commit `46cfa2011a80cf3b529c2c279eb5c3055bff161e`; issue #1280 closed at 2026-06-09T08:28:37Z; closeout PR #1384 merged into `main` at 2026-06-09T09:04:15Z with merge commit `8346be4ac1fbaa829e6c6f7d3f73280066ed3b78`; repo carrier closeout is synchronized to terminal checkpoint.
- Next Step: Round 6 scheduler can refresh `origin/main` after this carrier repair merges and reassess PR #1385 purity/gate inputs; keep #1258 parent closeout dependent on all Round 5 terminal carriers and parent closeout evidence.
- Blockers: None
- Latest Validation Summary: 2026-06-09 carrier repair validation on branch `work/1280-carrier-closeout-repair`: `python3 .loom/bin/loom_flow.py recovery writeback --target . --item WI-1280 --current-checkpoint closed_out ...` passed and resynchronized `.loom/status/current.md`; `python3 .loom/bin/loom_flow.py carrier closeout-sync --target . --item WI-1280 --apply ...` passed and refreshed terminal metadata; `python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1280 --write` refreshed `.loom/shadow/merge-ready-loom.json` and `.loom/shadow/closeout-loom.json` for the updated status surface; `python3 .loom/bin/loom_init.py fact-chain --target .` passed with derived status fresh; `python3 .loom/bin/loom_flow.py purity-check --target . --item WI-1280` passed with checkpoint `closed_out` and no active workspace conflict; `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking` passed after shadow refresh; `git diff --check` passed. Scope is limited to WI-1280 carrier/status/shadow closeout repair; no implementation, workflow, release, Round 6, or #1258 parent closeout changes.
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
