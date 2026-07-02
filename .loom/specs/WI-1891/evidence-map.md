# WI-1891 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
|---|---|---|---|---|---|---|---|
| EV-001 | behavior_evidence | `.agents/plugins/marketplace.json` | S1 / A1 / A2 | published Loom marketplace catalog | present | review / PR gate / merge-ready / closeout | Recheck JSON and source path after any catalog edit. |
| EV-002 | behavior_evidence | `plugins/loom/.codex-plugin/plugin.json` | S1 / A2 | plugin manifest targeted by the catalog | present | review / PR gate / release consumer | Recheck if plugin manifest path or plugin name changes. |
| EV-003 | test_evidence | `python3 -m json.tool .agents/plugins/marketplace.json >/dev/null` | S1 / A1 | JSON syntax validation | present | review / PR gate | Rerun after catalog edits. |
| EV-004 | test_evidence | `tmp_home=$(mktemp -d); HOME="$tmp_home" codex plugin marketplace add /Users/mc/dev/Loom; rc=$?; rm -rf "$tmp_home"; exit $rc` | S2 / A3 | Codex marketplace parser with temporary home | present | review / PR gate / #1892 | Rerun after catalog shape, plugin root, or Codex marketplace behavior changes. |
| EV-005 | test_evidence | `python3 tools/loom_check.py --profile source --source-surface source-self-fixture .` | S3 / A4 | source checker accepts published catalog and rejects installed-state fixtures | present | review / PR gate / merge-ready / closeout | Rerun after checker, catalog, generated runtime, or adoption boundary changes. |
| EV-006 | fresh_verification_input | `.loom/progress/WI-1891.md` | EV-001-EV-005 / A1-A5 | current branch / current head / WI-1891 | present | review / merge-ready / closeout | Refresh after final validation, PR metadata, review, hosted checks, and merge readback. |

## Deferred Evidence

| Evidence | Status | Rationale | Consumer Boundary | Recheck Condition | Follow-up |
|---|---|---|---|---|---|
| Real user Codex marketplace installation | not_required | WI-1891 verifies parseability in a temporary home and does not mutate user/workstation state. | review / PR gate / closeout | Require if a future WI installs or upgrades the plugin in a real profile. | #1892 / FR #1902 |
| Install-boundary documentation | deferred | #1892 owns documentation for marketplace/plugin/CLI/repo adoption boundaries. | FR #1889 closeout | Complete before closing FR #1889. | #1892 |
