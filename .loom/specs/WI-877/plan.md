# WI-877 Plan

- Suite path: minimal

1. Read the #876 machine carrier contract and current parser/gate implementation.
2. Extend PR metadata parser preflight to include `pre_review`, `review`, and `merge_ready` declared surfaces.
3. Wire preflight evidence into pre-review and review flow outputs without replacing authored governance truth.
4. Add diagnostics for raw excerpt hash, declared source locator/hash, expected schema/parser version, missing fields, parse error, repair hint, and fallback target.
5. Update focused contract fixtures and generated skills runtime copies.
6. Validate with whitespace, focused rg, skills surface, source contract-only loom_check, CLI contract, suite carrier/evidence checks, PR gate, controlled merge, reconciliation, and closeout checks as appropriate.

## Validation Mapping

- Acceptance 1 -> focused `rg` for `pre_review`, parser surface choices, and validator allowed surfaces.
- Acceptance 2 -> focused `rg` for `pr-metadata-preflight` steps in `flow pre-review`, `flow review`, and `flow merge-ready`.
- Acceptance 3 -> `python3 tools/loom_check.py --profile source --source-surface contract-only .`.
- Acceptance 4 -> focused `rg` for `raw_excerpt_sha256`, `source_range_or_hash`, `expected_schema`, and `fallback_to`.
- Acceptance 5 -> focused `rg` for parser truth-boundary docs and unchanged Work Item/review/merge-ready/closeout authority.
