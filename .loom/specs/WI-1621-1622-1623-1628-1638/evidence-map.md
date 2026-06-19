# Evidence Map

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `docs/adoption/global-cli-user-plugin-contract.md` | #1621 #1622 #1623 #1628 #1638 | WI-1621-1622-1623-1628-1638 / branch work/1621-1628-global-install-contracts | present | adoption docs / implementation Work Items / merge-ready | Update if install contract scope changes. |
| EV-002 | test_evidence | `.loom/progress/WI-1621-1622-1623-1628-1638.md` | targeted local checks | WI-1621-1622-1623-1628-1638 / current PR head | present | review / PR gate / closeout | Refresh after head, PR body, or hosted gate changes. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1621-1622-1623-1628-1638.md` | EV-001 EV-002 | WI-1621-1622-1623-1628-1638 / current PR head | present | hosted merge gate / closeout | Refresh after head, PR body, or hosted gate changes. |
