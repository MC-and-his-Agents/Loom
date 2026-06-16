# WI-1236 Implementation Contract

## Ownership

- Branch: `work/1236-hotcp-regression-fixtures`
- Work Item: WI-1236 / GitHub issue #1236
- Write scope:
  - `tools/check_cli_contract.py`
  - `.loom/work-items/WI-1236.md`
  - `.loom/progress/WI-1236.md`
  - `.loom/specs/WI-1236/**`
  - `.loom/status/current.md`
  - `.loom/bootstrap/init-result.json`
  - `.loom/shadow/closeout-loom.json`
  - `.loom/shadow/merge-ready-loom.json`
- Non-goals: runtime/source behavior changes, generated runtime sync, docs/help/release updates, Round 10/11/deferred work, release/tag/npm actions, and shared schema/parser/failure vocabulary changes.

## Required Behavior

- The new fixture must start from a stale active carrier: host truth is issue closed/completed and PR merged, while progress/status/init-result still point to a non-terminal Work Item.
- The fixture must prove the fact-chain still points at the completed Work Item before carrier closeout sync.
- The fixture must prove `workspace retire` is local-only and does not mutate versioned progress/status/init-result carriers.
- The fixture must prove `repair plan/apply --issue <n>` remains the carrier closeout sync path after retire.
- The fixture must prove the repair path terminalizes to idle `no_active_item` fact-chain readback.
- The fixture must cover both root workspace naming and retained historical item naming.

## Validation Expectations

- Focused local validation must pass before review:
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/check_cli_contract.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`
- Suite and carrier validation must consume WI-1236 evidence.
- PR body metadata must bind Work Item, branch, and head SHA before hosted checks or merge gate.

## Rollback

- Revert the WI-1236 branch commits before merge if the fixture causes unrelated governance-closeout failures.
- Do not weaken repair/apply fail-closed behavior, workspace retire local-only semantics, or idle/no_active fact-chain behavior to make the fixture pass.
