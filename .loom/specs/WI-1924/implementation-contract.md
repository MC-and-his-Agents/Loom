# WI-1924 Implementation Contract

- Suite path: minimal

## Ownership

- Owns closeout gate PR-role selection for retained merge-ready evidence.
- Owns focused governance-closeout contract coverage for carrier/final closeout PRs whose heads differ from the implementation PR head.
- Owns synchronized runtime copies of `loom_flow.py` and the focused checker update.

## Contract

- For `carrier_sync_pr` and `final_closeout_pr`, when an `implementation_pr` role is provided, retained merge-ready execution evidence is validated against the implementation PR head.
- Host checks and merge backlink evidence remain validated against the current carrier/final closeout PR head.
- Without an implementation PR role, existing current-PR behavior remains unchanged.

## Non-Goals

- Do not change workstation registry CLI behavior.
- Do not change WI-1895 implementation semantics.
- Do not change release judgment, GitHub merge mechanics, or workstation upgrade orchestration.

## Validation Binding

- A1: `python3 tools/check_cli_contract.py --surface governance-closeout` and the live WI-1895 carrier-sync closeout status readback prove split-head merge-ready consumption.
- A2: `python3 tools/check_cli_contract.py --surface governance-closeout` preserves implementation PR and legacy fallback behavior.
- A3: `python3 tools/check_cli_contract.py --surface governance-closeout`, `python3 tools/check_cli_contract.py --surface closeout-wrapper`, generated-tree drift, py compile, and diff hygiene prove the focused contract and copy sync.
