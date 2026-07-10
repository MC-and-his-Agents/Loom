# WI-1904 Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: this is a bounded FR-4 CLI/fixture batch over the already-frozen workstation registry, global CLI/user plugin, host adapter, and repo/global artifact contracts. consumer boundary: suite validate, review, PR gate, controlled merge, closeout, and FR-4 issue closeout may consume this minimal suite plus focused CLI contract validation. recheck condition: require full suite artifacts if scope expands into destructive multi-repository mutation, release publishing, host-private Codex APIs, or FR-5 legacy migration apply.
- Consumes:
  - Work Item / FR locator: #1904, #1905, #1906, #1907 under FR #1902.
  - Story Readiness confirmed locator, blocking locator, or not_applicable rationale: issue bodies and current milestone strategy define this CLI batch.
  - Story scenario locator, or not_applicable rationale: scenarios are defined in this spec.
  - Story Business Confirmation confirmed locator, blocking locator, or not_applicable rationale: no external business semantics beyond developer workstation upgrade behavior.
- Produces:
  - Scenario ids / locators: S1-S4 in this file.
  - Acceptance ids / locators: A1-A6 in this file.
  - Behavior evidence expectation: focused workstation registry CLI contract plus adjacent host/plugin freshness checks.
- Locator:
  - Spec locator: .loom/specs/WI-1904/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: issues #1902, #1904, #1905, #1906, #1907; docs/adoption/workstation-registry-contract.md; docs/adoption/global-cli-user-plugin-contract.md; docs/adoption/host-adapter-matrix.md.
  - Freshness rule: recheck after workstation registry schema, installed-state version context, host plugin freshness, Codex marketplace guidance, or repo mutation boundaries change.

## Goal

Make `loom workstation upgrade` useful after the plan-only slice: one command can plan machine-level CLI/plugin refresh, classify registered repositories, apply the machine refresh, and optionally apply a single low-risk repo adoption refresh without degrading FR-4 or FR-5 scope.

## Scope

- In scope:
  - #1904: machine plan covers npm CLI upgrade, Codex plugin/marketplace refresh guidance, and host doctor fallback.
  - #1905: repository plans classify registered entries as `repo_noop`, `repo_auto_commit_candidate`, `repo_pr_required`, or `blocked`.
  - #1906: `workstation upgrade --apply` performs machine-level refresh; repository mutation is supported only for one explicit registered target.
  - #1907: one invocation exposes freshness cache semantics so repository classification does not repeat host/plugin freshness reads.
- Out of scope:
  - Full automatic multi-repository mutation.
  - Deferring or shrinking FR-5 legacy migration.
  - Publishing v0.27.0 or closing the milestone; #1914 owns release closeout.
  - Codex plugin hot reload guarantees.

## Key Scenarios

### Scenario S1

Given a workstation with no registered repositories
When `loom workstation upgrade --plan --to 0.27.0 --json` runs
Then the output is non-mutating, classifies the machine plan as `machine_only`, and lists npm CLI, Codex plugin/marketplace refresh, and host doctor steps.

### Scenario S2

Given registered repositories with current metadata-only, stale metadata-only, legacy/repo-local, and drifted entries
When `loom workstation upgrade --plan --to 0.27.0 --json` runs
Then the output includes `repo_noop`, `repo_auto_commit_candidate`, `repo_pr_required`, and `blocked` classifications without writing repository payloads.

### Scenario S3

Given a workstation operator explicitly runs `loom workstation upgrade --apply --to 0.27.0 --json`
When no `--target <repo>` is supplied
Then Loom applies only machine-level refresh steps and does not mutate any registered repository.

### Scenario S4

Given a registered stale metadata-only repository is explicitly supplied with `--target <repo>`
When `loom workstation upgrade --apply --to 0.27.0 --target <repo> --json` runs
Then Loom may refresh only that single `repo_auto_commit_candidate`; `repo_pr_required`, `blocked`, and unknown entries remain blocked/manual.

## Behavior Evidence

- Scenario coverage:
  - S1 -> `python3 tools/check_cli_contract.py --surface workstation-registry`.
  - S2 -> `python3 tools/check_cli_contract.py --surface workstation-registry`.
  - S3 -> `python3 tools/check_cli_contract.py --surface workstation-registry`.
  - S4 -> `python3 tools/check_cli_contract.py --surface workstation-registry`.
- Adjacent regression coverage:
  - Host/plugin boundary -> `python3 tools/check_cli_contract.py --surface adoption-host-metadata`.
  - Static sanity -> `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `git diff --check`.
- Expected evidence locator: PR validation summary for the FR-4 batch PR.
- Freshness rule: rerun checks after changes to `tools/loom.py`, workstation registry fixtures/docs, host plugin freshness, or installed-state metadata refresh behavior.
- Execution ledger acceptance locator: .loom/specs/WI-1904/spec.md.

## Exceptions And Boundaries

- Failure modes: unsupported registry schema, missing path, remote hash drift, duplicate repo id, unknown adoption mode, or non-explicit repo apply must fail closed.
- Operational boundaries: machine apply may mutate global npm/Codex user state; repository apply requires explicit single target and must not write Loom runtime, plugin, or skills payload.
- Rollback or fallback expectations: revert the batch PR to remove CLI behavior; for live workstation state, rerun host doctor/install/register or per-repo adoption validation as appropriate.

## Acceptance Criteria

- [ ] A1: `workstation upgrade --plan` exposes machine-level CLI/plugin/host doctor steps.
- [ ] A2: Repository plans include `repo_noop`, `repo_auto_commit_candidate`, `repo_pr_required`, and `blocked`.
- [ ] A3: `workstation upgrade --apply` can execute machine-level refresh without repository mutation.
- [ ] A4: Explicit single-target repo apply is limited to `repo_auto_commit_candidate`.
- [ ] A5: The plan exposes single-invocation freshness cache semantics and invalidation conditions.
- [ ] A6: Tests and docs preserve workstation truth vs repository truth boundaries.
