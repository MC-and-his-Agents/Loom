# WI-1924 Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md, consistency-analysis.md; rationale: WI-1924 is a focused closeout gate bug fix over an already observed role-binding regression; consumer boundary: suite validate, review, PR gate, merge-ready, closeout status for WI-1924, and WI-1895 carrier-sync closeout evidence; recheck condition: require full suite artifacts if the change expands into new closeout workflow semantics, repository migration behavior, or release policy.
- Consumes:
  - Spec locator: `.loom/specs/WI-1924/spec.md`
  - Scenario ids / locators: S1, S2, S3
  - Acceptance ids / locators: A1-A3
  - Story Readiness consumed state: not required; rationale: #1924 has a precise issue scope and concrete failing closeout status; consumer boundary: suite validate, review, PR gate, and closeout; recheck condition: require story readiness if the work changes user-facing workstation upgrade behavior.
  - Story Business Confirmation consumed state: not required; rationale: this repair only changes internal gate evidence binding; consumer boundary: suite validate, review, PR gate, and closeout; recheck condition: require business confirmation if closeout policy or repository mutation semantics change.
- Produces:
  - Validation strategy by scenario: py compile, focused governance-closeout contract surface, closeout-wrapper surface, generated-tree drift check, live WI-1895 closeout status regression, and diff hygiene.
  - Test strategy by acceptance: synthetic split-head carrier-sync fixture plus live WI-1895 carrier-sync status readback.
  - Implementation contract locator: not_applicable; rationale: spec and plan are sufficient for this bounded gate repair; consumer boundary: review and PR gate; recheck condition: require implementation-contract.md if the fix expands beyond closeout role evidence binding.
  - Fresh verification evidence expectation: `.loom/progress/WI-1924.md` latest validation summary and evidence map.
- Locator:
  - Plan locator: `.loom/specs/WI-1924/plan.md`
- Provenance:
  - Source spec / issue / PR locator: `.loom/specs/WI-1924/spec.md`, #1924, #1895, #1923.
  - Freshness rule: refresh after closeout gate implementation, checker fixture, generated copy, PR metadata, review, hosted-check, or closeout evidence changes.

## Steps

1. Add role helpers for current PR and merge-ready evidence PR selection.
2. Pass implementation PR payload into closeout backlink checks for carrier/final closeout roles.
3. Compare retained merge-ready attempt head against the selected implementation PR head while keeping current PR host checks and merge backlink unchanged.
4. Add a governance-closeout contract fixture with different implementation and carrier PR heads.
5. Sync runtime copies and validate.

## Dependencies

- Consumes WI-1895 closeout repair failure as regression evidence.
- Does not block #1896 implementation.

## Validation

- `python3 tools/check_cli_contract.py --surface governance-closeout`
- `python3 tools/check_cli_contract.py --surface closeout-wrapper`
- `python3 tools/skills_surface.py check --surface generated-tree-drift`
- `python3 tools/py_compile_clean.py skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_flow.py plugins/loom/skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py examples/new-project/.loom/bin/loom_flow.py tools/check_cli_contract.py`
- `CODEX_EXPORT_GH_TOKEN=1 python3 tools/loom.py closeout status --target . --item WI-1895 --issue 1895 --implementation-pr 1921 --carrier-sync-pr 1923 --pr-role carrier_sync_pr --branch work/1895-review-carrier-repair --json`
- `python3 tools/loom.py suite validate --target . --item WI-1924 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1924 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1924 --json`
- `git diff --check`

## Test Strategy

- A1 -> test evidence: `governance-closeout` split-head carrier-sync fixture plus real WI-1895 carrier-sync closeout status.
- A2 -> test evidence: unchanged implementation PR and legacy current-PR fallback assertions in `governance-closeout`.
- A3 -> test evidence: `governance-closeout`, `closeout-wrapper`, py compile, generated-tree drift, and diff hygiene checks.
