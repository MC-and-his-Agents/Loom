# WI-576 Implementation Contract

## Ownership

- `docs/methodology/harness/structured-event-evidence.md` owns the stable event evidence schema and evidence-only boundary.
- `docs/methodology/harness/status-surface-contract.md` owns optional status exposure rules for event evidence.
- `docs/methodology/harness/host-action-contract.md` owns the rule that host-backed tracker state remains evidence, not host/tracker truth.
- `docs/evidence/orchestration-conformance-profiles.md` owns orchestration profile expectations for fake agent and fake tracker fixtures.
- `src/skills/shared/scripts/loom_check.py` owns mechanical event validation and fake orchestration fixtures.

## Guardrails

- Do not let event evidence author recovery, issue, tracker, review, merge-ready, closeout, or scheduler truth.
- Do not call real models, real tools, real trackers, or host mutation APIs from fake fixtures.
- Do not let optional host tracker availability pollute core `orchestration-core` pass/fail.
