# Current Status

## Derived Fact Chain View

- Item ID: WI-782
- Goal: Require verify to prove stable Loom carriers are visible to Git
- Scope: Extend `loom_init verify` and regression coverage so required stable `.loom` carriers fail closed when ignored or missing, report untracked carriers that need `git add`, and avoid treating runtime scratch/cache/tmp paths as stable carriers.
- Execution Path: adoption/bootstrap
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-782.md
- Review Entry: .loom/reviews/WI-782.json
- Validation Entry: targeted stable carrier Git visibility fixture; python3 tools/skills_surface.py check; make skills-check; make loom-check
- Closing Condition: #782 is implemented, validated, reviewed, merged, and issue state reflects the PR
- Current Checkpoint: build
- Current Stop: #782 implementation and follow-up review fixes are committed on work/782-verify-stable-carriers-git-visible; review records and PR closeout remain.
- Next Step: Record fresh spec and code review records, run adopt verify, then push PR and merge #782 if host checks pass.
- Blockers: No #782 implementation blockers recorded; full make loom-check hang is retained as a validation caveat in Latest Validation Summary.
- Latest Validation Summary: py_compile passed for changed runtime scripts; python3 tools/skills_surface.py check passed; make loom-demo-new-project passed; make skills-check passed; targeted check_deep_existing_repo_bootstrap passed including runtime-as-stable fail-closed fixture; root loom_init verify and shadow-parity passed before the follow-up fix; make loom-check was attempted after the follow-up fix and hung in repo-interop shadow-parity hash-drift fixture, not in the #782 stable-carrier fixture.
- Recovery Boundary: .loom/work-items/WI-782.md is the active static work item carrier.
- Current Lane: work/782-verify-stable-carriers-git-visible

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-782.md
- Dynamic Truth: .loom/progress/WI-782.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
