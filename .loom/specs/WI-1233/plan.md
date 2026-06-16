# WI-1233 Plan

- Suite path consumed: minimal

## Steps

1. Add a scoped `carrier_closeout_required` active workspace diagnostic classification when GitHub issue/PR host truth is complete but recovery carrier checkpoint is non-terminal.
2. Preserve old `stale_carrier` and `shared_workspace_conflict` branches when host truth is unavailable, not terminal, or the local carrier is already terminal.
3. Add focused fixture coverage with fake GitHub readback for host-complete drift plus existing stale and live conflict assertions.
4. Update the workspace/purity diagnostics documentation and synchronize maintained runtime copies.
5. Run minimal static, compile, focused diagnostics, and applicable carrier/suite validation before PR metadata readback.

## Validation

- `git diff --check`
- Python compile for touched Python files.
- Focused retire workspace fixture through `tools/loom_check.py --profile source --source-surface retire-workspace .`
- Suite/carrier validation for WI-1233 where applicable.
