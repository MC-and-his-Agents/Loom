# Current Status

## Derived Fact Chain View

- Item ID: WI-571
- Goal: Deliver #571 approval and sandbox policy read surface for v0.8.0 / #531.
- Scope: Define approval/sandbox policy read contracts, preserve the host-adapter boundary, expose policy and risk summary in status/flow output, and validate missing/conflict/unsafe policy fixtures.
- Execution Path: phase/v0.8.0/fr/571
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-571.md
- Review Entry: .loom/reviews/WI-571.json
- Validation Entry: make check
- Closing Condition: `policy_readiness` exposes approval policy, sandbox policy, `declared | missing | conflict | unsafe`, and risk summary; required policy risk blocks the owning surface; optional/advisory policy risk remains advisory; status reads the latest derived summary; fixtures cover missing/conflict/unsafe policy; `make check` passes cleanly; and the #571 batch PR absorbs #572-#575.
- Current Checkpoint: build checkpoint
- Current Stop: WI-571 approval/sandbox policy read surface implementation, docs, generated skill surfaces, and policy fixtures are in progress on the batch branch.
- Next Step: Run targeted status/flow checks and full `make check`, then record review evidence and open the #571 PR.
- Blockers: None recorded.
- Latest Validation Summary: Initial policy read surface implementation is under validation; targeted fixture smoke must pass before merge-ready.
- Recovery Boundary: Branch work/571-approval-sandbox-read-surface; active item WI-571; policy readiness evidence is derived from companion locators and must not replace recovery truth, execution_attempt evidence, retained host action results, or host permission/sandbox systems.
- Current Lane: v0.8.0 / #531 / #571 approval and sandbox policy read surface

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-571.md
- Dynamic Truth: .loom/progress/WI-571.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
