# WI-1114 Implementation Contract

## Owned Files

- `tools/loom.py`
- `tools/check_cli_contract.py`
- `docs/methodology/harness/cli-command-matrix.md`
- `.loom/work-items/WI-1114.md`
- `.loom/progress/WI-1114.md`
- `.loom/status/current.md`
- `.loom/specs/WI-1114/spec.md`
- `.loom/specs/WI-1114/plan.md`
- `.loom/specs/WI-1114/implementation-contract.md`
- `.loom/reviews/WI-1114.spec.json`
- `.loom/reviews/WI-1114.json`
- `.loom/shadow/merge-ready-loom.json`
- `.loom/shadow/closeout-loom.json`

## Contract

- `suite scaffold` is an implemented suite command only for dry-run planning in #1114.
- Dry-run scaffold plans the minimal suite artifacts `spec.md` and `plan.md` below `.loom/specs/<item>/`.
- Dry-run scaffold reports source templates, consumed locators, overwrite policy, rollback note, `apply_required: true`, `apply: false`, and empty `created_locators`.
- Dry-run scaffold emits `mutates: false` and does not create, edit, or delete target files.
- `--apply` fails closed until #1115 owns explicit writes.
- `--suite full` fails closed until #1116 owns full artifact planning and generation.

## Non-Goals

- No scaffold writes.
- No full suite generation.
- No suite validate/analyze, evidence, consistency, or carrier commands.
- No host state mutation.
- No review, merge-ready, closeout, or Project truth mutation by the suite CLI.
- No generated skills mutation.
- No spec-kit command names or `.specify/` layout.
