# WI-1129 Spec

- Suite path: minimal

- Full suite artifacts not_applicable: rationale: #1129 is a narrow CLI slice for evidence-map scaffold dry-run/apply and only needs spec, plan, implementation contract, evidence-map, docs, and CLI contract fixtures; consumer boundary: carrier validation, merge-ready integration, closeout reconciliation, consistency-analysis, E2E governance, and doctor/verify integration remain owned by later Work Items under #1126/#1136/#1145; recheck condition: this change expands beyond evidence-map scaffold generation or a later consumer requires the full suite path.

## Goal

Users can generate an evidence-map scaffold safely without mutating files by default and without treating generated placeholders as present evidence.

## Key Scenarios

### Scenario S1

Given a Work Item without an evidence-map
When `loom suite evidence scaffold` runs without `--apply`
Then the CLI reports the planned evidence-map write, source template, consumed suite locators, overwrite policy, rollback note, and seed row freshness without mutating the repository.

### Scenario S2

Given a Work Item without an evidence-map
When `loom suite evidence scaffold --apply` runs
Then the CLI creates only `.loom/specs/<item>/evidence-map.md`, preserves existing files, and reports created locators.

### Scenario S3

Given generated scaffold rows or unsafe target paths
When evidence validation or scaffold apply runs
Then generated rows remain `missing`, validation does not pass merely because the scaffold exists, and traversal, symlink, or non-file targets fail closed before writes.

## Acceptance Criteria

- [ ] A1: `loom help --json` declares `suite evidence scaffold` as an implemented suite command.
- [ ] A2: Dry-run emits `mutates: false`, plans only `.loom/specs/<item>/evidence-map.md`, reports source template and consumed suite locators, and creates no files.
- [ ] A3: `--apply` creates the evidence-map scaffold with preserve-existing overwrite policy and reports created locators.
- [ ] A4: Scaffold seed rows start with `missing` freshness and do not satisfy `suite evidence validate`.
- [ ] A5: Unsafe item segments, symlink paths, and non-file artifact targets fail closed before writes.
