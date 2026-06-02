# WI-1196 Spec

- Suite path: minimal

## Scenarios

- Scenario S1: `loom host verify --host codex --mode plugin` reports target repository payload verification and does not imply Codex Desktop workstation registration.
- Scenario S2: `loom host register --host codex --source ./plugins/loom --scope user` reports and, with `--apply`, writes user-level workstation registration state.
- Scenario S3: `loom doctor`, `loom repair plan`, and `loom upgrade-plan` surface a missing workstation registration when the target repository payload is current.

## Acceptance Criteria

- AC-1: CLI JSON separates target repository payload state from developer workstation registration state.
- AC-2: README and adoption docs explain the second-machine Codex workflow.
- AC-3: Regression coverage proves a HotCP-style repo-current/user-plugin-missing state.

- Full suite artifacts not_applicable: rationale: #1196 is governed by the GitHub issue tree and this minimal Work Item suite; the current implementation is a bounded CLI/docs/test change and does not need research, contracts, readiness-checklist, consistency-analysis, execution-breakdown, or task-carrier artifacts. consumer boundary: review, merge-ready, repair/upgrade planning, and closeout consume #1196-#1203 issue acceptance, `.loom/work-items/WI-1196.md`, `.loom/progress/WI-1196.md`, this minimal spec/plan, validation output, and PR evidence. recheck condition: if #1196 expands into product behavior beyond the repo payload/workstation registration split, introduces external data/security risk, or changes command naming semantics outside the frozen issue contract, author a full suite before review.
