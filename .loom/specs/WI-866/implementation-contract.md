# WI-866 Implementation Contract

## Write Scope

- `docs/methodology/harness/closeout-gate.md`
- `docs/methodology/harness/gate-chain.md`
- `docs/methodology/harness/host-action-contract.md`
- `src/skills/shared/references/harness/closeout-gate.md`
- `src/skills/shared/references/harness/gate-chain.md`
- `src/skills/shared/references/harness/host-action-contract.md`
- `src/skills/shared/scripts/loom_flow.py`
- `src/skills/shared/scripts/loom_check.py`
- Generated `skills/` runtime/reference copies
- `examples/new-project` embedded runtime/hash refresh
- WI-866 Loom work item, recovery, spec, and review carriers

## Guardrails

- `--skip-gate` may skip only explicit heavyweight local gate execution, not the required closeout contract backlink checks.
- Required host checks evidence proves PR head freshness only; it does not replace authored review, merge-ready truth, or reconciliation audit.
- Merge-ready evidence must be retained execution-attempt evidence for the same Work Item and PR head.
- Review evidence must be an allow decision for an implementation review and must bind to the current validation summary.
- Any unreadable or stale control-plane evidence must block instead of being treated as implicitly satisfied.
