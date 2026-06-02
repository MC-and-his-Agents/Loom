# WI-1196 Implementation Contract

## Ownership

- Owns #1196-#1203 implementation for separating target repository Loom payload install state from Codex Desktop workstation registration state.
- Owns CLI behavior in `tools/loom.py` for `host verify`, `doctor`, `host register`, `repair plan`, and `upgrade-plan`.
- Owns regression coverage in `tools/check_cli_contract.py` and release-surface checks in `tools/check_release_surface.py`.
- Owns adoption documentation in `README.md`, `docs/adoption/codex-install.md`, `docs/adoption/unified-install-experience.md`, and `docs/adoption/host-adapter-matrix.md`.
- Does not own unrelated Loom carrier cleanup, deprecated npm installer revival, Codex Desktop private state, current-session plugin hot reload claims, or closeout beyond #1196-#1203.

## Guardrails

- `loom host install` and `loom host verify` describe target repository payload state only.
- Codex Desktop workstation registration is a separate user-level state with explicit `loom host register --host codex` dry-run/apply behavior.
- Workstation registration state must not be persisted as target repository truth.
- Repair and upgrade plans may recommend workstation registration when target payload verifies but workstation state is missing.
- Documentation must not make `@mc-and-his-agents/loom-installer` the primary install path.
- Documentation must not claim this session can hot-load newly installed Codex plugins.

## Required Local Validation

- `git diff --check`
- `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `python3 tools/check_cli_contract.py`
- `python3 tools/check_release_surface.py`
- `make loom-check`
- `loom doctor --target <fixture> --json`
- `loom host verify --host codex --mode plugin --target <fixture> --json`
- `loom host register --host codex --source <fixture>/plugins/loom --scope user --dry-run --json` under isolated `HOME`/`CODEX_HOME`
- `loom host register --host codex --source <fixture>/plugins/loom --scope user --apply --json` under isolated `HOME`/`CODEX_HOME`
- docs link check
- PR/CI status and target branch validation before closeout
