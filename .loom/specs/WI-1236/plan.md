# WI-1236 Plan

## Implementation Steps

1. Extend the governance-closeout CLI contract fixture in `tools/check_cli_contract.py`.
2. Add a HotCP-style stale active carrier fixture that starts with host-complete GitHub truth and non-terminal progress/status carriers.
3. Assert `workspace retire` remains local-only and leaves versioned carrier files unchanged.
4. Assert `repair plan/apply --issue <n>` remains the carrier closeout sync path after retire and produces idle `no_active_item` fact-chain readback.
5. Add retained historical item naming coverage without changing lookup/runtime semantics.
6. Record WI-1236 carriers, evidence map, and validation summaries for review/merge-ready consumption.

## Validation

- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1236 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1236 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1236 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py fact-chain --target . --json`
- PR metadata preflight/readback, hosted checks, pr-gate, controlled merge, and post-merge closeout readback before closing #1236.

## Dependencies

- Hard dependency consumed: #1235 stable behavior on `origin/main` at merge commit `703feadf46162d7937ede040a098a013093b2c39`.
- Follow-up dependency: #1237 final docs/help/release surface must consume this fixture behavior after #1236 merges.
- Convergence dependency: #1296 release/no-release closeout starts only after #1236 and #1237 merge.

## Scope Guard

- Do not touch #1237 docs/help, #1296 release/no-release, parent #1228 closeout, Round 10/11, Deferred roadmap, release/tag/npm/GitHub Release, workflow/runtime behavior, shared schema/parser/failure vocabulary, or unrelated refactors.
