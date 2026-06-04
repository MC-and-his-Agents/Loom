# WI-1304 Spec

## Suite Contract

- Suite path: minimal
- Suite index locator: this Work Item uses the minimal two-file suite because the change is a narrow governance runtime fix.
- Full-path artifacts not_applicable: artifacts: contracts.md, readiness-checklist.md, research.md, suite-index.md; rationale: the minimal suite is enough for this bounded gate-consumption fix because the behavior is fully described in spec.md and plan.md and the omitted full-path artifacts would duplicate the same narrow contract; consumer boundary: suite validate, spec review, implementation review, PR gate, merge-ready, and closeout may treat only those four full-path artifacts as not required for WI-1304; recheck condition: require the full suite if #1304 expands beyond governance maturity detection, runtime copy synchronization, or the documented validation commands.
- Consumes:
  - Work Item / FR locator: #1304
  - Story Readiness locator: NA; #1304 is an unblocker defect found during PR-A closeout.
  - Story scenario locator: NA; scenarios are authored below from the observed gate failure.
  - Story Business Confirmation locator: NA; this is internal Loom gate behavior.
- Produces:
  - Scenario ids / locators: S1, S2
  - Acceptance ids / locators: A1, A2, A3, A4, A5
  - Behavior evidence expectation: governance-profile, adopt verify, carrier refresh, and bootstrap-regression command evidence.
- Locator:
  - Spec locator: .loom/specs/WI-1304/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: #1304; PR-A #1297 WI-1264 closeout blocker.
  - Freshness rule: re-run the validation commands after any change to governance_surface runtime copies or WI-1304 carriers.

## Goal

Governance maturity must consume the formal spec gate contract accurately when a Work Item uses a docs-only suite decision. A docs-only contract PR with an approved spec review record should not be downgraded from strong maturity solely because it has no `plan.md`.

## Scope

- In scope: update governance maturity carrier detection so a docs-only suite decision plus an approved `.loom/reviews/<item>.spec.json` can satisfy the formal spec-or-NA portion of the standard maturity gate; sync installed and skill runtime copies.
- Out of scope: changing suite validation rules, weakening spec review, weakening implementation review, changing PR head binding, changing hosted CI requirements, or modifying PR-A/B/C/D contract content.

## Key Scenarios

### Scenario S1

Given
- a Work Item has `.loom/specs/<item>/spec.md` with a docs-only suite decision
- the same Work Item has an approved `.loom/reviews/<item>.spec.json`
- host governance signals are readable

When
- `governance-profile status` reads that Work Item

Then
- maturity treats the formal suite path as satisfied
- `standard` and `strong` are not blocked by missing `plan_path` or `spec_gate`

### Scenario S2

Given
- a Work Item lacks either the docs-only suite decision or the approved spec review record

When
- `governance-profile status` reads that Work Item

Then
- maturity must not treat the formal suite path as satisfied by the docs-only path
- review, suite rationale, CI, PR head binding, and closeout gates remain independently required

## Behavior Evidence

- Story scenario mapping: NA; scenarios are local to #1304.
- Story readiness locator: NA; #1304 is an internal gate unblocker.
- Story business confirmation locator: NA.
- Scenario coverage:
  - S1 -> `python3 .loom/bin/loom_flow.py governance-profile status --target /Users/mc/dev/Loom-worktrees/1264-regression-surface-contract --host github`
  - S2 -> `python3 tools/loom_check.py --profile source --source-surface bootstrap-regression .` and `python3 .loom/bin/loom_flow.py carrier refresh --target . --dry-run`
- Expected evidence locator: WI-1304 PR validation section and hosted checks.
- Freshness rule: evidence is fresh only for the current PR head after WI-1304 review is recorded.

## Exceptions And Boundaries

- Failure modes: missing approved spec review, invalid suite path decision, runtime manifest drift, or stale carrier hash must block or fall back as before.
- Operational boundaries: this change only teaches maturity detection to recognize an already-authored formal docs-only path; it does not create or approve that path.
- Rollback or fallback expectations: revert the governance_surface change and runtime copies; affected docs-only PRs will again require explicit blocker handling.

## Acceptance Criteria

- [x] A1: docs-only suite decision plus approved spec review can satisfy maturity's formal suite path.
- [x] A2: runtime copies and bootstrap hashes remain aligned.
- [x] A3: `adopt verify` and `bootstrap-regression` do not report runtime provenance drift.
- [x] A4: suite validation and review gates remain separate from maturity detection.
- [x] A5: PR-A can consume this after rebasing, without fake minimal suite files.
