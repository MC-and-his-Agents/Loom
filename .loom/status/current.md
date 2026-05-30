# Current Status

## Derived Fact Chain View

- Item ID: WI-1152
- Goal: Add generated skills surface parity fixture coverage for the full spec suite CLI integration chain.
- Scope: #1152 only: prove route matrix, shared references, installed layout, and generated package runtime surfaces remain in parity after suite integration.
- Execution Path: issue #1152 -> branch work/1152-generated-skills-surface-parity -> target-local workspace `.` -> PR pending.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1152.md
- Review Entry: .loom/reviews/WI-1152.json
- Validation Entry: git diff --check; focused rg; PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py; generated/package/install surface checks as applicable.
- Closing Condition: #1152 PR is opened with validation evidence for the owning worker; main thread owns final review, merge ordering, Project closeout, #1152 issue closeout, and parent FR/phase reconciliation after merge.
- Current Checkpoint: merge
- Current Stop: WI-1152 CI remediation is ready for PR gate and main-thread review; worker will not merge, close out, or update Project.
- Next Step: Hand PR URL, head SHA, validation, and checks readback to the main thread; do not merge, closeout, or sync Project.
- Blockers: None recorded.
- Latest Validation Summary: Passing local evidence on 2026-05-30 for CI remediation head a2765df1cdaecf27a92a3088b665d1effffacf99: git diff --check; focused rg for WI-1152, generated skills surface, route matrix, shared references, installed layout, runtime parity, /speckit, .specify, skills_surface, and loom skills check; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .
- Recovery Boundary: #1152 owns only generated skills surface parity fixture coverage for route matrix, shared references, installed layout, and generated runtime surfaces. It does not implement #1150 stale host conflict fixtures, #1151 scaffold mutation fixtures, #1153 PR gate / merge-ready / closeout integration fixtures, Project reconciliation, #1145 closeout, or #1107 closeout.
- Current Lane: full-spec-suite-cli/e2e-governance/generated-skills-surface-parity

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1152.md
- Dynamic Truth: .loom/progress/WI-1152.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
