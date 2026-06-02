# WI-1196 Plan

- Suite path: minimal

## Validation

- S1 -> automated validation evidence: `python3 tools/check_cli_contract.py`, `loom host verify --host codex --mode plugin --target <fixture> --json`, and manual isolated fixture smoke.
- S2 -> automated validation evidence: `loom host register --host codex --source <fixture>/plugins/loom --scope user --dry-run --json` and `--apply --json` under isolated `HOME`/`CODEX_HOME`.
- S3 -> automated validation evidence: `loom doctor --target <fixture> --json`, `loom repair plan --target <fixture> --json`, and `loom upgrade-plan --target <fixture> --json`.
- AC-1 -> test evidence: CLI contract fixture and focused command smokes.
- AC-2 -> structural evidence: docs link check and `python3 tools/check_release_surface.py`.
- AC-3 -> test evidence: HotCP-style isolated HOME fixture in `tools/check_cli_contract.py`.

## Minimal Path Applicability Records

- full-path-artifacts not_applicable rationale: #1196 is a bounded CLI/docs/test Work Item with GitHub issue acceptance already authored; no separate research, contracts, readiness-checklist, consistency-analysis, execution-breakdown, or task-carrier artifacts are required for review. consumer boundary: review, merge-ready, repair/upgrade planning, and closeout consume #1196-#1203 issue acceptance, `.loom/work-items/WI-1196.md`, `.loom/progress/WI-1196.md`, this minimal spec/plan, validation output, and PR evidence. recheck condition: if command naming, privacy/security semantics, or external host behavior expands beyond the current issue contract, author the full suite before review.
