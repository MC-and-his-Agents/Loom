# WI-1031 Plan

## Implementation Target

Update only the `loom-story` skill boundary so #1032 can later consume a stable story readiness contract from the spec-suite entry path.

## Steps

1. Update `src/skills/loom-story/SKILL.md` with the confirmed / pending / revision-requested / not_applicable vocabulary.
2. Update `src/skills/loom-story/references/input-signals.md` so missing context returns `pending`, user revision returns `revision-requested`, and non-business work returns rationale-backed `not_applicable`.
3. Update `src/skills/loom-story/references/output-contract.md` with fail-closed delivery consumption rules.
4. Regenerate checked-in `skills/` surfaces with `python3 tools/skills_surface.py generate`.
5. Refresh WI-1031 carriers and review evidence for PR merge gate consumption.
6. Validate with focused `rg`, skills surface checks, contract-only `loom_check`, version/release checks, and GitHub reconciliation.

## Constraints

- Do not change user-story scaffold fields owned by #1030.
- Do not change spec-suite entry rules owned by #1032.
- Do not change delivery planning, task carrier, consistency analysis, gate-chain, or CLI surfaces.
- Keep #1015 open until #1032 is complete and the FR can be closed.

## Validation

- `git diff --check`
- `python3 tools/skills_surface.py check`
- `rg -n "needs-shaping|ready \\| needs-shaping|not-applicable" src/skills/loom-story skills/loom-story`
- `rg -n "loom-story|pending|revision-requested|not_applicable|formal spec" skills src docs .loom`
- `rg -n "技术方案|测试策略|Business Confirmation|业务语义" skills src docs .loom`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_release_surface.py`
- `python3 tools/loom_flow.py reconciliation audit --target . --issue 1031 --project 4`

## Entry Conditions

- #1029 is closed and Project Done.
- #1030 is closed and Project Done.
- #1031 is active in `/Users/mc/dev/Loom-1031-loom-story-boundary`.
