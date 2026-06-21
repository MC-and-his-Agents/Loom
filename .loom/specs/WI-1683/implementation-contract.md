# WI-1683 Implementation Contract

## Runtime Contract

- Add `governance_intensity_gate_payload` as the generic PR gate classifier for the existing governance intensity metadata carrier.
- Keep `docs_governance_lite_gate_payload` as a compatibility payload for existing docs-governance lite consumers.
- Allow `light` only for low-risk `docs_only`, `docs_governance`, and bounded `fixture` metadata.
- Require `docs_only` and `docs_governance` light changes to use `suite_path: not_applicable` with the repo suite decision marker.
- Require bounded `fixture` light changes to use `suite_path: minimal`.
- Keep `runtime`, `release`, `external_action`, and `mixed` as upgrade-required classes for attempted light changes.
- Keep `contract` outside the light allowlist unless a later Work Item defines a narrower contract subclass.

## Output Contract

- The generic gate returns `schema_version: loom-governance-intensity-gate/v1`.
- The payload exposes declared and effective intensity, effective suite path, upgrade reasons, consumed locators, and non-skippable gates.
- The authority boundary must state that intensity classification does not replace fact-chain, current-head review, PR metadata readback, hosted checks, PR gate, release judgment, controlled merge, or post-merge closeout.
- The legacy docs-governance lite payload remains available as `docs_governance_lite_gate` and is `not_applicable` for other governance metadata classes.

## Test Contract

- Existing docs-governance lite positive and negative PR gate fixtures continue to pass or block as before.
- New metadata preflight fixtures prove that `light/docs_only` with `not_applicable` and `light/fixture` with `minimal` pass.
- Negative metadata preflight fixtures prove that `light/runtime`, `light/release`, and `light/contract` still block.
- `python3 tools/check_cli_contract.py --surface pr-metadata` is the focused contract check for this Work Item.
