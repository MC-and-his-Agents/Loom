# WI-1243 Spec

## Suite Contract

- Suite path: minimal
- Work Item / FR locator: #1243
- Path decision provenance: #1243 implements the next global-cli runtime provider follow-up batch by turning retained `.loom/bin` residue into deterministic repair/upgrade planning without authorizing mutating apply.
- Full-suite-artifacts not_applicable: rationale: the batch changes bounded CLI/runtime planning behavior and scoped docs/carriers only; consumer boundary: suite validate, review, PR gate, and merge-ready consume the minimal suite plus targeted CLI contract evidence and local validation; recheck condition: require full suite artifacts if scope expands into mutating repair apply, shared carrier lanes, release execution, or downstream repo writes.

## Scope

Implement deterministic non-mutating migration planning for repositories that already declare `runtime_provider: global-cli` but still retain `.loom/bin`.

## Scenarios

- S1: `loom repair plan` emits a runtime-carrier migration action that is separate from skills/plugin payload migration.
- S2: Eligible retained `.loom/bin` repositories receive proposal-only deletion semantics that require explicit apply/confirmation.
- S3: Repositories whose repo-local gate carriers still reference `.loom/bin` receive exact blocker locators and no safe deletion proposal.
- S4: `loom upgrade-plan` preserves the same runtime-carrier migration/blocker semantics as `loom repair plan`.
- S5: Installed-state and migration docs describe retained `.loom/bin` as runtime-carrier residue, not current provider proof or plugin payload drift.

## Acceptance Criteria

- AC-1: `tools/loom.py` emits deterministic runtime-carrier migration actions for `global-cli` installed-state with retained `.loom/bin`.
- AC-2: Deletion of retained `.loom/bin` remains non-mutating and explicit-confirmation-only.
- AC-3: Exact repo-local gate blocker paths are reported when shared or repo-local carriers still point to `.loom/bin`.
- AC-4: `tools/check_cli_contract.py` covers both the eligible and blocked retained-`.loom/bin` fixtures.
- AC-5: Adoption docs record the separation between runtime-carrier migration and skills/plugin payload migration.
