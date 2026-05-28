# WI-1138 Implementation Contract

## Consumed Contracts

- `docs/methodology/harness/full-spec-suite-cli-surface.md`
- `docs/methodology/templates/spec-suite.md`
- `docs/adoption/loom-installed-state-v2.md`
- `docs/methodology/harness/cli-command-matrix.md`

## Required Behavior

- `loom verify` must keep consuming `doctor` before suite validation.
- `loom verify` must run suite validation only when `--item` or installed-state/profile requirements explicitly require it.
- Declared suite command support must remain diagnostic-only and must not require validation by itself.
- Required suite validation must be read-only and consume `suite_validate_payload`.
- Required suite validation failure must make verify fail closed with structured suite validation evidence.

## Forbidden Behavior

- No universal suite validation requirement.
- No `suite evidence validate`, `suite carrier validate`, or consistency analyzer execution from verify.
- No host writes or mutating repair/install behavior.
- No `/speckit.*` command names or `.specify/` layout.
- No CLI output replacing Work Item, review, merge-ready, closeout, docs, or source truth.
