# Implementation Contract

## Suite Contract

- Suite path consumed: minimal
- Spec locator: .loom/specs/WI-1452/spec.md
- Plan locator: .loom/specs/WI-1452/plan.md
- Contract locator: .loom/specs/WI-1452/implementation-contract.md
- Freshness rule: valid for PR #1614 implementation head 07bb4651cc662c008e2855f877fa6ee7844cc931 and later carrier-only sync commits.

## Required Behavior

- `controlled-merge` must compute a `triggered_check_rollup` from current PR status check rollup data.
- Required-check logic must continue to use branch protection / ruleset required contexts exactly as before.
- Triggered checks classify:
  - `SUCCESS`, `SKIPPED`, and `NEUTRAL` as allowed.
  - failed, cancelled, timed out, action required, startup failure, unknown, unreadable, queued, pending, waiting, requested, and in progress states as blocking.
- Missing inputs must distinguish required-check drift, triggered failed check, triggered pending check, and unreadable rollup.

## Allowed Writes

- Runtime source and generated runtime copies.
- Controlled-merge references and docs.
- Targeted CLI contract fixtures.
- Demo stable fixture sync.
- WI-1452 Loom carriers and review record.

## Forbidden Writes

- Live branch protection or rulesets.
- Release version, tags, GitHub Release, npm publication.
- #1292, #1293, or #1285 closeout state.
- Raw host merge outside controlled merge.

## Validation Contract

- Local targeted checks listed in `.loom/specs/WI-1452/plan.md` must pass.
- PR body metadata readback must bind `WI-1452`, branch `work/1452-controlled-merge-triggered-checks`, and the current PR head.
- Hosted checks must be read back and classified before merge.
- Controlled merge check must run before merge.
