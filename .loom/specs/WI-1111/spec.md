# WI-1111 Spec

- Suite path: minimal
- Work Item: WI-1111

## Goal

Expose the implemented read-only `loom suite inspect` command through Loom's declared CLI surface.

## Scope

- Add `suite inspect` to `loom help --json`.
- Keep `suite inspect` classified as `domain: suite`, `status: implemented`, and JSON-capable.
- Extend CLI contract checks so the declared matrix cannot drift from the implemented command.
- Update the human command matrix so only `suite inspect` leaves planned status.

## Scenarios

### S1 Help JSON Declares Command

Given the repository CLI supports `loom suite inspect`,
When `loom help --json` runs,
Then `suite inspect` appears in the command matrix as an implemented suite command.

### S2 CLI Contract Guards Declaration

Given the CLI contract check runs,
When it validates required commands,
Then it requires `suite inspect` and verifies its implemented suite-domain declaration.

### S3 Existing Inspect Behavior Remains Stable

Given unknown, minimal, full, and missing required artifact suite fixtures,
When `tools/check_cli_contract.py` runs,
Then the existing read-only suite inspect payload behavior remains unchanged.

## Acceptance

- AC-1111-1: `loom help --json` includes exactly the existing `suite inspect` command, not additional suite subcommands.
- AC-1111-2: `suite inspect` remains read-only and uses the shared CLI JSON envelope.
- AC-1111-3: command matrix docs distinguish implemented `suite inspect` from still-planned suite commands.
