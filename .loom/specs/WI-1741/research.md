# WI-1741 Research

## Findings

- `loom ship` is implemented in `tools/loom.py` and already owns PR metadata, PR gate, controlled merge, and closeout policy sequencing.
- `loom_check.py` already exposes targetable source surfaces such as `contract-only`, `source-self-fixture`, `daily-execution-cli-full`, and `distribution-regression`.
- Validation profile selection should be a ship diagnostic, not a governance intensity or closeout policy.
- Changed paths can be read from GitHub PR files and fall back to local git diff when the host readback is unavailable.

## Decision

Implement a small selector in `tools/loom.py` that returns `light`, `standard`, `full`, or `release`, plus source surface and validation command hints.

## Boundaries

- Do not rewrite `loom_check.py`.
- Do not execute validation commands from `loom ship`.
- Do not merge this with #1739 repair-chain behavior.
