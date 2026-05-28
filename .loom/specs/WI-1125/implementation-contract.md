# WI-1125 Implementation Contract

## Ownership

- `src/skills/shared/scripts/loom_flow.py`: spec-review flow/gate and spec review record allow consume suite validation results.
- `src/skills/shared/scripts/loom_check.py`: installed-skill regression for incomplete formal suite blocking spec-review approval.
- `skills/`: generated install/package runtime surface from `src/skills`.
- `.loom/bin/`: bootstrapped runtime mirror for repository self-governance validation.
- `.loom/bootstrap/manifest.json`: runtime hash updates for changed bootstrapped files.
- `docs/methodology/harness/full-spec-suite-cli-surface.md`: #1125 status and integration behavior.
- `docs/methodology/harness/cli-command-matrix.md`: command matrix wording for suite validate/spec-review consumption.

## Non-goals

- Do not implement #1126 evidence, carrier, or merge-ready validation.
- Do not change implementation review semantics beyond the existing dependency on a passing spec review gate.
- Do not add CLI writes, host writes, merge-ready writes, closeout writes, `/speckit.*`, or `.specify/` surfaces.
