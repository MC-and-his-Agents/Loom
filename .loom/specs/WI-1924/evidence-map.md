# WI-1924 Evidence Map

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
|---|---|---|---|---|---|---|---|
| EV-001 | behavior_evidence | `skills/shared/scripts/loom_flow.py` | S1 S2 S3 / A1 A2 A3 | closeout role merge-ready PR selection | present | review / PR gate / closeout | Recheck after closeout role code changes. |
| EV-002 | test_evidence | `python3 tools/check_cli_contract.py --surface governance-closeout` | S1 S2 S3 / A1 A2 A3 | carrier-sync fixture with implementation PR head split | present | review / PR gate | Rerun after closeout fixture or runtime changes. |
| EV-003 | test_evidence | `python3 tools/check_cli_contract.py --surface closeout-wrapper` | S3 / A3 | wrapper role argument preservation | present | review / PR gate | Rerun after wrapper or role args changes. |
| EV-004 | generated_surface | `python3 tools/skills_surface.py check --surface generated-tree-drift` | S1 S2 / A1 A2 | generated skills/runtime copy parity | present | package / hosted checks | Rerun after source/runtime copy changes. |
| EV-005 | test_evidence | `python3 tools/py_compile_clean.py skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_flow.py plugins/loom/skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py examples/new-project/.loom/bin/loom_flow.py tools/check_cli_contract.py` | S1 S2 / A1 A2 | Python syntax/readability | present | hosted checks | Rerun after Python edits. |
| EV-006 | test_evidence | `CODEX_EXPORT_GH_TOKEN=1 python3 tools/loom.py closeout status --target . --item WI-1895 --issue 1895 --implementation-pr 1921 --carrier-sync-pr 1923 --pr-role carrier_sync_pr --branch work/1895-review-carrier-repair --json` | S1 S2 / A1 A2 | real WI-1895 carrier-sync closeout status | present | closeout / milestone evidence | Rerun after closeout gate edits. |
| EV-007 | test_evidence | `git diff --check` | S1-S3 / A1-A3 | diff hygiene | present | review / PR gate | Rerun after any file edit. |
| EV-008 | fresh_verification_input | `.loom/progress/WI-1924.md` | EV-001 EV-002 EV-003 EV-004 EV-005 EV-006 EV-007 / A1-A3 | current branch / current head / WI-1924 | present | review / merge-ready / closeout | Refresh after validation, PR metadata, review, hosted checks, merge, or closeout evidence changes. |
