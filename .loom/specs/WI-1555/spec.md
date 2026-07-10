# WI-1555 Spec

- Suite path: not_applicable
- Rationale: WI-1555 is a focused CLI/runtime orchestration hardening slice. It wires existing reconciliation, closeout check, carrier closeout-sync, recovery writeback, and carrier refresh primitives behind a single facade; it does not introduce new product semantics beyond the explicit dry-run/apply command contract.
- Consumer boundary: Review, PR gate, hosted checks, and milestone/12 closeout consumers may use this suite decision only for the #1555 wrapper/runtime contract. Closeout freeze admission, closeout-specific gate policy, release/no-release judgment, and docs/skills convergence remain governed by #1532, #1533, #1515, and #1534.
- Recheck condition: Recheck with a full or minimal suite if `closeout run` starts implementing new closeout risk policy, batch/mixed-risk behavior, release judgment, or hosted gate semantics instead of orchestrating existing runtime primitives.
- Scope proof: The implementation diff is limited to `tools/loom.py`, `tools/check_cli_contract.py`, and WI-1555 carrier/review metadata.
- Review requirement: current_head_review_required
- Formal-suite not_applicable: rationale: WI-1555 productizes a narrow CLI wrapper/runtime orchestration entry for existing closeout primitives and does not define a new formal product behavior suite. consumer boundary: suite validate, review, PR gate, hosted CI, and issue closeout may consume this locator only as the formal suite path decision; implementation review, fact-chain, PR metadata, CI, closeout evidence, and post-merge terminal carrier evidence remain required. recheck condition: require a full or minimal suite if this PR starts changing closeout risk policy, batch or mixed-risk behavior, release/no-release judgment, hosted gate semantics, or a runtime primitive contract beyond wrapper orchestration. scope proof: `git diff origin/main...HEAD` must remain limited to `tools/loom.py`, `tools/check_cli_contract.py`, and WI-1555 carrier/review metadata. review requirement: `.loom/reviews/WI-1555.json` must review the current PR head before merge-ready.

## Acceptance

- `loom closeout run` is visible in `loom help --json`.
- Dry-run outputs a machine-readable step plan without mutating host or repo carriers.
- `--apply` delegates host reconciliation, closeout check, terminal carrier sync, recovery writeback, shadow refresh, and final closeout check in order.
- Apply mode stops before later mutations when a prerequisite step blocks.
- Wrapper contract fixtures cover argument forwarding, inferred terminal metadata, apply ordering, and stop-before-carrier mutation.
