# Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1716.md
- FR / parent locator: issue #1711
- Scope: Expose stale plugin payload refresh guidance from existing CLI freshness diagnostics.
- Suite path: minimal
- Current `HEAD`: fe14cd9c0a823b38dec24ded507a221d039abc4c before WI-1716 implementation commit
- PR locator: pending
- Host state locator: isolated Codex workstation fixture through `loom host doctor --host codex --scope user --json`

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1716/spec.md | present | authored for issue #1716 | Recheck before PR metadata and merge-ready. |
| `plan.md` | .loom/specs/WI-1716/plan.md | present | authored for issue #1716 | Recheck after validation changes. |
| task carrier | .loom/specs/WI-1716/task-carrier.md | present | issue #1716 / branch work/1716-plugin-refresh-guidance | Recheck issue and PR state before closeout. |
| review record | .loom/reviews/WI-1716.json | pending | review truth | Required before merge-ready. |
| merge-ready basis | PR metadata / hosted checks | pending | merge-ready truth | Required before merge. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py` | S1 S2 S3 | WI-1716 / plugin_payload_refresh_guidance | present | build / review / merge-ready / closeout | Re-run direct JSON checks after CLI output changes. |
| EV-002 | test_evidence | `tools/check_cli_contract.py` | A1 A2 A3 A4 | WI-1716 / adoption-host-metadata surface | present | build / review / merge-ready | Re-run `python3 tools/check_cli_contract.py --surface adoption-host-metadata`. |
| EV-003 | behavior_evidence | `docs/adoption/global-cli-user-plugin-contract.md` | S1 S2 | WI-1716 / documented host refresh boundary | present | build / review / closeout | Re-read docs after refresh guidance changes. |
| EV-004 | fresh_verification_input | `.loom/progress/WI-1716.md` | EV-001 EV-002 EV-003 | WI-1716 / latest validation summary | present | merge-ready / closeout / status | Refresh after final validation or head changes. |

## Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| Broad fixture catalog | deferred | WI-1716 covers focused guidance behavior only. | #1717 regression fixtures | Fixture matrix expands. | #1717 |
| Release execution | deferred | WI-1716 is guidance behavior only. | #1718 release closeout | Version bump or release action enters scope. | #1718 |
