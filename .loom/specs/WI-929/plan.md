# WI-929 Plan

1. Move #893/#894/#895 command names from reserved to implemented in `tools/loom.py`.
2. Add thin JSON wrappers for workspace, issue, project, PR, merge, reconcile, host, and skills domains.
3. Delegate to existing `loom_flow.py`, `skills_surface.py`, `host_adapter_check.py`, `version_surface_check.py`, and installer shim evidence where appropriate.
4. Extend CLI contract checks with host-control, host, and skills command fixtures.
5. Update CLI control-plane docs and Work Item carriers.
6. Validate with focused CLI commands and full repository checks before PR creation.
