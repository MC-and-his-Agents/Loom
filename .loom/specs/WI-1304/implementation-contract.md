# WI-1304 Implementation Contract

## Contract

WI-1304 changes only governance maturity detection. A Work Item may satisfy the formal spec gate for maturity through either:

- the existing full/minimal path with `spec.md` and `plan.md`, or
- a docs-only suite decision in `spec.md` plus an approved `.loom/reviews/<item>.spec.json`.

This contract does not change suite validation, spec review recording, implementation review recording, PR head binding, CI checks, fact-chain requirements, or closeout requirements.

## Write Scope

- `skills/shared/scripts/governance_surface.py`
- `src/skills/shared/scripts/governance_surface.py`
- `skills/loom-*/.loom-runtime/shared/scripts/governance_surface.py`
- `.loom/bin/governance_surface.py`
- `.loom/bootstrap/manifest.json`
- `.loom/bootstrap/init-result.json`
- WI-1304 carriers, suite files, review files, status surface, and shadow hash surfaces

## Required Behavior

- Detect a suite path decision from the active Work Item spec.
- Detect an approved spec review record for the active Work Item.
- Treat `plan_path` maturity as satisfied when an approved docs-only suite decision is present.
- Keep `spec_gate` dependent on regular review, spec path, and either plan path or the approved docs-only suite decision.
- Keep runtime manifest and init-result hashes aligned with the installed runtime copy.

## Forbidden Behavior

- Do not mark invalid suite rationale as valid.
- Do not let a missing spec review satisfy maturity.
- Do not change PR gate review-head semantics.
- Do not move A-D contract PR content into #1304.
- Do not relax hosted CI or closeout requirements.

## Validation Binding

- `git diff --check`
- `python3 tools/loom.py suite validate --target . --item WI-1304 --json`
- `python3 .loom/bin/loom_init.py verify --target .`
- `python3 .loom/bin/loom_flow.py fact-chain --target .`
- `python3 .loom/bin/loom_flow.py shadow-parity --target .`
- `python3 .loom/bin/loom_flow.py carrier refresh --target . --dry-run`
- `python3 .loom/bin/loom_flow.py governance-profile status --target /Users/mc/dev/Loom-worktrees/1264-regression-surface-contract --host github`
- `python3 tools/loom_check.py --profile source --source-surface bootstrap-regression .`
