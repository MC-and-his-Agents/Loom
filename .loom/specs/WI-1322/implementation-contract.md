# Implementation Contract

## Ownership

- `src/skills/shared/scripts/loom_flow.py`, `skills/shared/scripts/loom_flow.py`, generated skill `.loom-runtime/shared/scripts/loom_flow.py` copies, and `.loom/bin/loom_flow.py`: docs-governance lite metadata/preflight/pr-gate consumption behavior.
- `tools/check_cli_contract.py`: targeted positive and fail-closed fixtures for docs-governance lite metadata, suite validate, review-surface metadata preflight, and pr-gate behavior.
- `docs/methodology/harness/tiered-gate-consumption-contract.md`: minimal clarification that review/pre-review preflight consumes the single declared merge-ready metadata carrier.
- `.loom/work-items/WI-1322.md`, `.loom/progress/WI-1322.md`, `.loom/status/current.md`, `.loom/specs/WI-1322/*`, and `.loom/reviews/WI-1322*.json`: WI-1322 carrier, suite, evidence, and review truth.

## Non-Goals

- Do not implement #1323 full escalation and misuse fixture matrix.
- Do not implement #1324 parent/final closeout.
- Do not change unrelated runtime providers, review engine selection, controlled merge strategy, hosted release strategy, or external-visible behavior.
- Do not treat all docs-only changes as docs-governance lite.
- Do not let docs-governance lite skip fact-chain, current-head review, PR metadata/readback, release/no-release judgment, PR gate, hosted checks, controlled merge, or closeout.

## Required Behavior

- `governance_intensity=light` is accepted only for `change_class=docs_governance`, `suite_path=not_applicable`, `review_requirement=current_head_review_required`, and `release_judgment=no_release`.
- A `suite_path=not_applicable` metadata carrier must match a repo suite path decision that is present and only `not_applicable`.
- Missing `suite_not_applicable` rationale fields, unknown governance enum values, high-risk classes, deferred release judgment, PR body/head mismatch, and stale review remain blocking.
- A single `surface: merge_ready` machine carrier may be consumed by `pre_review` / `review` metadata preflight when the repo contract declares those `required_before` surfaces.

## Validation

- `python3 tools/check_cli_contract.py --surface aggregate`
- `git diff --check`
- `python3 tools/py_compile_clean.py tools/check_cli_contract.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py`
- `python3 tools/skills_surface.py check`
- `python3 .loom/bin/loom_init.py fact-chain --target .`
- `python3 tools/loom.py suite validate --target . --item WI-1322 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1322 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1322 --json`
