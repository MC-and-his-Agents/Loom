# WI-875 Plan

- Suite path consumed: minimal
- Consumes: .loom/specs/WI-875/spec.md; issues #875, #876, #877, #874.
- Produces: focused parser fixture coverage and fresh validation evidence.

## Implementation Goal

Deliver focused regression coverage for PR metadata Markdown drift and legacy migration, plus a minimal parser diagnostic for unsupported parser versions. Defer #957 readiness/cost guard and any full-suite CLI tree work.

## Phases

1. Read #875 scope and current #874/#877 parser/body-file implementation.
2. Add minimal parser support-version validation while preserving documented `repo-parser/v1` compatibility.
3. Extend `check_pr_metadata_machine_preflight_contract` with Markdown drift, negative carrier, readback mismatch, and legacy migration fixtures.
4. Regenerate checked-in skills runtime surfaces from `src/skills`.
5. Validate with whitespace, focused rg, skills surface, contract-only loom_check, CLI contract, suite checks, PR gate, controlled merge, reconciliation, and closeout checks as appropriate.

## Constraints

- Do not change frozen PR metadata carrier schema version.
- Do not make parser/CLI output authoritative Work Item, review, merge-ready, closeout, or docs/source truth.
- Do not implement #957 pre-review readiness/cost guard.
- Keep generated skills synchronized with source runtime.

## Validation Mapping

- A1 -> test evidence: `python3 tools/loom_check.py --profile source --source-surface contract-only .` plus focused rg for readback/hash drift fixtures.
- A2 -> test evidence: direct unsupported parser-version smoke plus contract-only `loom_check`.
- A3 -> test evidence: contract-only `loom_check` dual_read/advisory legacy fixture.
- A4 -> structural check: focused rg for `raw_excerpt_sha256`, `expected_format`, `unsupported parser_version`, and `gh_pr_edit_body_file_readback`.
- A5 -> structural check: focused rg and PR summary boundary statement.

## Fresh Verification Evidence

- `git diff --check`: pass on 2026-06-01.
- Focused `rg` for parser-version, Markdown drift, legacy, hash, and fallback anchors: pass on 2026-06-01.
- `python3 tools/skills_surface.py check`: pass on 2026-06-01.
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`: pass on 2026-06-01.
- `python3 tools/check_cli_contract.py`: pass on 2026-06-01.
