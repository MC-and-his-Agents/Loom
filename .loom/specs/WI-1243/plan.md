# WI-1243 Plan

## Suite Contract

- Suite path: minimal
- Suite path consumed: minimal
- Spec locator: .loom/specs/WI-1243/spec.md
- Plan locator: .loom/specs/WI-1243/plan.md
- Full-suite-artifacts not_applicable: rationale: the batch is bounded to runtime-carrier migration planning, fixture coverage, and adoption docs; consumer boundary: suite validate, review, PR gate, and merge-ready consume this plan plus targeted CLI contract evidence; recheck condition: promote to full suite if mutating apply, shared carrier closeout, release mechanics, or downstream runtime rewrites enter scope.

## Steps

1. Replace retained-`.loom/bin` abstract residue classification with deterministic runtime-carrier migration actions.
2. Scan repo-local carrier and docs surfaces for `.loom/bin` references, separating gate blockers from guidance-only references.
3. Keep `.loom/bin` deletion proposal-only and explicit-confirmation-only while `repair apply` remains fail-closed.
4. Mirror runtime-carrier migration semantics into `loom upgrade-plan`.
5. Extend CLI contract fixtures for both blocker-free and blocker-present retained-`.loom/bin` repositories.
6. Update adoption docs to explain runtime-carrier migration boundaries.
7. Validate with `git diff --check`, targeted CLI contract surface, `py_compile`, and WI-1243 suite validation.

## Scenario Mapping

- S1 -> Steps 1 and 4.
- S2 -> Steps 1 and 3.
- S3 -> Steps 2 and 5.
- S4 -> Steps 4 and 5.
- S5 -> Steps 6 and 7.

## Acceptance Mapping

- AC-1 -> structural check: `tools/loom.py` repair/upgrade plan payloads and `python3 tools/check_cli_contract.py --surface adoption-host-metadata`.
- AC-2 -> test evidence: retained-`.loom/bin` fixture asserts `requires_confirmation=true`, `deletes=[".loom/bin"]`, and proposal-only semantics.
- AC-3 -> test evidence: blocked retained-`.loom/bin` fixture asserts exact blocker locators in `.loom/status/current.md` and `.loom/bootstrap/init-result.json`.
- AC-4 -> test evidence: `python3 tools/check_cli_contract.py --surface adoption-host-metadata`.
- AC-5 -> manual and structural evidence: `docs/adoption/loom-installed-state-v2.md` and `docs/adoption/cli-first-legacy-migration-playbook.md`.
