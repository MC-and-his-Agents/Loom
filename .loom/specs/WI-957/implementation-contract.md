# WI-957 Implementation Contract

## Write Scope

- `src/skills/shared/scripts/loom_flow.py` pre-review readiness/cost guard.
- `src/skills/shared/scripts/loom_check.py` fixture assertions for pre-review guard output.
- `src/skills/loom-pre-review/SKILL.md` and `src/skills/loom-pre-review/references/output-contract.md`.
- `tools/check_cli_contract.py` wrapper contract assertions.
- Generated `skills/` runtime copies produced from `src/skills`.
- WI-957 Loom carriers and evidence records.

## Exclusions

- No #1107 full spec suite CLI tree.
- No rewrite of frozen Work Item, review, merge-ready, closeout, or docs/source truth contracts.
- No parser/CLI/PR body/runtime evidence promotion to authored truth.
- No change to controlled merge, closeout, or review model policy.
