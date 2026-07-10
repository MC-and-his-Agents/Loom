# WI-1895 Implementation Contract

## Ownership

- Owns: `loom workstation register/list/unregister --json`, global workstation registry read/write helpers, command matrix/help entries, focused isolated HOME contract coverage, registry CLI docs, and WI-1895 Loom carriers.
- Does not own: `loom workstation upgrade --plan`, live registry drift validation, global runtime cache relocation, Codex marketplace/plugin refresh, package release, or target repository adoption mutation.

## Required Outputs

- `tools/loom.py` workstation command entries, dispatch, and handlers.
- `tools/check_cli_contract.py` focused CLI coverage in the `workstation-registry` surface.
- `docs/adoption/workstation-registry-contract.md` CLI surface notes.
- WI-1895 suite, evidence map, task carrier, work item, and progress entries.

## Validation Contract

The focused test surface must validate:

- `workstation list` is read-only for a fresh isolated HOME.
- `workstation register --target <repo> --json` writes `~/.loom/repositories.json`.
- The persisted registry uses `loom-workstation-repositories/v1`.
- Registered entries include absolute path, stable id, canonical remote URL, remote hash, adoption snapshot, opt-in state, and last-seen timestamp.
- Target repository does not receive runtime, plugin, skills, or host payload writes.
- `workstation unregister --keep-entry` marks an entry opted out/list-only.
- `workstation unregister --id <repo-id>` removes the entry.

## Consumer Boundary

#1896 can consume this CLI surface to add live fail-closed validation for missing
paths, remote hash drift, and repo id conflicts. FR #1902 can consume the
registry for workstation upgrade planning, but every candidate still needs
repository-local adoption validation before mutation.
