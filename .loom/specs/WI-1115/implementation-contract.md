# WI-1115 Implementation Contract

## Owned Files

- `tools/loom.py`
- `tools/check_cli_contract.py`
- `docs/methodology/harness/cli-command-matrix.md`
- `.loom/work-items/WI-1115.md`
- `.loom/progress/WI-1115.md`
- `.loom/status/current.md`
- `.loom/specs/WI-1115/spec.md`
- `.loom/specs/WI-1115/plan.md`
- `.loom/specs/WI-1115/implementation-contract.md`
- `.loom/reviews/WI-1115.spec.json`
- `.loom/reviews/WI-1115.json`
- `.loom/shadow/merge-ready-loom.json`
- `.loom/shadow/closeout-loom.json`

## Contract

- `suite scaffold` remains read-only by default and preserves the #1114 dry-run contract.
- `suite scaffold --apply` is implemented only for repo-local minimal suite artifacts.
- Apply creates missing `.loom/specs/<item>/spec.md` and `.loom/specs/<item>/plan.md` files from Loom scaffold templates.
- Apply preserves existing files and does not overwrite them.
- Apply reports actual `created_locators`, per-artifact write state, `apply: true`, and `apply_required: false`.
- Apply emits `mutates: true` only when at least one locator was created.
- Apply fails closed before writing when the item is not a single repo-local path segment or the artifact path contains symlinks or non-file artifact placeholders.
- `--suite full` remains fail-closed until the full-suite Work Item owns that surface.

## Non-Goals

- No full suite generation.
- No suite validate/analyze, evidence, consistency, or carrier commands.
- No host state mutation.
- No review, merge-ready, closeout, or Project truth mutation by the suite CLI.
- No generated skills mutation.
- No spec-kit command names or `.specify/` layout.
