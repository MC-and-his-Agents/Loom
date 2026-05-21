# WI-810 Spec

## Outcome

`governance-profile upgrade-plan --host github` outputs a deterministic read -> judge -> write -> verify plan for GitHub profile adoption instead of only listing missing fields.

## Acceptance

- The upgrade plan includes `loom-adoption-decisions/v1`, `loom-guided-adoption-plan/v1`, and `loom-companion-generation/v1`.
- The adoption decisions cover the fixed GitHub profile decision set: FR / Work Item layering, closeout/reconciliation read surface, repo companion, repo interop, GitHub controlled merge, repo-specific residue, spec review instruction locator, implementation review instruction locator, authority boundary, and guardian/integration contract boundary.
- Every judgment contains `id`, `question`, `source_locator`, `reasoning`, `write_targets`, `verification_commands`, and `status`.
- Every judgment expands into read, judge, write, and verify steps.
- Write targets are concrete file locators or GitHub host object locators.
- Companion generation remains dry-run by default and does not generate repo-native shadow verdicts.
- `loom_check` validates the fixed decision coverage and the four-phase guided plan.

## Non Goals

- Do not enable blocking gate rollout.
- Do not execute verification commands from the plan.
- Do not write GitHub or repo files from `upgrade-plan`.
- Do not promote repo-native review, guardian, or integration-contract rules into Loom core.
