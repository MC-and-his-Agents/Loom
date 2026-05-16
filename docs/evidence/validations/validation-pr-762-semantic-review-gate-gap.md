# Validation: PR #762 Semantic Review Gate Gap

## 1. Sample

- Repository: `clawhello/Loom`
- PR: `#762`
- Merge commit: `806c5688584e36c27cb6cf2dcb62485e9e6f8e1b`
- Validation date: `2026-05-16`
- Follow-up parent issue: `#763`

This record captures a Loom self-governance regression: Loom's internal gate model treated semantic review as a hard merge prerequisite, but the host merge path did not enforce that prerequisite for PR `#762`.

## 2. Observed Gap

Live GitHub readback showed:

- PR `#762` was merged.
- GitHub review records for PR `#762` were absent.
- `main` branch protection required `py-compile`, `demo-bootstrap`, `repo-local-cli`, and `loom-check`.
- `main` did not require a PR-specific semantic review gate check.
- active GitHub rulesets were empty at the time of the readback.
- required approving review count was `0`.

The gap was not that Loom lacked a semantic review concept. The gap was that no host-enforced check proved the current PR head had a fresh authored Loom review record before merge.

## 3. Failure Mode

`make loom-check` is too broad to answer the PR-local merge question by itself. It can prove repository-level contracts, but it does not bind all of these facts to the current PR head:

- PR is bound to one Loom Work Item.
- Work Item `review_entry` exists.
- authored review record at `review_entry` has `decision == allow`.
- `reviewed_head` covers the current PR head.
- `reviewed_validation_summary` matches current recovery truth.
- raw review, shadow review, PR text, CI success, or GitHub comments were not consumed as semantic approval.

Because this bridge was missing from branch protection, a direct host merge could bypass Loom's intended semantic approval hard gate.

## 4. Loom Hardening Response

The regression is now mapped to reusable Loom capability:

- [pr-merge-gate.md](../../methodology/harness/pr-merge-gate.md) defines the narrow PR-specific approval bridge.
- [controlled-merge.md](../../methodology/harness/controlled-merge.md) treats bare `gh pr merge` as a bypass risk unless the stable PR gate check is host-enforced.
- [host-action-contract.md](../../methodology/harness/host-action-contract.md) exposes `pr-gate check` and `controlled-merge check|merge` as explicit host actions.

The stable host check name is:

```text
loom-pr-merge-gate
```

## 5. Evidence Standard

This regression is closed only when live readback proves:

- workflow exists and ran for the PR head
- required check list or active ruleset requires `loom-pr-merge-gate`
- fresh authored review approval passes the gate
- missing/stale/non-allow review blocks the gate
- controlled merge consumes the gate and required-check readback before delegating to `gh pr merge`

Until all conditions are true, the regression remains an active Loom self-governance hardening item.
