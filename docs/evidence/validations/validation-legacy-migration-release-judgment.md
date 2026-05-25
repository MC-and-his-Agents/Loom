# Validation: Legacy Migration And Release Judgment

## Scope

This record closes #897 evidence for #948, #949, #950, #951, and #952.

It validates the CLI-first legacy migration command surface against three real
repository shapes without mutating those repositories:

- WebEnvoy: `/Users/mc/dev/WebEnvoy`
- Syvert: `/Users/mc/dev/syvert`
- HotCP: `/Users/mc/dev/HotCP`

The mechanical fixture lives in
[`legacy-migration-validation-fixtures.json`](../fixtures/legacy-migration-validation-fixtures.json).

## Command Evidence

The validation command is:

```bash
python3 tools/check_cli_contract.py
```

The check materializes the three repository shapes in a temporary directory and
asserts the same CLI contract for each sample:

- `loom detect` returns `mixed-legacy`.
- `loom doctor` fails closed and falls back to `["loom repair plan"]`.
- `loom repair plan` is non-mutating and emits repair/classification actions.
- `loom upgrade-plan` is non-mutating and requires installed-state repair plus
  legacy surface classification.
- `loom verify` blocks because `doctor` blocks.

## Live Read-Only Sample

On 2026-05-25, direct read-only CLI detection of the local sample repositories
reported:

| Repository | Classification | Surfaces |
| --- | --- | --- |
| WebEnvoy | `mixed-legacy` | `.loom/bin`, `.loom/bootstrap/manifest.json`, `.loom/companion/manifest.json`, `.agents/skills` |
| Syvert | `mixed-legacy` | `.loom/bin`, `.loom/bootstrap/manifest.json`, `.loom/companion/manifest.json` |
| HotCP | `mixed-legacy` | `.loom/bin`, `.loom/bootstrap/manifest.json`, `.loom/companion/manifest.json`, `.agents/skills` |

The versioned fixture is the authoritative regression input because local sample
repositories can continue evolving independently.

## Release Judgment For #897

Conclusion: #897 is a no-publish validation batch.

Reason:

- #897 does not change the installer package authority line by itself.
- #897 does not make a root repository release decision by itself.
- All three legacy samples remain blocked until repo-owned migration applies
  `loom-installed-state/v2` and consumes repair/upgrade plans.
- #996 owns final release readiness, version surface, GitHub tag/release, and
  npm publish or no-publish judgment for the whole #885 CLI-first phase.

#897 is ready to be consumed by #996 when this record, the fixture, and
`docs/adoption/cli-first-legacy-migration-playbook.md` are merged with passing
CLI contract checks.
