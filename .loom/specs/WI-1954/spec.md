# Spec

## Suite Contract

- Suite path: minimal
- Full suite artifacts not_applicable: rationale: WI-1954 is a bounded v0.27.1 runtime fix batch for two already-scoped host friction bugs, #1928 and #1930; it does not introduce a new product workflow, host adoption model, permission boundary, release mechanism, or external write surface beyond the required implementation PR and follow-on v0.27.1 release. consumer boundary: suite validate, spec review, implementation review, PR metadata, hosted checks, PR gate, merge-ready, release #1955, and closeout may consume this minimal suite as the path decision and acceptance contract while still requiring current-head review, fact-chain/status readback, local validation, hosted checks, release evidence, and issue closeout. recheck condition: require a fuller suite if scope expands into #1933 temporary label hardcoding, #1935/v0.28.0 host adoption tax, downstream repo-local `tools/loom.py` requirements, new release workflow behavior, permissions, or external host actions.

## Goal

Complete the v0.27.1 host friction implementation batch by fixing #1928 and #1930 without expanding into #1933, #1935, or v0.28.0 adoption work.

## Scope

- Fix #1928 so activating a real Work Item from idle refreshes `fact_chain.mode` to the active work-item mode.
- Fix #1930 so suite validation can consume global `loom` CLI JSON when a host repository has no repo-local `tools/loom.py`.
- Keep runtime copies, plugin payload metadata, and demo bootstrap fixtures synchronized.
- Keep #1933 temporary label hardcoding, #1935/v0.28.0 host adoption tax, and downstream repo-local shim requirements out of scope.

## Acceptance Criteria

- [x] A1: `work-item create/update --activate` from `no_active_item` records active fact-chain mode for the activated item.
- [x] A2: Build/readiness suite validation consumes repo-local CLI JSON when present.
- [x] A3: Build/readiness suite validation falls back to global `loom` CLI JSON when repo-local CLI is absent.
- [x] A4: Runtime source, generated copies, plugin payload metadata, and demo bootstrap fixture carriers remain synchronized.
- [x] A5: PR #1967 metadata identifies the v0.27.1 batch, covers #1928 and #1930, and excludes #1933/#1935.
