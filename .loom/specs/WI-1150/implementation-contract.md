# WI-1150 Implementation Contract

## Contract

- `author_stale_evidence_block_fixture` creates only repo-local fixture artifacts and intentionally stale evidence-map bindings.
- `require_stale_evidence_block_validation` must observe a blocking `suite evidence validate` result with `stale_evidence`, `evidence_map` taxonomy, and remediation text.
- `author_host_conflict_block_fixture` creates only repo-local Work Item, recovery, and task-carrier fixture artifacts with conflicting host mirror signals.
- `require_host_conflict_block_validation` must observe a blocking `suite carrier validate` result with `carrier_truth_conflict`, `task_carrier` taxonomy, recognized host signals, and remediation text.
- Source and installed self-fixture paths both consume the negative fixtures.
- Generated runtime copies must be produced by `tools/skills_surface.py generate`.

## Boundaries

- No production reconciliation behavior change.
- No GitHub mutation in the fixture code.
- No parent issue closeout.
