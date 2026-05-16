# Current Status

## Derived Fact Chain View

- Item ID: WI-763
- Goal: Host-enforce Loom semantic review approval before PR merge
- Scope: Add a PR-specific merge gate, host workflow, controlled merge wrapper, PR #762 regression evidence, generated skill surfaces, and validation proving raw review evidence cannot satisfy approval.
- Execution Path: self-governance/pr-semantic-review-gate/763
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-763.md
- Review Entry: .loom/reviews/WI-763.json
- Validation Entry: python3 tools/loom_check.py . && make skills-check && git diff --check
- Closing Condition: PR gate is implemented and required by host branch protection or ruleset; this branch has a fresh authored review record for the PR head; controlled merge consumes only the authored Loom review record and required-check readback; #763 and child issues contain proof; implementation is merged; main readback proves loom-pr-merge-gate is required.
- Current Checkpoint: merge checkpoint
- Current Stop: Local implementation, ruleset fixture support, installer package version bump, vendored .loom/bin runtime refresh, validation refresh, and default loom/default-codex review run are complete on branch harden-pr-semantic-review-gate.
- Next Step: Record the refreshed authored implementation review for the vendored runtime refresh, push PR #769, prove live PR-head checks and host readback, then merge through controlled-merge.
- Blockers: None recorded.
- Latest Validation Summary: 2026-05-16 validation refresh for WI-763 at current branch: py_compile for touched entrypoints -> OK; installer version bump gate -> OK; git diff --check -> OK; adopt verify, make skills-check, shadow-parity, and full loom_check passed before vendored runtime refresh; root .loom/bin runtime refresh is in progress to satisfy root-self-governance.
- Recovery Boundary: Branch harden-pr-semantic-review-gate; parent issue #763; active Work Item WI-763; raw review evidence remains runtime evidence only and never approval truth.
- Current Lane: self-governance / #763 semantic review host enforcement

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-763.md
- Dynamic Truth: .loom/progress/WI-763.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
