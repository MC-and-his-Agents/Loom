# WI-929 Spec

## Objective

Implement the CLI-first command layer for #893/#894/#895 so the phase can consume executable command semantics for host control, host adapters, and generated SKILLS surfaces.

## Acceptance

- `loom help --json` marks #929-#943 command names implemented.
- Host-control commands emit structured JSON and delegate existing harness readers where available.
- Host adapter commands distinguish full-repo/native discovery from adapter-managed plugin and single-skill paths.
- Skills commands read, check, package, and fail-closed around generated `skills/` mutation.
- Mutating host, skills, workspace, merge, and reconciliation paths require explicit apply/execute semantics or block with fallback.
- Contract checks cover representative positive and fail-closed fixtures.
