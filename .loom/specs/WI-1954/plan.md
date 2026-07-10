# Plan

## Suite Contract

- Suite path consumed: minimal
- Full suite artifacts not_applicable: rationale: WI-1954 uses focused runtime and fixture regression evidence for two bounded host friction fixes; full-only suite artifacts would not add decision value unless the batch expands beyond #1928/#1930. consumer boundary: suite validate, spec review, implementation review, PR metadata, hosted checks, PR gate, merge-ready, release #1955, and closeout consume this plan only with the current Work Item, progress, review, PR body, and hosted check evidence. recheck condition: expand the suite if the implementation starts changing #1933, #1935/v0.28.0 adoption behavior, release workflow mechanics, permissions, or external host actions.
- Consumes:
  - Spec locator: .loom/specs/WI-1954/spec.md
  - Acceptance ids / locators: A1-A5 in .loom/specs/WI-1954/spec.md#acceptance-criteria

## Implementation Steps

- Update `loom_flow.py` so active Work Item activation refreshes `fact_chain.mode`.
- Update suite validation command discovery to try repo-local CLI invocations first and global `loom` CLI JSON when available.
- Synchronize source/runtime copies and plugin payload metadata.
- Add focused CLI contract regressions for #1928 and #1930.
- Refresh `examples/new-project` demo bootstrap fixture after runtime changes.
- Bind PR #1967 metadata and Loom carriers to `WI-1954`.

## Validation

- A1 -> test evidence: `assert_work_item_activate_from_idle_syncs_fact_chain_mode`.
- A2 -> test evidence: existing suite validation consumption fixtures.
- A3 -> test evidence: `assert_build_consumes_global_suite_without_repo_local_tools`.
- A4 -> validation evidence: `py_compile_clean`, `tools/loom.py skills release-check --json`, and `make loom-demo-new-project-check`.
- A5 -> validation evidence: `loom pr metadata-preflight/readback`, hosted PR gate, and PR #1967 readback.

## Boundaries

- Do not add #1933 temporary hardcoding.
- Do not implement #1935 or v0.28.0 host adoption tax.
- Do not require downstream host repositories to add repo-local `tools/loom.py`.
- Do not skip pre-check hooks or hosted gates.
