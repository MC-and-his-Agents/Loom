# Host-Derived Fact Contract

Loom assigns each field to one authority and derives views at read time.

| Field | Authority |
| --- | --- |
| product goal, scope, closing condition | GitHub issue/FR |
| Work Item identity and parent | GitHub issue tree |
| branch, PR, head, checks, merge | GitHub and Git readback |
| formal workspace | Git worktree plus explicit typed Work Item |
| semantic review | current-head host attestation/artifact |
| product acceptance | product-owned acceptance locator/verdict |
| installed runtime mode | small installed-state metadata plus CLI readback |

No committed global current/status/progress/review/shadow file participates in
the public fact path. Legacy files may be diagnosed for migration but cannot
override an authority or become remediation.

Delivery, product acceptance, and reconciliation remain orthogonal. A green
delivery gate or merged PR cannot independently close a product story.
