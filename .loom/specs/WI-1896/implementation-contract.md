# WI-1896 Implementation Contract

- Suite path: minimal

## Ownership

- Owns `loom workstation list` classification of stored registry entries whose path, remote, or repo id can no longer be trusted.
- Owns fail-closed repair guidance and mutation-planning eligibility for blocking registry classifications.
- Owns focused CLI contract coverage for missing path, remote hash drift, and duplicate id cases.

## Contract

- `path_missing` is blocking when `path_state != present` or the stored absolute path no longer exists.
- `remote_hash_drift` is blocking when the current `remote.origin.url` hash differs from the stored `remote.hash`.
- `repo_id_conflict` is blocking when the same workstation-local id is reused for different path/remote identities.
- Blocking classifications make `loom workstation list` return `block`, exclude affected entries from `eligible_for_plan`, and include repair guidance.
- `loom workstation register` refuses to write while the existing registry has blocking classifications; `unregister` remains available as a repair path.

## Non-Goals

- Do not implement `loom workstation upgrade --plan` or `--apply`.
- Do not mutate target repositories.
- Do not move runtime/cache artifacts to global storage in this Work Item.

## Validation Binding

- A1: `python3 tools/check_cli_contract.py --surface workstation-registry` covers missing path fail-closed behavior.
- A2: `python3 tools/check_cli_contract.py --surface workstation-registry` covers remote hash drift fail-closed behavior and register refusal while drift is present.
- A3: `python3 tools/check_cli_contract.py --surface workstation-registry` covers duplicate id fail-closed behavior.
- A4: `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py` and `git diff --check` cover syntax and diff hygiene.
