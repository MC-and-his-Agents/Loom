# WI-1253 Plan

## Implementation Steps

- Add explicit `daily-execution-cli-fast` and `daily-execution-cli-full` source-surface selectors to `loom_check`.
- Keep `merge-gate`, `source-self-fixture`, and default `full` source checks consuming the full daily-execution-cli bucket.
- Add Makefile aliases for the fast local smoke and full daily CLI bucket replay.
- Add mechanical self-check anchors so scripts, Makefile, and docs stay aligned.
- Document the distinction between fast local proof, full bucket proof, hosted checks, merge-ready, release/no-release, and scheduler-owned gates.
- Synchronize generated skills runtime copies from `src/skills`.
- Record WI-1253 carriers without authoring scheduler-owned semantic review approval.

## Validation

- `git diff --check`
- `make daily-execution-cli-fast`
- `make daily-execution-cli-full`
- `python3 tools/skills_surface.py check`
- `python3 tools/check_cli_contract.py`
- `python3 tools/loom.py suite inspect --target . --item WI-1253 --json`
- `python3 tools/loom.py suite validate --target . --item WI-1253 --json`
- PR metadata preflight/readback on the current PR head
- Hosted checks readback after push

## Ownership Constraints

- WI-1253 owns only daily-execution-cli fast/full entrypoints, docs alignment, mechanical checks, generated runtime sync, WI-1253 carriers, PR metadata, and validation evidence.
- Scheduler gate cleanup may terminalize `.loom/progress/WI-1251.md` only to consume the already merged and closed #1251 state and prevent stale active workspace binding; it does not reopen #1251 ownership or alter #1251 implementation behavior.
- WI-1253 does not start #1254 or #1247.
- WI-1253 does not weaken full merge-ready/release coverage or fail-closed behavior.
- WI-1253 does not run scheduler-owned semantic review, PR gate, controlled merge, release, no-release closeout, or parent closeout.
