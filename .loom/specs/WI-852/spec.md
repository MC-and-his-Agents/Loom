# WI-852 Spec

## Outcome

`loom_status` and `flow merge-ready` consume Governance Lint / Operating Lint evidence as derived evidence before host merge, so stale or blocking governance failures are visible without running an expensive semantic review or creating a second authored truth source.

## Acceptance

- `loom_status` emits a top-level `governance_lint` object using `loom-governance-lint-status/v1` with `surface=status`.
- `flow merge-ready` emits a top-level `governance_lint` object using `loom-governance-lint-status/v1` with `surface=merge_ready`.
- `flow merge-ready` includes a deterministic `governance-lint` step in the merge-ready step list.
- Blocking lint evidence enters `missing_inputs` and can block the corresponding surface even when other checkpoint fallback signals are present.
- Advisory lint evidence remains advisory and does not change the verdict.
- Status and merge-ready consume the stable lint evidence envelope; neither surface writes a second lint verdict or replaces authored review records.

## Non Goals

- Do not implement a standalone `loom lint` CLI.
- Do not hardcode repo-specific lint rules into Loom core.
- Do not change review approval, PR gate, controlled merge, or closeout authority.
- Do not use raw review output, CI status, PR body, shadow evidence, or lint result as authored review truth.
