# WI-957 Plan

- Suite path consumed: minimal
- Consumes: .loom/specs/WI-957/spec.md; issues #957, #876, #877, #874, #875, and #969.
- Produces: pre-review readiness/cost guard runtime, docs contract, fixtures, and validation evidence.

## Implementation Goal

Extend existing `flow pre-review` with a fail-closed readiness/cost guard for expensive semantic review, without creating the #1107 full spec suite CLI tree or changing frozen truth contracts.

## Phases

1. Read #957, #969, previous PR metadata work, and pre-review/review/merge-ready/closeout contracts.
2. Add guard payload to `src/skills/shared/scripts/loom_flow.py` and wire it into `flow pre-review`.
3. Update pre-review skill output contract and runtime fixture checks.
4. Sync generated skills/runtime surfaces from `src/skills`.
5. Validate with whitespace, focused rg, skills surface, contract-only loom_check, CLI contract, suite checks, PR gate, controlled merge, reconciliation, and closeout checks as appropriate.

## Constraints

- Do not implement #1107 full spec suite CLI tree.
- Do not rewrite frozen core contracts.
- Do not make parser/CLI output authoritative Work Item, review, merge-ready, closeout, or docs/source truth.
- Keep generated skills synchronized with source runtime.
- Treat #969 as consumed model/profile proof only; do not own model policy.

## Validation Mapping

- A1 -> test evidence: `python3 tools/loom_check.py --profile source --source-surface contract-only .` step-order assertion.
- A2 -> test evidence: `python3 tools/check_cli_contract.py` and contract-only `loom_check`.
- A3 -> behavior evidence: focused smoke with PR payload fixture or direct `flow pre-review` JSON showing `checkout_head_drift`.
- A4 -> structural evidence: focused rg for `source_issue": "#969"`, `pr_metadata_preflight`, `closeout_preview`, and `post_review_carrier_policy`.
- A5 -> structural evidence: focused rg for deterministic validation tokens and generated skills/release/package token classification.

## Fresh Verification Evidence

- Pending until implementation stabilizes.
