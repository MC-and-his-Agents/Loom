# Current Status

## Derived Fact Chain View

- Item ID: WI-1196
- Goal: Separate target repository Loom payload install state from Codex Desktop workstation plugin registration state, then close out #1196 and #1197-#1203 through merge-ready, merge, target branch validation, and issue closeout.
- Scope: #1196 issue tree only: freeze terminology, update README and adoption docs, extend CLI diagnostics, add explicit Codex workstation registration, recommend registration from repair and upgrade plans, add HotCP-style regression coverage, and collect release/readiness evidence. Do not revive `@mc-and-his-agents/loom-installer` as the primary install path, do not write Codex Desktop private state into target repository truth, and do not claim current-session plugin hot reload.
- Execution Path: issue #1196 -> branch work/1196-codex-workstation-registration -> workspace `.` -> PR pending.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1196.md
- Review Entry: .loom/reviews/WI-1196.json
- Validation Entry: make loom-check; python3 tools/check_cli_contract.py; python3 tools/check_release_surface.py; loom doctor/host verify fixture smokes; workstation registration dry-run/apply fixture; docs link check; git diff --check; PR/CI status after push
- Closing Condition: #1196-#1203 have closeout evidence, the target PR is merged, target branch validation passes, and child issues then parent issue are closed with evidence.
- Current Checkpoint: merge
- Current Stop: PR #1212 is open on branch `work/1196-codex-workstation-registration`; PR body now declares `Loom Work Item: WI-1196`, local merge checkpoint is the active gate, and CI merge gate is being re-consumed.
- Next Step: Re-run PR checks, merge PR #1212 after merge-ready passes, validate target branch, and close #1197-#1203 then #1196.
- Blockers: None recorded.
- Latest Validation Summary: Passing: `make loom-check` full source surface; `python3 tools/check_cli_contract.py`; `python3 tools/check_release_surface.py`; `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_check.py src/skills/shared/scripts/loom_check.py`; `git diff --check`; `python3 tools/skills_surface.py check`; `python3 tools/host_adapter_check.py`; `python3 tools/version_surface_check.py`; `python3 tools/check_demo_bootstrap_fixture.py`; focused isolated fixture where `host install --apply` creates target payload, `host verify` passes with `verifies: target-repository-payload`, `doctor` blocks on missing workstation registration before register, `repair plan` and `upgrade-plan` stay non-mutating, `host register --dry-run` writes no isolated user files, `host register --apply` writes isolated user registration, and `doctor` passes after registration. Pending: PR/CI, merge-ready, merge, target branch validation, and issue closeout evidence.
- Recovery Boundary: Current batch owns #1196-#1203 only. It may edit CLI, adoption docs, README, regression tests, Loom carriers for #1196, PR/issue evidence, and release/readiness closeout records. It must not change deprecated installer primary-path semantics, persist Codex Desktop private state into target repo truth, or claim current-session hot reload.
- Current Lane: loom-hardening/codex-workstation-registration

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: make loom-check
- Lane Entry: loom-hardening/codex-workstation-registration

## Sources

- Static Truth: .loom/work-items/WI-1196.md
- Dynamic Truth: .loom/progress/WI-1196.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
