# WI-1736 Implementation Contract

## Scope

- Runtime owner: `src/skills/shared/scripts/loom_flow.py`.
- Generated mirrors: `skills/shared/scripts/loom_flow.py`, `plugins/loom/skills/shared/scripts/loom_flow.py`, `examples/new-project/.loom/bin/loom_flow.py`.
- Package metadata: `plugins/loom/.codex-plugin/plugin.json` payload hash only.
- Test evidence: `test/work_item_audit_test.py` and `tools/check_cli_contract.py --surface closeout-wrapper`.

## Required Behavior

- Apply/write mode must recompute carrier refresh actions after files are written.
- Output must expose fixed entries separately from remaining refresh entries.
- Dry-run mode must not mutate files and must keep reporting pre-apply refresh-needed entries.
- The command must remain compatible with existing carrier refresh JSON consumers.

## Non-Goals

- No `loom ship` orchestration.
- No review stale classification.
- No validation profile selection.
- No closeout policy change.
- No release publish or version bump.
