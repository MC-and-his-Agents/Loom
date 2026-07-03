# WI-1896 Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md, consistency-analysis.md; rationale: WI-1896 is a focused CLI safety hardening with direct issue scope and focused contract fixtures; consumer boundary: suite validate, review, PR gate, merge-ready, and closeout for WI-1896; recheck condition: require full suite artifacts if the change expands beyond workstation registry validation into upgrade orchestration, runtime cache migration, target repository mutation, or release behavior.
- Consumes:
  - Spec locator: `.loom/specs/WI-1896/spec.md`
  - Scenario ids / locators: S1, S2, S3
  - Acceptance ids / locators: A1-A5
  - Story Readiness consumed state: not required; rationale: #1896 has precise negative cases and existing registry contract fixtures; consumer boundary: suite validate, review, PR gate, and closeout; recheck condition: require story readiness if the work changes user-facing workstation upgrade workflow.
  - Story Business Confirmation consumed state: not required; rationale: this repair only changes CLI fail-closed classification; consumer boundary: suite validate, review, PR gate, and closeout; recheck condition: require business confirmation if repository mutation policy or upgrade UX semantics change.
- Produces:
  - Validation strategy by scenario: touched-file py compile, workstation-registry contract surface, and diff hygiene.
  - Test strategy by acceptance: temp HOME registry fixtures for missing path, remote drift, duplicate id, opted-out, and positive register/list/unregister behavior.
  - Implementation contract locator: `.loom/specs/WI-1896/implementation-contract.md`
  - Fresh verification evidence expectation: `.loom/progress/WI-1896.md` latest validation summary and evidence map.
- Locator:
  - Plan locator: `.loom/specs/WI-1896/plan.md`
- Provenance:
  - Source spec / issue / PR locator: `.loom/specs/WI-1896/spec.md`, #1896, #1893.
  - Freshness rule: refresh after workstation registry implementation, fixture, docs, PR metadata, review, hosted-check, or closeout evidence changes.

## Steps

1. Add live registry classification for missing path, remote hash drift, and duplicate id.
2. Include repair guidance and remove blocking entries from `eligible_for_plan`.
3. Make `loom workstation list` return `block` when blocking classifications exist.
4. Make `loom workstation register` refuse writes while the existing registry has blocking ambiguity.
5. Add focused negative contract coverage for missing path, remote drift, and duplicate id.

## Dependencies

- Consumes #1894 schema and #1895 CLI command surface.
- Does not block #1903 implementation except as a registry safety prerequisite.

## Validation

- `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `python3 tools/check_cli_contract.py --surface workstation-registry`
- `python3 tools/loom.py suite validate --target . --item WI-1896 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1896 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1896 --json`
- `git diff --check`

## Test Strategy

- A1 -> test evidence: `workstation-registry` missing path temp HOME fixture.
- A2 -> test evidence: `workstation-registry` remote hash drift temp HOME fixture plus register refusal assertion.
- A3 -> test evidence: `workstation-registry` duplicate id temp HOME fixture.
- A4 -> test evidence: existing opted-out list-only fixture remains non-blocking.
- A5 -> structural check: `.loom/specs/WI-1896/evidence-map.md`, `.loom/reviews/WI-1896.json`, PR metadata readback, PR gate, merge-ready, and closeout consumption.
