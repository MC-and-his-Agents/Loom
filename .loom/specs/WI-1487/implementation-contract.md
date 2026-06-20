# WI-1487 Implementation Contract

## Scope

- Document thread rotation triggers and the minimum handoff package contract.
- Update source, generated, and plugin mirror documentation for the recovery model and handoff output contract.

## Contract

- Thread rotation is required when context budget risk, tool output pollution, rising handoff/resume cost, or executor change would make continuation in the current thread unsafe or inefficient.
- The minimum handoff package includes item id, branch, PR, `head_sha`, optional `run_id`, fact carrier locators, bounded summary, artifact locator, current stop, next step, blockers, and validation summary or locator.
- New threads consume the bounded summary and authoritative locators first.
- Old full conversation turns are read only for explicit audit or targeted clarification.
- Full diagnostics are explicit artifacts; they are diagnostic evidence, not authoritative truth carriers.
- Full diagnostics do not live in repo-local plugin/runtime/skills installation paths.

## Non-Goals

- Do not implement a scheduler.
- Do not update command examples owned by #1486.
- Do not change CLI output behavior owned by #1483/#1484.
- Do not restore repo-local plugin/runtime/skills installation paths, single-skill packages, or old installer compatibility.

## Validation

- `git diff --check`
- `python3 tools/py_compile_clean.py tools/loom.py test/output_envelope_test.py`
- `python3 tools/loom.py fact-chain --target . --json`
- `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`
- `python3 tools/skills_surface.py check --surface generated-tree-drift`
- `python3 tools/loom.py suite validate --target . --item WI-1487 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1487 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1487 --json`
