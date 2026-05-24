# WI-898 Spec

## Behavior Contract

WI-898 freezes the CLI-first control-plane entry for #886 and the installed-state contract entry for #887.

Observable behavior:

- `python3 tools/loom.py help --json` emits `loom-cli-output/v1`, includes the #885 command matrix, and classifies each command as `implemented`, `delegated`, or `reserved`.
- `python3 tools/loom.py version --json` emits repository, skills, plugin, host adapter, runtime, and package version authority context.
- `python3 tools/loom.py installed-state show|validate|export --target <repo> --json` consumes only `loom-installed-state/v2` metadata and fails closed when metadata is missing, unreadable, invalid, or carries unknown version authority.
- Reserved #885 commands return structured `result=block` output instead of calling unrelated legacy wrappers.
- Legacy surface hints may be reported for diagnostics, but they do not satisfy installed-state validation.

## Boundaries

- CLI owns command semantics, JSON output, fail-closed behavior, and installed-state interpretation.
- SKILLS and plugins remain entry/discovery layers that call CLI or consume CLI JSON.
- `.loom/` remains repo execution fact storage and must not become global distribution truth.
- This Work Item does not implement #888+ detect/doctor/repair, install/upgrade, host, skills, scenario, workspace, PR, merge, or migration execution chains.

## Acceptance

- Command semantics and naming are documented under `docs/methodology/harness/`.
- `loom-installed-state/v2` schema and graph rules are documented under `docs/adoption/`.
- `tools/check_cli_contract.py` mechanically covers help/version JSON, missing metadata fail-closed, legacy hints, valid graph export, and mixed/unknown version metadata fail-closed.
- `make check` passes on the PR head.
