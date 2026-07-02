# WI-1894 Implementation Contract

## Ownership

- Owns: workstation registry schema documentation, registry fixture catalog, focused CLI contract fixture validation, and WI-1894 Loom carriers.
- Does not own: `loom workstation` command implementation, real global registry writes, multi-repository upgrade orchestration, global runtime cache relocation, plugin payload, marketplace catalog, package version, or repository adoption behavior.

## Required Outputs

- `docs/adoption/workstation-registry-contract.md`
- `docs/evidence/fixtures/workstation-registry-fixtures.json`
- adoption README/taxonomy/global CLI contract links
- `tools/check_cli_contract.py` focused `workstation-registry` surface
- WI-1894 suite, evidence map, task carrier, work item, and progress entries

## Validation Contract

The focused test surface must validate:

- fixture schema version `loom-workstation-registry-fixtures/v1`
- registry schema version `loom-workstation-repositories/v1`
- registry authority `workstation`
- logical path `~/.loom/repositories.json`
- required entry fields: `id`, `path`, `path_state`, `remote`, `adoption`, `opt_in`, `last_seen_at`
- fixture coverage for `path_missing`, `remote_hash_drift`, `repo_id_conflict`, and `opted_out`
- absence of forbidden repository truth fields such as issue, PR, review, merge-ready, closeout, runtime log, and plugin payload fields

## Consumer Boundary

#1895 can consume the schema to implement register/list/unregister. #1896 can
consume the fixture classifications to implement fail-closed validation. Neither
consumer may treat registry entries as repository adoption success or closeout
truth without running repository-local validation.
