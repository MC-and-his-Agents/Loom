# WI-1233 Implementation Contract

- Suite path: minimal

## Allowed Changes

- `skills/shared/scripts/loom_flow.py` active workspace diagnostics and maintained runtime/generated copies.
- `skills/shared/scripts/loom_check.py` focused diagnostics fixture and maintained runtime/generated copies.
- `docs/methodology/harness/workspace-and-purity.md`.
- Scoped WI-1233 work item, progress, spec, plan, implementation contract, and status carrier.

## Required Invariants

- `stale_carrier` remains report-only for terminal recovery carriers.
- `shared_workspace_conflict` remains blocking for live same-workspace carriers without completed host truth.
- `carrier_closeout_required` only applies when host issue/PR readback proves complete/merged state while repo recovery remains non-terminal.
- `closeout_required` metadata/status bool semantics are unchanged.
- Remediation for host-complete carrier drift points to carrier closeout sync, not workspace retire.
