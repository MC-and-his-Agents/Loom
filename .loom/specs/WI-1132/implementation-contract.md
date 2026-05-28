# WI-1132 Implementation Contract

## Allowed Changes

- `tools/loom.py`
- `tools/check_cli_contract.py`
- `docs/methodology/harness/full-spec-suite-cli-surface.md`
- `docs/methodology/harness/cli-command-matrix.md`
- `.loom/progress/WI-1131.md`
- WI-1132 Loom carriers and status/shadow files

## Required Behavior

- `suite carrier inspect` and `suite carrier validate` remain read-only.
- Host mirror conflict classifications are derived validation findings only.
- Blocking conflicts use stable `carrier_truth_conflict` failure kind and `task_carrier` failed layer.
- Project Done, checklist checked, issue closed/open, and PR merged remain tracking or locator evidence only unless Work Item/recovery/review/merge-ready/closeout truth independently allows completion.

## Prohibited Behavior

- No Project or issue auto-sync.
- No pre-review/review/merge-ready integration.
- No closeout semantic changes.
- No host writes.
- No `/speckit.*` command names.
- No `.specify/` layout.
