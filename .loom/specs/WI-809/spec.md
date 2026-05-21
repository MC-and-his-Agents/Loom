# WI-809 Spec

## Outcome

Loom can read a repository's GitHub-profile adoption signals and emit a deterministic maturity judgment for the GitHub profile upgrade assistant without writing files, mutating GitHub, or enabling blocking gates.

## Acceptance

- `governance-profile status --host github` and upgrade-plan flows expose GitHub profile maturity evidence.
- The detector keeps maturity level values limited to `unadopted`, `light`, `standard`, and `strong`.
- Blocked adoption is represented as a separate maturity judgment, not as a maturity level.
- Output includes source locators and missing/conflicting signal evidence for light, standard, strong, and blocked cases.
- `loom_check` validates GitHub profile maturity fixtures.
- Generated skills/runtime surfaces stay synchronized with `src/skills`.

## Non Goals

- Do not write files as part of detector status or upgrade-plan judgment.
- Do not modify GitHub issue, Project, PR, branch protection, or check state.
- Do not enable or require a blocking gate.
- Do not expand this Work Item into #810 read-judge-write-verify planning or #811 rollout/rollback activation.
