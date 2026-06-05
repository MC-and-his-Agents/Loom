# WI-1240-1242 Plan

## Suite Contract

- Suite path: minimal
- Suite path consumed: minimal
- Spec locator: .loom/specs/WI-1240-1242/spec.md
- Plan locator: .loom/specs/WI-1240-1242/plan.md
- Full-suite-artifacts not_applicable: rationale: #1239 froze the provider contract and #1240/#1241/#1242 provide bounded implementation acceptance; consumer boundary: build, review, PR gate, hosted checks, release judgment, and parent closeout consume this plan plus targeted runtime evidence; recheck condition: require full path if the batch expands into migration repair, fixture migration, docs/release closeout, or a new provider selection contract.

## Steps

1. Add runtime provider modeling to installed-state metadata and validation.
2. Update detect, doctor, verify, and repair classification so global-cli provider state can pass without `.loom/bin` and stale `.loom/bin` is repairable residue.
3. Update fact-chain/status/story-carrier entrypoint reporting to use global `loom ... --json` commands for global-cli provider state.
4. Preserve repo-local wrapper behavior and fallback command prefixes for existing repository-local runtime state.
5. Apply governance command-prefix parity to source scripts, generated skill runtime copies, and demo bootstrap fixtures.
6. Add targeted regression coverage for global-cli provider success, malformed provider fail-closed behavior, stale `.loom/bin` residue, and repo-local wrapper compatibility.
7. Sync WI carrier evidence, PR body machine fields, and release impact plan without implementing #1243/#1244 migration repair/fixtures or #1245/#1246 docs/release closeout.
8. Run targeted local validation, PR gate, hosted checks, and release judgment; classify the known full contract self-repo carrier failure as environment/carrier-state when reproduced under terminal WI-1311 or uncommitted carrier purity.

## Scenario Mapping

- S1 -> Steps 1 and 6.
- S2 -> Steps 1, 2, and 6.
- S3 -> Steps 2 and 6.
- S4 -> Steps 3 and 6.
- S5 -> Steps 4, 5, and 6.
- S6 -> Steps 5, 7, and 8.

## Acceptance Mapping

- AC-1 -> structural check: `tools/loom.py`.
- AC-2 -> test evidence: targeted global-cli smoke and `tools/check_cli_contract.py` fixtures.
- AC-3 -> behavior evidence: fact-chain/status/story-carrier targeted smoke and `tools/loom.py`.
- AC-4 -> test evidence: repo-local wrapper fallback tests in targeted smoke and CLI contract coverage.
- AC-5 -> structural check: `tools/governance_surface.py`, `src/skills/shared/scripts/governance_surface.py`, `skills/shared/scripts/governance_surface.py`, generated skill runtime copies, and `examples/new-project` fixture sync.
- AC-6 -> validation evidence: `.loom/progress/WI-1240-1242-build-evidence.json`, `git diff --check`, py_compile, skills check, demo bootstrap check, targeted global-cli smoke, fact-chain/admission/build checks, PR gate, hosted checks, and release judgment.
- AC-7 -> manual evidence: PR body release impact / release note plan, with release execution deferred to #1245/#1246 or parent closeout flow.

## Ownership Constraints

- Write ownership is limited to #1240/#1241/#1242 implementation, generated runtime parity, demo fixture parity, and WI/PR carriers for this batch.
- Non-goals: #1243/#1244 migration repair/fixtures, #1245/#1246 docs/release closeout, and unrelated review-head gate changes in `src/skills/shared/scripts/loom_flow.py`.
- Main executor owns integration, validation evidence, PR metadata, and final gate consumption.

## Applicability Boundary

- Full-suite-artifacts not_applicable: rationale: this is a bounded provider-runtime implementation with frozen contract and targeted behavior evidence; consumer boundary: minimal suite, Work Item, build evidence, review, PR gate, hosted checks, and release impact plan are sufficient for merge readiness; recheck condition: require additional formal artifacts if provider selection semantics change, downstream no-`.loom/bin` evidence cannot be reproduced, runtime/admission failure types cannot be classified, or the batch expands beyond #1240/#1241/#1242.
