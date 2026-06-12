# Current Status

## Derived Fact Chain View

- Item ID: WI-1451
- Goal: Harden Loom repository required-check governance so `.github/workflows/node-installer-pr.yml` always produces a stable PR check context, preserves full gate behavior on relevant path hits, preserves fast success on path misses, and records the explicit live-config/readback boundary for additional required contexts.
- Scope: Issue #1451 only: change `.github/workflows/node-installer-pr.yml` to run on every pull request; move the path filter into the job so the stable job/check name `node-installer-pr` always appears; preserve the existing full installer gate on relevant path hits; preserve fast success on path misses; record the 2026-06-13 live readback that `main` branch protection currently requires `py-compile`, `demo-bootstrap`, `repo-local-cli`, `loom-check`, and `loom-pr-merge-gate`, while repo rulesets read back as empty; evaluate `root-self-governance` as a required-context candidate and record the explicit boundary that live branch-protection or ruleset mutation is outside this worker scope. Do not mutate live branch protection/rulesets, loosen existing required checks, admin enforcement, strict status checks, PR merge protection, runner permissions, or implement product-level triggered-check aggregation. Do not process #1244/#1461/#1464/#1465, #1245/#1246/#1238, #1255, Round 9/10/11, Deferred roadmap, VERSION/tag/GitHub Release/npm publish/live actions, shared contract/schema/parser/failure vocabulary changes, or raw host merge.
- Execution Path: issue #1451 -> branch `work/1451-required-check-hardening` -> PR for workflow and WI-1451 carriers -> hosted readback proving stable `node-installer-pr` check context on the exact PR head -> scheduler-owned current-head review / PR gate / merge lane -> separately authorized live-config action only if the scheduler decides to add `node-installer-pr` and/or `root-self-governance` to host-enforced required contexts.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1451.md
- Review Entry: .loom/reviews/WI-1451.json
- Validation Entry: `git diff --check`; YAML syntax parse for `.github/workflows/node-installer-pr.yml`; targeted path-hit/path-miss smoke for the workflow diff detector; `python3 tools/loom.py suite inspect --target . --item WI-1451 --json`; `python3 tools/loom.py suite validate --target . --item WI-1451 --json`; `python3 .loom/bin/loom_init.py fact-chain --target .`; `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`; `python3 .loom/bin/loom_flow.py review read --target . --item WI-1451`; `python3 .loom/bin/loom_flow.py state-check --target . --item WI-1451`; PR metadata preflight/readback; hosted check readback for the exact PR head.
- Closing Condition: The WI-1451 PR proves the stable hosted context `node-installer-pr` on the current head, records the current live required-context baseline and `root-self-governance` candidate decision, passes local validation and hosted checks, and stops at `waiting-scheduler-gate` for scheduler-owned review/gate plus any separately authorized live-config readback or mutation.
- Current Checkpoint: merge
- Current Stop: WI-1451 is preparing the always-run `node-installer-pr` workflow and the matching Loom carriers on branch `work/1451-required-check-hardening`. The intended stable hosted check context is `node-installer-pr`; current live required contexts on `main` remain `py-compile`, `demo-bootstrap`, `repo-local-cli`, `loom-check`, and `loom-pr-merge-gate`, and repo rulesets currently read back as `[]`.
- Next Step: Finish local validation, create the WI-1451 PR, read back PR metadata and hosted checks for the exact head, then stop at `waiting-scheduler-gate` so the scheduler can own review/gate and any separately authorized live-config action for `node-installer-pr` and the `root-self-governance` candidate.
- Blockers: None.
- Latest Validation Summary: Startup readback on 2026-06-13 confirmed worksite `/Users/mc/.codex/worktrees/1451-required-check-hardening/Loom`, branch `work/1451-required-check-hardening`, clean status, base `origin/main` at `ecf7ab25d6c49fbac4b93854e6ca9a0cd47975ed`, issue #1451 OPEN, and no open PR already using this branch. Live host readback on 2026-06-13 showed `main` branch protection required contexts `py-compile`, `demo-bootstrap`, `repo-local-cli`, `loom-check`, and `loom-pr-merge-gate` with `strict=true`; `gh api repos/MC-and-his-Agents/Loom/rulesets --paginate` returned `[]`. The latest observed successful `node-installer-pr-gate` run on PR head `7b56175a5db1d17bea046d405b0531f1637969ff` exposed a generic check-run name `gate`, proving the current context is not stable enough to add as a safe required check.
- Recovery Boundary: WI-1451 only. Do not mutate live branch protection/rulesets, do not loosen existing governance, and do not expand into controlled-merge product semantics, triggered-check aggregation, #1244/#1461/#1464/#1465, #1245/#1246/#1238, #1255, Round 9/10/11, Deferred roadmap, VERSION/tag/GitHub Release/npm publish/live actions, shared contract/schema/parser/failure vocabulary changes, or raw host merge.
- Current Lane: self-governance-hardening

## Runtime Evidence

- Run Entry: Scheduler thread `019eb28d-ac3b-7623-8955-12542fa2e08d` delegated WI-1451 to worker `R8-WI-1451-worker-1` with gate owner `scheduler`.
- Logs Entry: Worker worksite is `/Users/mc/.codex/worktrees/1451-required-check-hardening/Loom` on branch `work/1451-required-check-hardening`; the worker owns workflow/carrier implementation, local validation, PR metadata, and hosted-check readback, then stops at `waiting-scheduler-gate`.
- Diagnostics Entry: `node-installer-pr-gate` currently emits the generic hosted check name `gate`; WI-1451 replaces that with a stable always-run context while keeping path-hit full validation and path-miss fast success inside the same job.
- Verification Entry: Current live host readback on 2026-06-13 shows `main` branch protection required contexts `py-compile`, `demo-bootstrap`, `repo-local-cli`, `loom-check`, and `loom-pr-merge-gate` with `strict=true`; repo rulesets are empty; `root-self-governance` is an always-run check candidate but not yet host-required.
- Lane Entry: self-governance-hardening

## Sources

- Static Truth: .loom/work-items/WI-1451.md
- Dynamic Truth: .loom/progress/WI-1451.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
