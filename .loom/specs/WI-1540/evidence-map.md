# WI-1540 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | host_terminal_evidence | GitHub issue #1538; PR #1537 | `.loom/specs/WI-1540/spec.md` S1 | WI-1538 terminal closeout | current | closeout sync / downstream purity | Re-read issue #1538 and PR #1537 if terminal facts drift. |
| EV-002 | carrier_sync_evidence | `.loom/progress/WI-1538.md` | `.loom/specs/WI-1540/spec.md` S1 S3 | WI-1540 / WI-1538 terminal checkpoint | present | purity checks and downstream Work Items | Re-read WI-1538 progress if purity reports active carrier drift. |
| EV-003 | fact_chain_evidence | `.loom/work-items/WI-1540.md`; `.loom/progress/WI-1540.md`; `.loom/status/current.md` | `.loom/specs/WI-1540/spec.md` S2 | WI-1540 active carrier chain | current | review / PR gate | Re-run fact-chain after final status/shadow refresh. |
| EV-004 | pr_metadata_evidence | PR #1539 body readback | `.loom/specs/WI-1540/spec.md` S2 | WI-1540 / PR #1539 / head 0ce75ba6ea0c88bb6974b1b645cbbfc8300b8aa5 | current | PR gate | Re-render and preflight PR body if branch, head, or Work Item changes. |
