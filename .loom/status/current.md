# Current Status

## Derived Fact Chain View

- Item ID: WI-1296
- Goal: Release idle closeout sync support as Loom CLI v0.14.1 and bind post-merge release evidence back into Round 9 closeout.
- Scope: Issue #1296 only: bump Loom CLI release surfaces from v0.14.0 to v0.14.1, verify the target tag/release/npm version is unoccupied before merge, run release/version/package/CLI/skills validation, let the existing `loom-cli-release` workflow publish from main after merge, then read back the workflow run, tag, GitHub Release, npm package, installed/global CLI smoke, and terminal carrier closeout evidence. Do not implement new runtime behavior, alter release workflow semantics, change installer legacy release surfaces, close parent #1228 before #1296 is closed/completed, or touch Round 10/11/deferred/unrelated files.
- Execution Path: issue #1296 -> branch `work/1296-release-closeout` -> version surface bump and release evidence carriers -> local release validation -> PR metadata/readback -> hosted checks and release-judgment -> controlled merge -> main-push release workflow readback -> tag/GitHub Release/npm/global smoke readback -> terminal carrier closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1296.md
- Review Entry: .loom/reviews/WI-1296.json
- Validation Entry: release/tag/npm preflight; `git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/version_surface_check.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_release_surface.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py skills release-check --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`; suite validate/evidence/carrier validate for WI-1296; fact-chain/shadow; PR metadata, hosted checks, release-judgment, controlled merge, and post-merge release readback.
- Closing Condition: PR for #1296 is merged from branch `work/1296-release-closeout` with head/body/carrier/review/shadow aligned; `loom-cli-release` main-push run for the merge commit succeeds; `v0.14.1` tag, GitHub Release, npm `@mc-and-his-agents/loom@0.14.1`, and installed/global CLI smoke are read back; `.loom/**` terminal closeout carriers consume that evidence; issue #1296 is CLOSED/COMPLETED.
- Current Checkpoint: build
- Current Stop: Release-prep head `737f244ed33982a86345f121a5bb7369b3bc5463` has version surfaces prepared, spec review recorded, the task-carrier release evidence locator repaired to EV-003, local suite/fact-chain/shadow/metadata preflight passed, and `flow review` now blocks only on the not-yet-recorded implementation review artifact.
- Next Step: Record implementation review bound to the current release-prep head, commit and push, create/update PR metadata, run PR metadata preflight and PR gate, wait for hosted checks and release-judgment, merge, then consume main-push release evidence.
- Blockers: None
- Latest Validation Summary: 2026-06-16T16:39Z current-head review preflight passed at `737f244ed33982a86345f121a5bb7369b3bc5463`: v0.14.1 remote tag absent; `gh release view v0.14.1` release not found; npm `@mc-and-his-agents/loom@0.14.1` E404; `git diff --check` pass; fact-chain pass; shadow-parity pass; version surface pass; release surface pass; npm package check pass for version 0.14.1; skills surface pass; `loom.py skills release-check --json` pass; suite inspect/validate/evidence validate/carrier validate pass for WI-1296 after task-carrier locator repair; `tools/check_cli_contract.py` pass in 397.50s; `flow spec-review` pass; PR metadata preflight pass for local body/payload fixture; `flow review` pass through runtime/fact-chain/state/build/spec-review/suite/metadata and blocks only on missing `.loom/reviews/WI-1296.json`, which is the next artifact to record.
- Recovery Boundary: WI-1296/#1296 release closeout only. Consume #1235 closeout merge 703feadf46162d7937ede040a098a013093b2c39, #1236 closeout merge 47083d932490b76a49f97d9a0cb307134582282b, #1237 implementation merge 864e12ace9090ba38cf55d6456726d7d291d5aae, and #1237 closeout merge a840bfa2dab65fa46c254d1eae7f6069afcd8b84. Do not close parent #1228 or milestone until #1296 is closed/completed; do not change release workflow semantics, installer legacy release line, runtime/schema/parser/failure vocabulary, Round 10/11, Deferred roadmap, or unrelated files.
- Current Lane: round-9-wi-10-release-closeout

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: not_applicable
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1296.md
- Dynamic Truth: .loom/progress/WI-1296.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
