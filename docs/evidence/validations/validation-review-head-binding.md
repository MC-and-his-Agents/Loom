# Validation: Review Head Binding

## Goal

验证 `loom-review/v1` 的 head binding 能区分 review artifact freshness、carrier-only refresh、implementation drift 与 mixed stale drift。

## Semantics

- `fresh`: review artifact recorded against current `HEAD`
- `carrier-only`: current `HEAD` differs only by allowed Loom carrier paths after review
- `implementation-drift-only`: implementation files changed after review and must not be treated as fresh
- `stale`: mixed or otherwise unsafe drift after review

This contract batch also freezes the semantic approval boundary consumed by PR-facing gates:

- `semantic_review_disposition` is the authored merge-facing review disposition carried by the single review record
- only `required`、`passed`、`not_applicable`、`waived` are consumable states
- `not_applicable` and `waived` require `reason`、`change_class`、`substitute_validation`、`authority`
- repo companion、guardian、CI success, and GitHub review comments remain evidence-only and do not replace the generic Loom disposition boundary

## Validation Entry

```bash
python3 tools/loom_check.py .
```

## Runtime Evidence

`loom_check` installed pre-merge fixture covers:

- positive merge checkpoint exposes `fresh`
- post-review carrier refresh remains passable and exposes `carrier-only`
- post-review README implementation drift blocks merge and exposes `implementation-drift-only`

## Result

Pass. Merge-ready / checkpoint merge now consume review head binding semantics instead of treating all head drift as a generic stale state.
The same contract keeps semantic review approval bound to the current PR head and prevents repo companion or guardian signals from silently substituting for Loom-authored disposition truth.
