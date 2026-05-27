# WI-1114 Spec

- Suite path: minimal
- Work Item: WI-1114

## Goal

Implement dry-run planning for `loom suite scaffold`.

## Scope

- Add `suite scaffold` to the implemented `loom help --json` command matrix.
- Route `loom suite scaffold --target <repo> --item <item> --json` through the shared CLI JSON envelope.
- Plan minimal suite artifacts only: `.loom/specs/<item>/spec.md` and `.loom/specs/<item>/plan.md`.
- Include planned writes, source templates, consumed locators, overwrite policy, `apply_required`, rollback note, and empty `created_locators`.
- Prove dry-run behavior leaves target files unchanged and emits `mutates: false`.
- Keep `--apply` fail-closed because write execution belongs to #1115.
- Keep `--suite full` fail-closed because full artifact generation belongs to #1116.

## Scenarios

### S1 Minimal Dry-Run Plans Writes

Given a target repository and Work Item id,
When `loom suite scaffold --json` runs without `--apply`,
Then it reports planned `spec.md` and `plan.md` locators, source template locators, and `mutates: false` without creating files.

### S2 Existing Files Are Preserved

Given a target where a planned artifact already exists,
When dry-run scaffold runs,
Then the planned action preserves the existing file and the overwrite policy reports no overwrite allowance.

### S3 Apply Is Reserved

Given a caller passes `--apply`,
When #1114 scaffold runs,
Then it fails closed, reports `mutates: false`, and creates no locators.

### S4 Full Suite Is Reserved

Given a caller requests `--suite full`,
When #1114 scaffold runs,
Then it fails closed to the minimal dry-run fallback until the full suite Work Item implements that path.

## Acceptance

- AC-1114-1: `loom help --json` includes `suite scaffold` as an implemented suite command.
- AC-1114-2: `loom suite scaffold --target . --item WI-1114 --json` emits `result: pass`, `mutates: false`, `apply_required: true`, planned minimal spec/plan writes, and empty `created_locators`.
- AC-1114-3: `tools/check_cli_contract.py` fails if dry-run scaffold mutates a fixture target.
- AC-1114-4: `tools/check_cli_contract.py` fails if `--apply` or `--suite full` stop failing closed before their later Work Items.
- AC-1114-5: No host truth, review truth, merge-ready truth, closeout truth, generated skills, spec-kit command names, or `.specify/` layout are introduced.
