# WI-1127 Implementation Contract

## Inputs Consumed

- Parent FR: #1126
- Work Item: #1127
- Contracts:
  - `docs/methodology/harness/full-spec-suite-cli-surface.md`
  - `docs/methodology/templates/evidence-map.md`
  - `docs/methodology/templates/spec-suite.md`
  - `docs/methodology/harness/task-carrier-contract.md`
  - `docs/methodology/harness/gate-chain.md`

## Owned Changes

- `tools/loom.py`
- `tools/check_cli_contract.py`
- `docs/methodology/harness/cli-command-matrix.md`
- `docs/methodology/harness/full-spec-suite-cli-surface.md`
- WI-1127 `.loom/` carrier files
- `.loom/progress/WI-1125.md` terminal recovery update for the already-merged previous Work Item

## Non-Goals

- Do not implement `suite evidence scaffold`.
- Do not implement suite carrier inspect/validate.
- Do not wire evidence validation into merge-ready or closeout gates.
- Do not write review, merge-ready, closeout, host, Project, `/speckit.*`, or `.specify/` truth from CLI evidence commands.
- Do not rewrite frozen #1014-#1020 core contracts.

## Verification

- `git diff --check`
- Focused `rg` for `suite evidence`, `missing_evidence_map`, `stale_evidence`, `missing_fresh_verification_evidence`, `/speckit`, and `.specify`
- `python3 tools/check_cli_contract.py`
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
- Additional source self-governance checks before PR gate
