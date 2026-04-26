# Validation: Review Head Binding

## Goal

验证 `loom-review/v1` 的 head binding 能区分 review artifact freshness、carrier-only refresh、implementation drift 与 mixed stale drift。

## Semantics

- `fresh`: review artifact recorded against current `HEAD`
- `carrier-only`: current `HEAD` differs only by allowed Loom carrier paths after review
- `implementation-drift-only`: implementation files changed after review and must not be treated as fresh
- `stale`: mixed or otherwise unsafe drift after review

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
