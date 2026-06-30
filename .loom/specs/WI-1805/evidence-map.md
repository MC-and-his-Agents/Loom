# WI-1805 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `skills/shared/scripts/governance_surface.py` | S1 A1 | WI-1805 / #1826 | present | review / PR gate / release readiness | Re-run host governance capability tests and runtime-copy parity after diagnosis changes. |
| EV-002 | contract_evidence | `docs/adoption/github-profile.md` | S2 A2 | WI-1805 / #1827 | present | review / docs / closeout | Re-run profile contract tests after wording or enum changes. |
| EV-003 | behavior_evidence | `skills/shared/scripts/loom_flow.py` | S3 S4 A3 A4 | WI-1805 / #1828 | present | PR gate / merge-ready | Re-run merge profile tests and CLI contract after merge runtime changes. |
| EV-004 | metadata_evidence | `https://github.com/MC-and-his-Agents/Loom/pull/1831` | S5 A5 | PR #1831 / WI-1805 | present | PR gate / merge-ready / closeout | Re-render PR metadata and rerun preflight/readback after PR body or head changes. |
| EV-005 | release_evidence | `docs/evidence/v0.23.0-release-readiness.md` | S5 A5 A6 | v0.23.0 | present | release readiness / release readback | Re-run package, release surface, version, npm smoke, and payload hash checks after metadata changes. |
| EV-006 | test_evidence | `test/governance_merge_profile_test.py` | A1 A2 A3 A4 A5 | WI-1805 / focused tests | present | review / PR gate / merge-ready | Re-run targeted unittest suite and CLI contract after code, fixture, or metadata changes. |
| EV-007 | fresh_verification_input | `.loom/progress/WI-1805.md` | EV-001 EV-002 EV-003 EV-004 EV-005 EV-006 A1 A2 A3 A4 A5 A6 | WI-1805 / current branch | present | review / PR gate / closeout | Refresh after PR head, review, hosted checks, merge, publish, or readback changes. |

## External Actions

| Subject | Status | Rationale | Consumer Boundary | Recheck Condition | Follow-up Locator |
| --- | --- | --- | --- | --- | --- |
| PR #1831 merge | pending | Requires current-head review, PR gate, and hosted checks. | merge-ready | Re-run after any pushed commit or PR body change. | https://github.com/MC-and-his-Agents/Loom/pull/1831 |
| v0.23.0 GitHub Release/npm publish | pending | Release must happen after PR #1831 merges to `main`. | release closeout | Run release readback against merge commit, tag, npm package, workflow, plugin metadata, and carrier state. | #1830 |
