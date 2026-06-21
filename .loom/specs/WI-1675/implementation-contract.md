# WI-1675 Implementation Contract

## Contract

- Change class: docs_only
- Owned files: `README.md`, `README.zh-CN.md`, WI-1675 Loom carriers.
- Runtime behavior: unchanged.
- Install behavior: unchanged.
- Release behavior: unchanged.

## Consumer Boundary

- Review, PR gate, hosted checks, merge-ready, controlled merge, and closeout consume this contract only as a documentation-scope boundary.
- Recheck if the PR changes runtime code, installer behavior, package/release surfaces, legacy migration contracts, host mutation behavior, permissions, or downstream adoption behavior.

## Validation Contract

- `git diff --check`
- README badge/body link scan.
- Chinese README token scan.
- English/Chinese heading and maintainer-link readback.
- `python3 tools/loom.py fact-chain --target . --json`
- `python3 tools/loom.py workspace check --target . --branch work/1675-readme-install-clarity --item WI-1675 --json`
- `python3 tools/loom.py suite validate --target . --item WI-1675 --json`
