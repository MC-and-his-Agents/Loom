# WI-1052 Plan

## Implementation Strategy

1. Read #1052, #1012/#1020 closeout, #1014-#1020 completion evidence, current full spec suite contracts, task carrier, evidence-map, consistency-analysis, gate-chain, GitHub profile, route matrix, scenario skills, and current CLI docs.
2. Add a docs/source planning record under `docs/methodology/harness/`.
3. Link the planning record from the harness README and the CLI command matrix as planned-only names.
4. Add repo-local #1052 fact-chain and review records so PR gate consumes the current Work Item instead of stale #1051 evidence.

## Validation Strategy

| Acceptance | Validation |
| --- | --- |
| AC-1052-1 | Focused `rg` over behavior class terms in the planning document. |
| AC-1052-2 | Focused `rg` over planned suite command names in docs and non-Markdown implementation surfaces. |
| AC-1052-3 | Focused `rg` over JSON and failure taxonomy terms; `python3 tools/check_cli_contract.py`. |
| AC-1052-4 | Focused `rg` over `doctor`, `verify`, and scenario skill terms. |
| AC-1052-5 | Review `Implementation Backlog` section in the planning document. |
| AC-1052-6 | `rg` over non-Markdown code paths for planned suite command names returns no implementation hits. |

## Commands Run

- `git diff --check`
- focused `rg` over CLI/suite/fail-closed/spec-kit terms
- non-Markdown `rg` for planned suite command names
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
- `python3 tools/check_cli_contract.py`
- `python3 tools/check_release_surface.py`
- `python3 tools/version_surface_check.py`

## Risks

- If planned names are added to `loom help --json` before implementation, the command matrix would imply implementation that does not exist. This PR keeps them in a planned-only section.
- If scenario skills consume the planning record as runtime truth, they would bypass source contracts. The planning record states that scenario skills must consume CLI JSON only after later implementation.
