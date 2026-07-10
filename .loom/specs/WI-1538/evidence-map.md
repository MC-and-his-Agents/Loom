# WI-1538 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | carrier_sync_evidence | `.loom/progress/WI-1531.md` | `.loom/specs/WI-1538/spec.md` S1 S2 | WI-1538 / WI-1531 terminal checkpoint | present | purity checks and downstream Work Items | Re-read WI-1531 progress if purity reports host-complete carrier drift. |
| EV-002 | fact_chain_evidence | `.loom/work-items/WI-1538.md`; `.loom/progress/WI-1538.md`; `.loom/status/current.md` | `.loom/specs/WI-1538/spec.md` S3 | WI-1538 active carrier chain | current | review / PR gate | Re-run fact-chain after final status/shadow refresh. |
| EV-003 | review_history_scope_proof | `git diff -- .loom/progress/WI-1531.md .loom/reviews/WI-1531.json` | `.loom/specs/WI-1538/spec.md` S2 | WI-1531 retained review history | current | PR gate / closeout | Do not rewrite retained review history; only progress checkpoint may change. |
