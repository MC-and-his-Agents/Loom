# WI-1116 Implementation Contract

## Owned Files

- `tools/loom.py`
- `tools/check_cli_contract.py`
- `docs/methodology/harness/cli-command-matrix.md`
- `.loom/work-items/WI-1116.md`
- `.loom/progress/WI-1116.md`
- `.loom/status/current.md`
- `.loom/specs/WI-1116/spec.md`
- `.loom/specs/WI-1116/plan.md`
- `.loom/specs/WI-1116/implementation-contract.md`
- `.loom/reviews/WI-1116.spec.json`
- `.loom/reviews/WI-1116.json`
- `.loom/shadow/merge-ready-loom.json`
- `.loom/shadow/closeout-loom.json`

## Contract

- `suite scaffold` remains read-only by default.
- Minimal suite dry-run and apply behavior remains compatible with #1114 and #1115.
- `suite scaffold --suite full` plans the six standard full suite artifacts.
- `suite scaffold --suite full --apply` creates only missing full suite scaffold artifacts under `.loom/specs/<item>/`.
- Full suite artifacts are `suite-index.md`, `spec.md`, `plan.md`, `research.md`, `contracts.md`, and `readiness-checklist.md`.
- `suite-index.md`, `spec.md`, and `plan.md` are required artifacts.
- `research.md`, `contracts.md`, and `readiness-checklist.md` are conditional artifacts; scaffold generation may create their templates, but later validation decides whether their authored content is applicable.
- Apply preserves existing files and does not overwrite them.
- Apply reports actual `created_locators`, per-artifact write state, `apply: true`, and `apply_required: false`.
- Apply emits `mutates: true` only when at least one locator was created.
- Apply fails closed before writing when the item is not a single repo-local path segment or the artifact path contains symlinks or non-file artifact placeholders.

## Non-Goals

- No authored final spec, plan, research, contract, or readiness content.
- No evidence-map, consistency-analysis, execution breakdown, or task-carrier generation.
- No suite validate/analyze, evidence, consistency, or carrier subcommands.
- No host state mutation.
- No review, merge-ready, closeout, or Project truth mutation by the suite CLI.
- No generated skills mutation.
- No spec-kit command names or `.specify/` layout.
