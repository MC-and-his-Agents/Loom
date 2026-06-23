# WI-1736 Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1736 is a bounded runtime readback fix for carrier refresh apply semantics. consumer boundary: suite validate, review, PR gate, controlled merge, and closeout may consume this minimal spec, plan, implementation contract, evidence map, and focused validation output. recheck condition: require full suite artifacts if scope expands into ship repair-chain orchestration, review stale policy, closeout policy, or release behavior.
- Work Item / FR locator: issue #1736 under FR #1734.
- Scenario locators: S1, S2.
- Acceptance locators: A1, A2, A3.
- Spec locator: .loom/specs/WI-1736/spec.md
- Provenance: GitHub issue #1736.
- Freshness rule: Recheck if carrier refresh apply semantics, generated runtime copies, or plugin payload metadata change.

## Goal

Make `carrier refresh --apply` read back the post-apply state so users do not see stale `refresh_needed` output after a successful write.

## Scope

- In scope: recompute carrier refresh state after apply, report fixed and remaining refresh entries, update generated runtime copies, keep demo bootstrap fixture aligned, and cover the behavior with focused regression checks.
- Out of scope: `loom ship` repair-chain orchestration, review stale classification, closeout policy expansion, release publishing, and merge permission changes.

## Scenarios

### S1: Apply Output Reflects Post-Apply State

Given carrier refresh finds stale generated carrier evidence
When the operator runs refresh in apply/write mode
Then the command reports the entries fixed by the write and the remaining refresh state after readback.

### S2: Dry Run Remains Non-Mutating

Given carrier refresh runs in dry-run mode
When stale generated carrier evidence is detected
Then the command reports refresh-needed entries without mutating files or pretending they were fixed.

## Acceptance Criteria

- [ ] A1: apply/write mode recomputes readback after mutation.
- [ ] A2: output distinguishes fixed entries from remaining refresh entries.
- [ ] A3: dry-run behavior and generated runtime mirrors remain aligned.
