# Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1732.md`
- FR / parent locator: GitHub issue #1732
- Scope: tombstone legacy `@mc-and-his-agents/loom-installer` package.
- Suite path: minimal

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `packages/loom-installer/src/index.ts` | S1 | WI-1732 / tombstone result | present | build / review / merge-ready / closeout | Re-run package test after CLI result changes. |
| EV-002 | test_evidence | `packages/loom-installer/test/installer.test.ts` | A1 A2 | WI-1732 / fail-closed JSON output | present | build / review / merge-ready | Re-run `npm --prefix packages/loom-installer test`. |
| EV-003 | docs_check_evidence | `packages/loom-installer/README.md` | A4 S3 | WI-1732 / tombstone README | present | review / closeout | Re-run package docs check. |
| EV-004 | workflow_evidence | `.github/workflows/node-installer-pr.yml` | A3 S2 | WI-1732 / PR tombstone gate | present | hosted checks / merge-ready | Re-run installer sunset guard. |
| EV-005 | release_guard_evidence | `tools/check_release_surface.py` | A3 A5 | WI-1732 / installer sunset guard | present | release-surface / closeout | Re-run `python3 tools/check_release_surface.py --surface installer-sunset-guard`. |
| EV-006 | fresh_verification_input | `.loom/progress/WI-1732.md` | EV-001 EV-002 EV-003 EV-004 EV-005 | WI-1732 / latest validation summary | present | merge-ready / closeout / status | Refresh after final validation or head changes. |
