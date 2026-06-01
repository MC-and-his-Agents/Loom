# WI-876 Plan

- Suite path: minimal

1. Update repo companion contract copies with the stable PR metadata machine carrier fields and allowed carrier forms.
2. Update PR template references with the human layer / machine carrier boundary.
3. Regenerate checked-in skills surface from `src/skills`.
4. Validate with whitespace, focused text, skills surface, and source contract-only checks.
5. Record WI-876 workspace, PR, head SHA, validation, merge, closeout, and Project truth.

## Validation Mapping

- Acceptance 1 -> focused `rg` for `carrier_id`, `repo_specific_field_set`, `source_range_or_hash`, and companion contract sections.
- Acceptance 2 -> focused `rg` for PR template machine carrier guidance.
- Acceptance 3 -> focused `rg` for parser/CLI output boundary text.
- Acceptance 4 -> `python3 tools/skills_surface.py check`.
- General repository contract integrity -> `python3 tools/loom_check.py --profile source --source-surface contract-only .`.
