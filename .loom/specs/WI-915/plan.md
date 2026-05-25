# WI-915 Plan

1. Promote #890/#891 command names from reserved/delegated to implemented in the CLI matrix.
2. Add thin wrappers in `tools/loom.py` that preserve command names, JSON output, and fail-closed fallbacks while delegating to existing runtime readers.
3. Extend `tools/check_cli_contract.py` with #915-#923 command presence, representative positive reads, and fail-closed fixtures.
4. Update CLI command/control-plane docs to record the new command families and boundaries.
5. Run focused validation, record review carriers, open PR, and let CI/PR gate consume the Work Item chain.
