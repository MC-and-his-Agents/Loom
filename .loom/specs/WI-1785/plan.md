# WI-1785 Plan

## Phases

- P1: Read PR body machine metadata in the hosted merge gate workflow.
- P2: Infer `closeout` only when the machine carrier explicitly declares `surface: closeout`; otherwise keep `merge_ready`.
- P3: Pass the inferred surface to `tools/loom_flow.py pr-gate check`.
- P4: Validate closeout and merge_ready inference locally, run suite/fact-chain/shadow checks, open PR, consume hosted checks, merge, and close out #1785.
- P5: Update #1784 with the fixed main workflow and rerun its hosted gate.

## Scenario Mapping

- S1 -> P1, P2, P3, P4, P5
- S2 -> P1, P2, P3, P4
- S3 -> P1, P2, P4

## Acceptance Mapping

- A1 -> test evidence: local Python smoke parses a closeout metadata body and verifies `closeout`; hosted proof after merge: #1784 rerun passes.
- A2 -> test evidence: local Python smoke parses a merge_ready metadata body and verifies `merge_ready`.
- A3 -> test evidence: local Python smoke parses malformed body and verifies `merge_ready`.
- A4 -> test evidence: hosted check evidence on #1784 after #1785 merge.

## Validation

- `git diff --check`
- `python3 tools/py_compile_clean.py tools/loom.py`
- local Python smoke for workflow surface inference with closeout, merge_ready, and malformed metadata bodies
- Post-merge #1784 hosted `loom-pr-merge-gate` rerun after #1784 branch consumes this workflow fix.
- `python3 tools/loom.py fact-chain --target . --item WI-1785 --json`
- `python3 tools/loom.py suite validate --target . --item WI-1785 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1785 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1785 --json`
- `python3 tools/loom_flow.py shadow-parity --target . --surface all --blocking`

## Deferred

- A reusable CLI helper for PR metadata surface inference can go to #1774 backlog if the workflow-local parser proves insufficient.
- Supporting multiple simultaneous metadata surface blocks is out of scope unless a real PR requires it.
