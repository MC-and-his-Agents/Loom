# WI-1909 Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: FR-5 is a bounded CLI/fixture batch over already-frozen workstation registry and global runtime cache contracts, with an explicit issue tree and focused migration fixtures. consumer boundary: suite validate, review, PR gate, controlled merge, closeout, and FR-5 issue closeout may consume this minimal suite plus focused CLI contract validation. recheck condition: require full suite artifacts if scope expands into automatic multi-repository mutation, host-private Codex APIs, deleting host-owned tracked payloads, or release publishing.
- Consumes:
  - Work Item / FR locator: #1909, #1910, #1911, #1912, #1913 under FR #1908.
  - Story Readiness confirmed locator, blocking locator, or not_applicable rationale: issue bodies and milestone strategy define this CLI batch.
  - Story scenario locator, or not_applicable rationale: scenarios are defined in this spec.
  - Story Business Confirmation confirmed locator, blocking locator, or not_applicable rationale: no external business semantics beyond developer workstation migration behavior.
- Produces:
  - Scenario ids / locators: S1-S5 in this file.
  - Acceptance ids / locators: A1-A7 in this file.
  - Behavior evidence expectation: focused legacy migration CLI contract plus adjacent workstation/global cache validation.
- Locator:
  - Spec locator: .loom/specs/WI-1909/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: issues #1908, #1909, #1910, #1911, #1912, #1913; docs/adoption/workstation-registry-contract.md; docs/adoption/global-cli-user-plugin-contract.md.
  - Freshness rule: recheck after workstation registry schema, global cache path contract, installed-state authority, or legacy residue ownership rules change.

## Goal

Give repositories already using older Loom versions a low-risk explicit migration path from repo-local runtime/cache residue to workstation-owned global cache, without making migration a prerequisite for ordinary upgrade, doctor, status, resume, or adoption validation.

## Scope

- In scope:
  - #1909: `loom migrate-global-cache plan --target . --json` reports old repo-local cache/residue state without writes.
  - #1910: `loom migrate-global-cache apply --target . --json` moves ignored `.loom/runtime/**` and `.loom/tmp/**` into the global cache and registers the repository.
  - #1911: detect `.loom/bin`, `plugins/loom`, `.agents/skills`, and `.agents/plugins/marketplace.json` legacy residue with tracked/untracked ownership classification.
  - #1912: output repo change strategy as `no-op`, `auto-commit candidate`, `PR required`, or `blocked`.
  - #1913: run a migration validation package covering installed-state validate, host verify, skills check, doctor, and git status classification.
- Out of scope:
  - Automatic multi-repository migration.
  - Deleting payloads not proven to be Loom-owned cache/residue.
  - Treating migration output as review, merge, closeout, or release evidence.
  - Publishing v0.27.0 or closing the milestone; #1914 owns release closeout.

## Key Scenarios

### Scenario S1

Given a current metadata-only repository with no legacy repo-local cache
When `loom migrate-global-cache plan --target . --json` runs
Then the output is non-mutating and classifies the strategy as `no-op`.

### Scenario S2

Given a repository with ignored `.loom/runtime/**` and `.loom/tmp/**`
When `loom migrate-global-cache apply --target . --json` runs
Then Loom moves those cache paths to `~/.loom/repos/<repo-id>/`, writes or refreshes the workstation registry entry, and leaves repository git status free of ignored cache noise.

### Scenario S3

Given tracked legacy residue such as `.loom/bin`, `plugins/loom`, `.agents/skills`, or `.agents/plugins/marketplace.json`
When migration planning runs
Then Loom reports ownership/classification diagnostics and marks tracked payload removal as `PR required` unless it can prove a safer no-op.

### Scenario S4

Given malformed installed-state, conflicting registry identity, missing target, or unsafe residue ownership
When plan or apply runs
Then Loom fails closed with `blocked` classification and repair guidance, without deleting repository content.

### Scenario S5

Given apply completes
When validation package runs
Then installed-state validate, host verify, skills check, doctor, and git status classification are reported in the migration result.

## Behavior Evidence

- Scenario coverage:
  - S1 -> `python3 tools/check_cli_contract.py --surface legacy-migration`.
  - S2 -> `python3 tools/check_cli_contract.py --surface legacy-migration`.
  - S3 -> `python3 tools/check_cli_contract.py --surface legacy-migration`.
  - S4 -> `python3 tools/check_cli_contract.py --surface legacy-migration`.
  - S5 -> `python3 tools/check_cli_contract.py --surface legacy-migration`.
- Adjacent regression coverage:
  - Workstation/global cache boundary -> `python3 tools/check_cli_contract.py --surface workstation-registry`.
  - Static sanity -> `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `git diff --check`.
- Expected evidence locator: PR validation summary for the FR-5 batch PR.
- Freshness rule: rerun checks after changes to `tools/loom.py`, workstation registry/global cache helpers, legacy migration fixtures, runtime copies, or package surfaces in this batch.
- Execution ledger acceptance locator: .loom/specs/WI-1909/spec.md.

## Exceptions And Boundaries

- Failure modes: missing target, malformed installed-state, unsupported registry schema, remote hash drift, duplicate repo id, tracked host-owned residue, or failed validation package must fail closed.
- Operational boundaries: `plan` is always non-mutating; `apply` may move only ignored Loom cache/runtime outputs and may write workstation registry state; tracked repository payload cleanup remains PR/manual unless explicitly proven safe.
- Rollback or fallback expectations: restore moved cache from the global cache artifact locator if needed; rerun plan/doctor after repair; revert the batch PR to remove CLI behavior.

## Acceptance Criteria

- [ ] A1: `migrate-global-cache plan` reports current, old, mixed legacy, and missing installed-state fixtures without writes.
- [ ] A2: `apply` moves ignored `.loom/runtime/**` and `.loom/tmp/**` into global cache and writes the workstation registry.
- [ ] A3: Legacy residue detection covers `.loom/bin`, `plugins/loom`, `.agents/skills`, and `.agents/plugins/marketplace.json` with tracked/untracked ownership signals.
- [ ] A4: Strategy output includes `no-op`, `auto-commit candidate`, `PR required`, and `blocked`.
- [ ] A5: Tracked legacy payload deletion is classified as `PR required`, not auto-applied.
- [ ] A6: Post-migration validation reports installed-state validate, host verify, skills check, doctor, and git status.
- [ ] A7: Normal doctor/status/resume/adoption usage remains usable without first running migration.
