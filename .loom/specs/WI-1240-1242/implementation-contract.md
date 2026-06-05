# WI-1240-1242 Implementation Contract

## Contract Boundary

- Runtime provider selection follows #1239: `global-cli` and `repo-local-wrapper` are explicit provider states, and malformed provider declarations fail closed.
- No-`.loom/bin` repositories may pass only when installed-state declares the `global-cli` provider and satisfies its provider requirements.
- Stale `.loom/bin` under a valid global-cli provider is retained runtime residue and repairable evidence, not current executable truth.
- Repo-local wrapper compatibility remains supported for existing repository-local runtime state and fallback command-prefix behavior.

## Implementation Surfaces

- `tools/loom.py`: installed-state provider modeling, validate/detect/doctor/verify behavior, repair classification, and fact-chain/status/story-carrier entrypoint reporting.
- `tools/check_cli_contract.py`: targeted regression fixtures for global-cli provider, stale `.loom/bin`, malformed provider fail-closed behavior, and repo-local compatibility.
- `tools/governance_surface.py`, `src/skills/shared/scripts/governance_surface.py`, `skills/shared/scripts/governance_surface.py`, generated skill runtime copies, and `examples/new-project`: command-prefix and fixture parity.

## Non-Goals

- #1243/#1244 migration repair/fixtures.
- #1245/#1246 docs/release closeout execution.
- Unrelated review-head gate changes in `src/skills/shared/scripts/loom_flow.py`.

## Validation Contract

- Required local evidence: `git diff --check`, targeted global-cli smoke, py_compile, skills check, demo bootstrap check, suite validate, suite carrier validate, flow build, runtime evidence, fact-chain, PR gate, hosted checks, and release judgment.
- Full `tools/check_cli_contract.py` failure is classified as `environment/carrier-state failure` when it consumes terminal self-repo carrier `WI-1311` or uncommitted carrier purity; that classification is not a global-cli provider behavior failure.
- Release impact must be recorded in PR evidence because CLI/runtime/workflow behavior is user-visible; release execution remains outside this batch.
