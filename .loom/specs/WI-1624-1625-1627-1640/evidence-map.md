# Evidence Map

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py` | #1624 #1625 #1627 #1640 | WI-1624-1625-1627-1640 / branch `work/1624-global-install-cutover` | present | install / installed-state / detect / doctor | Re-run CLI contract checks after any CLI behavior change. |
| EV-002 | test_evidence | `.loom/progress/WI-1624-1625-1627-1640.md` | metadata-only adoption and AGENTS bootstrap validation | current branch head | present | PR gate / review | Refresh after install parser or planned writes change. |
| EV-003 | test_evidence | `.loom/progress/WI-1624-1625-1627-1640.md` | installed-state validator, doctor/detect, legacy fixture validation | current branch head | present | PR gate / review | Refresh after validator, legacy detection, or host install behavior changes. |
| EV-004 | test_evidence | `.loom/progress/WI-1624-1625-1627-1640.md` | syntax, diff hygiene, host/release surface validation | current branch head | present | PR gate / review | Re-run before PR metadata preflight and merge-ready. |
| EV-005 | fresh_verification_input | `.loom/progress/WI-1624-1625-1627-1640.md` | EV-001 EV-002 EV-003 EV-004 | current branch head | present | PR gate / review / merge-ready | Refresh after code, carrier, PR body, review, or hosted check changes. |
