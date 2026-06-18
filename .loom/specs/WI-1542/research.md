# Research

- Finding: milestone/12 lanes repeatedly hit late blockers when host-complete Work Items still had non-terminal repo-local carriers or stale shadow evidence.
- Finding: existing `active_workspace_diagnostics()` and `purity_report_from_context()` already identify shared workspace conflicts, stale terminal carriers, and host-complete carrier residue; the startup audit should consume them instead of creating a duplicate schema.
- Decision: expose a read-only `workspace audit` facade backed by runtime `work-item-audit` so operators can run one pre-start command before entering a lane.
- Decision: keep classifier names aligned with the #1513 vocabulary by mapping closeout residue to `carrier_refresh_needed` and shadow drift to `shadow_stale`.
- Decision: keep nonblocking terminal stale carriers compact to avoid overwhelming CLI readback while still preserving diagnostic evidence.
- Source: GitHub issue #1542, PR #1568 hosted failure classification on 2026-06-18, and `test/work_item_audit_test.py`.
