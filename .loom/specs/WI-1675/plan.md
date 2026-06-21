# WI-1675 Plan

## Implementation Steps

1. Add Zread and DeepWiki badges to both README versions.
2. Replace the opening README copy with product value, problem, architecture, and workflow sections.
3. Replace the install section with a short copyable agent prompt and step-by-step supported commands.
4. Remove new-user legacy compatibility wording from README install flow.
5. Align English and Chinese section/link structure, and keep Chinese prose mostly Chinese.
6. Record minimal WI-1675 Loom carriers for fact-chain, workspace, PR, and closeout consumption.

## Validation

- `git diff --check`
- README badge/body link scan: `rg -n "zread\\.ai|deepwiki\\.com" README.md README.zh-CN.md`
- Chinese README token scan: `rg -n "[A-Za-z][A-Za-z0-9_-]*" README.zh-CN.md`
- English/Chinese heading and maintainer-link readback: `rg -n "^## |^# |^- " README.md README.zh-CN.md`
- `python3 tools/loom.py fact-chain --target . --json`
- `python3 tools/loom.py workspace check --target . --branch work/1675-readme-install-clarity --item WI-1675 --json`
- `python3 tools/loom.py suite validate --target . --item WI-1675 --json`
- PR metadata preflight/readback, hosted checks, PR gate, controlled merge, and issue #1675 closeout readback.

## Dependencies

- Issue #1675 is the source Work Item.
- No hard dependency on runtime, release, package, or installer implementation work.

## Scope Guard

- Do not touch runtime behavior, installer implementation, package release surfaces, legacy migration contracts, host mutation behavior, permissions, external-visible execution, or downstream repository adoption.
