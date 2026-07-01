# Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1844 is a bounded release aftercare wrapper with focused CLI contract coverage and dogfood dry-run evidence. consumer boundary: suite validate, review, PR gate, merge-ready, controlled merge, issue closeout, and release/no-release decision may consume this minimal suite plus focused validation evidence. recheck condition: require full suite artifacts if scope expands into publishing, republishing, GitHub Release/npm mutation, automatic merge, multi-repo orchestration, new carrier/DSL, or release policy changes.
- Consumes:
  - Work Item / FR locator: #1844
  - Story Readiness confirmed locator, blocking locator, or skip rationale: skip rationale: #1844 issue tree is the scoped product source; require story readiness if the command expands into a broader release workflow or external host mutation.
  - Story scenario locator, or skip rationale: #1844 / #1842 / #1843 / #1846
  - Story Business Confirmation confirmed locator, blocking locator, or skip rationale: skip rationale: the issue tree already defines the product boundary and no separate business semantic carrier is needed; require business confirmation if the work changes release policy, package publication semantics, or downstream repository governance guarantees.
- Produces:
  - Scenario ids / locators: S1, S2
  - Acceptance ids / locators: A1-A5
  - Behavior evidence expectation: CLI contract and dogfood dry-run evidence.
- Locator:
  - Spec locator: .loom/specs/WI-1844/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: #1844 and milestone #21.
  - Freshness rule: rerun release-readback contract and dogfood dry-run after CLI or carrier wrapper changes.

## Goal

Provide a product CLI entry for release aftercare:
`loom release closeout-sync --version <version> --item <item> --pr <release-pr> [--apply]`.
The command helps any Loom-adopted repository terminalize repo carriers after release artifacts are already published.

## Scope

- In scope: release readback gating, merged release PR readback, `carrier closeout-sync`, recovery/status writeback, closeout and merge-ready shadow refresh, and post-commit PR metadata/gate next commands.
- Out of scope: publishing, republishing, editing GitHub Releases, npm writes, automatic merge, multi-repo batch mode, new DSL, new carrier, and Loom-repo-specific release logic.

## Key Scenarios

### Scenario S1

Given published release artifacts and a merged release PR

When an operator runs `loom release closeout-sync` in dry-run mode

Then Loom emits a non-mutating terminal carrier plan and next commands for PR metadata, gate, merge, and post-merge release readback.

### Scenario S2

Given release artifacts are missing, drifted, or the release PR does not match the release target commit

When an operator runs `loom release closeout-sync --apply`

Then Loom fails closed before any repo carrier mutation.

## Behavior Evidence

- Story scenario mapping: S1/S2 from #1844.
- Story readiness locator or skip rationale: skip rationale: #1844 issue tree is scoped and current; require a story readiness carrier if the scope expands beyond release carrier synchronization.
- Story business confirmation locator or skip rationale: skip rationale: this change reduces manual aftercare steps without changing release authority or product policy; require business confirmation if release publishing, npm, GitHub Release mutation, auto-merge, or governance guarantee semantics change.
- Scenario coverage:
  - S1 -> expected behavior evidence locator: `python3 tools/check_cli_contract.py --surface release-readback`.
  - S2 -> expected behavior evidence locator: `python3 tools/check_cli_contract.py --surface release-readback`.
- Expected evidence locator: .loom/progress/WI-1844.md
- Freshness rule: evidence must be regenerated after CLI wrapper or carrier refresh behavior changes.
- Execution ledger acceptance locator: .loom/specs/WI-1844/spec.md#acceptance-criteria

## Exceptions And Boundaries

- Failure modes: release readback drift/missing artifacts, unreadable PR, unmerged PR, release target commit mismatch, carrier writeback block, recovery/status block, shadow refresh block.
- Operational boundaries: `--apply` writes only repo carrier surfaces; host/npm/release surfaces remain read-only.
- Rollback or fallback expectations: revert the PR or rerun existing `carrier closeout-sync`/`recovery writeback` commands manually using emitted terminal metadata.

## Acceptance Criteria

- [x] A1: `release closeout-sync` appears in CLI help as an implemented delivery command.
- [x] A2: dry-run emits a terminal carrier plan without writing files.
- [x] A3: apply delegates only repo carrier/status/shadow updates and never publishes or merges.
- [x] A4: release drift or PR mismatch blocks before carrier writes.
- [x] A5: README, README.zh-CN, and CLI matrix describe the product boundary.
