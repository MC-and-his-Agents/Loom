# WI-1150 Plan

## Suite Contract

- Suite path consumed: minimal
- Full suite artifact skip is consumed from .loom/specs/WI-1150/spec.md.

## Implementation Plan

1. Add source `loom_check` helpers that author stale evidence and host conflict negative fixtures inside isolated fixture repositories.
2. Assert `suite evidence validate` blocks stale HEAD / PR head / validation summary bindings with `stale_evidence`, taxonomy, and remediation.
3. Assert `suite carrier validate` blocks Project / issue / carrier host conflicts with `carrier_truth_conflict`, taxonomy, recognized host signals, and remediation.
4. Run `tools/skills_surface.py generate` so generated runtime surfaces match `src/skills`.
5. Record #1150 Work Item, progress, spec, evidence, review, and status surface.

## Validation Commands

- Scenario mapping:
  - S1 -> automated validation evidence: source-self stale evidence fixture and `suite evidence validate` block payload.
  - S2 -> automated validation evidence: source-self host conflict fixture and `suite carrier validate` block payload.
- Acceptance mapping:
  - AC-1 -> test evidence: stale HEAD / PR head / validation summary fixture assertions in `src/skills/shared/scripts/loom_check.py`.
  - AC-2 -> test evidence: Project / issue / checklist / PR host conflict fixture assertions in `src/skills/shared/scripts/loom_check.py`.
  - AC-3 -> structural check: taxonomy and remediation assertions in stale evidence and host conflict helper functions.
  - AC-4 -> structural check: `tools/skills_surface.py check`.
  - AC-5 -> manual evidence: implementation diff stays limited to fixture and generated surface sync; no production reconciliation behavior is changed.
- `git diff --check`
- focused `rg` for stale evidence / host conflict fixture ownership and forbidden spec-kit surfaces
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_check.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface source-self-fixture .`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .`
- root self-governance dry checks: `.loom/bin/loom_init.py verify`, `.loom/bin/loom_flow.py governance-profile status`, `.loom/bin/loom_flow.py runtime-parity validate`, `.loom/bin/loom_flow.py adopt verify --item WI-1150`, `.loom/bin/loom_flow.py carrier refresh --dry-run`, `.loom/bin/loom_flow.py shadow-parity --surface all --blocking`

## Guardrails

- Keep changes in fixtures and generated runtime sync.
- Do not implement new reconciliation write behavior.
- Do not replace Work Item, review, merge-ready, closeout, or source truth with CLI output.
