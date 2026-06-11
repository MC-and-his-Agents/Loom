# Skills Surface Split Closeout Evidence

This record is the #1400 docs/evidence convergence locator for parent #1261 and umbrella #1255. It consumes the merged #1397, #1398, and #1399 validation surfaces without changing generated skill packaging semantics.

## Scope

- Work Item: #1400
- Parent: #1261
- Umbrella: #1255
- Source surfaces:
  - #1397: `docs-reference-sync`, `generated-tree-drift`
  - #1398: `package-metadata`, `cache-artifacts`
  - #1399: `launcher-smoke`

## Named Skills Validation Surfaces

| Surface | Targeted command | Failure name | Evidence locator | Consumed from |
| --- | --- | --- | --- | --- |
| `docs-reference-sync` | `python3 tools/skills_surface.py check --surface docs-reference-sync` | `skills_docs_reference_sync_drift` | `tools/skills_surface.py:DOC_REFERENCE_SYNC` | #1397 / PR #1419 |
| `generated-tree-drift` | `python3 tools/skills_surface.py check --surface generated-tree-drift` | `skills_generated_tree_drift` | `src/skills -> skills` | #1397 / PR #1419 |
| `package-metadata` | `python3 tools/skills_surface.py check --surface package-metadata` | `skills_package_metadata_invalid` | `skills/*/loom-package.json; skills/*/contract.json; skills/*/.loom-runtime` | #1398 / PR #1424 |
| `cache-artifacts` | `python3 tools/skills_surface.py check --surface cache-artifacts` | `skills_cache_artifacts_present` | `skills/**/__pycache__; skills/**/*.py[cod]` | #1398 / PR #1424 |
| `launcher-smoke` | `python3 tools/skills_surface.py check --surface launcher-smoke [--skill <id>]` | `skills_launcher_smoke_failed` | `skills/<skill-id>/loom-package.json; skills/<skill-id>/<launcher>` | #1399 / PR #1432 |

## Aggregate Contract

The compatible aggregate script command remains:

```bash
python3 tools/skills_surface.py check
```

The CLI aggregate entrypoint remains:

```bash
python3 tools/loom.py skills check --target . --json
```

`make skills-check` also consumes the aggregate script command. The targeted `make skills-*-check` aliases are diagnostic and evidence locators for triage, review, PR metadata, and closeout; they do not create new package modes or release behavior.

## Consumption Boundary

#1261 can consume this record as the named surface inventory and closeout basis for generated SKILLS validation. #1255 can consume #1261 without treating the generated SKILLS validation as a black-box bucket, provided the consuming gate also has current-head aggregate validation and PR metadata/readback for the active PR.

This evidence does not close #1261 or #1255 by itself. It does not authorize release execution, generated skill content changes, new packaging semantics, hosted workflow changes, guardian/formal review, controlled merge, or parent closeout.
