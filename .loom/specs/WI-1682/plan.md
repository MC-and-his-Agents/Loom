# WI-1682 Plan

## Implementation Plan

- Freeze governance intensity classification inputs and outputs in `docs/methodology/harness/tiered-gate-consumption-contract.md`.
- Freeze Work Item / issue / PR / branch / head binding priority and repairability in the same contract and `docs/methodology/harness/pr-merge-gate.md`.
- Add the binding priority and safe repair shape to `.loom/companion/repo-interface.json`.
- Freeze closeout policy decisions in `docs/methodology/harness/closeout-gate.md` and mirror the closeout reference copies.
- Add focused contract assertions in `tools/check_cli_contract.py`.

## Validation Plan

- `git diff --check`
- `python3 -m json.tool .loom/companion/repo-interface.json`
- `python3 tools/check_cli_contract.py --surface pr-metadata`
- `python3 tools/check_cli_contract.py --surface closeout-wrapper`
- `python3 tools/check_cli_contract.py --surface merge-wrapper`
- `python3 tools/check_cli_contract.py --surface controlled-merge`
- `python3 tools/loom.py suite validate --target . --item WI-1682 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1682 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1682 --json`

## Boundaries

- This plan does not implement `loom ship`.
- This plan does not add controlled-merge post-merge closeout chaining.
- This plan does not publish v0.18.0; release closeout remains owned by #1696.

- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1682 is a bounded contract-foundation PR with issue-scoped acceptance and focused CLI contract validation. consumer boundary: suite validate, review, PR gate, merge-ready, controlled merge, and issue closeout may consume this minimal suite plus focused validation evidence. recheck condition: require full suite artifacts if scope expands into runtime command behavior, host mutation semantics, public CLI/API compatibility changes, release packaging, hosted workflow enforcement, or broader milestone #15 implementation.
