# WI-571 Implementation Contract

## Ownership

- `docs/methodology/harness/policy-read-surface.md` owns the stable approval/sandbox policy read contract.
- `docs/adoption/repo-companion-contract.md` owns the `policy_locators` declaration boundary.
- `docs/adoption/repo-interop-contract.md` owns the rule that retained host action results do not move into `repo-interface.json`.
- `src/skills/shared/scripts/governance_surface.py` owns policy declaration parsing and derived `policy_readiness`.
- `src/skills/shared/scripts/loom_flow.py` owns surface-specific policy blocking and advisory behavior.
- `src/skills/shared/scripts/loom_status.py` owns top-level status exposure.
- `src/skills/shared/scripts/loom_check.py` owns missing/conflict/unsafe policy fixtures and contract validation.

## Guardrails

- Do not implement host permission requests or sandbox mutation.
- Do not introduce Codex-specific approval/sandbox names into the stable Loom vocabulary.
- Do not treat optional/advisory policy risk as core failure.
- Do not let policy evidence replace authored recovery state, review records, merge-ready evidence, or retained host action results.

