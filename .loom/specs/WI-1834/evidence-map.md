# WI-1834 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py` | S1 S2 S3 S4 S5 A1 A2 A3 A4 | WI-1834 / #1835-#1837 | present | review / PR gate / merge-ready | Re-run runtime-upgrade CLI contract after command behavior changes. |
| EV-002 | contract_evidence | `docs/methodology/harness/cli-command-matrix.md` | S1 S3 A1 A5 | WI-1834 / #1835 | present | review / docs / release readiness | Re-run aggregate CLI contract after help or matrix changes. |
| EV-003 | docs_evidence | `README.md`; `README.zh-CN.md` | S1 S3 A3 A5 | WI-1834 / #1835 | present | review / user docs | Re-read both README files after wording or badge changes. |
| EV-004 | runtime_copy_evidence | `skills/shared/scripts/loom_flow.py`; `src/skills/shared/scripts/loom_flow.py`; `plugins/loom/skills/shared/scripts/loom_flow.py`; `.loom/bin/loom_flow.py` | S2 S4 A2 A4 A5 | WI-1834 / runtime parity | present | package / plugin / hosted checks | Re-run runtime-copy parity and demo fixture checks after runtime copy changes. |
| EV-005 | fixture_evidence | `examples/new-project/.loom/bin/loom_flow.py`; `examples/new-project/.loom/bootstrap/init-result.json`; `examples/new-project/.loom/bootstrap/manifest.json` | A5 | WI-1834 / demo bootstrap | present | hosted loom-check | Re-run `make loom-demo-new-project-check` after fixture changes. |
| EV-006 | metadata_evidence | `https://github.com/MC-and-his-Agents/Loom/pull/1839` | S4 A4 A6 | PR #1839 / WI-1834 | present | PR gate / merge-ready | Re-render PR metadata and rerun preflight/readback after PR body or head changes. |
| EV-007 | review_evidence | `.loom/reviews/WI-1834.json` | A6 | WI-1834 / reviewed head | present | PR gate / merge-ready | Refresh review if non-carrier code changes after reviewed head. |
| EV-008 | fresh_verification_input | `.loom/progress/WI-1834.md` | EV-001 EV-002 EV-003 EV-004 EV-005 EV-006 EV-007 A1 A2 A3 A4 A5 A6 | WI-1834 / current branch | present | review / PR gate / closeout | Refresh after pushed commit, PR body change, hosted gate, merge, release, or readback. |

## External Actions

| Subject | Status | Rationale | Consumer Boundary | Recheck Condition | Follow-up Locator |
| --- | --- | --- | --- | --- | --- |
| PR #1839 merge | pending | Requires current-head review, PR gate, and hosted checks. | merge-ready | Rerun after any pushed commit or PR body change. | https://github.com/MC-and-his-Agents/Loom/pull/1839 |
| v0.24.0 GitHub Release/npm publish | pending | Release must happen after PR #1839 merges to `main`. | release closeout | Run release readback against merge commit, tag, npm package, workflow, plugin metadata, and carrier state. | #1838 |
