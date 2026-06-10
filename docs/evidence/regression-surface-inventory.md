# Regression Surface Inventory

Status: inventory-only evidence for #1248, #1268, #1275, #1281 under umbrella #1255.

Read timestamp: 2026-06-05T05:01:12Z.

Read head: `c5ba4fdf6ec4358f5f960303eaed7d2737594fc3`.

Read branch: `work/1255-regression-inventory`.

This document freezes current regression surface boundaries before any split work. It does not change runner behavior, CI semantics, suite membership, or validation authority. Unknowns remain unknown until a later implementation PR proves them.

## Governing Contracts

The shared vocabulary and evidence rules are defined by [regression-surface-contract.md](../methodology/harness/regression-surface-contract.md).

Closed contract inputs:

| Issue | Contract role | Boundary consumed here |
| --- | --- | --- |
| #1264 | Regression bucket and named surface taxonomy | Use stable bucket, named surface, sub-scenario, fixture group, fast validation, full validation, and closeout evidence vocabulary. |
| #1265 | Regression surface evidence schema | Later splits must report surface label, scenario label, command, elapsed time, result, and failure summary. |
| #1266 | Fast and full validation policy | Fast surfaces may support local or PR iteration; full validation remains authoritative for merge-ready and release decisions. |

Parent #1255 excludes coverage removal, merge-ready or release weakening, workstation/session truth, and unrelated product behavior changes.

## #1248 Daily Execution CLI

Current bucket: `daily-execution-cli`.

Primary locator: `skills/shared/scripts/loom_check.py`, function `check_daily_execution_cli()`.

Current aggregate entry: `collect_source_failures(... SOURCE_SURFACE_SOURCE_SELF_FIXTURE ...)` includes `daily-execution-cli` as one `source-self-fixture` step.

Current always-read command inventory from `demo_commands`:

| Label | Command | Allowed result |
| --- | --- | --- |
| `runtime-state-init` | `python3 tools/loom_init.py runtime-state --target .` | `pass` |
| `runtime-state-flow` | `python3 tools/loom_flow.py runtime-state --target examples/new-project --item INIT-0001` | `pass` |
| `fact-chain` | `python3 tools/loom_flow.py fact-chain --target examples/new-project --item INIT-0001` | `pass` |
| `runtime-evidence` | `python3 tools/loom_flow.py runtime-evidence --target examples/new-project --item INIT-0001` | `pass` |
| `state-check` | `python3 tools/loom_flow.py state-check --target examples/new-project --item INIT-0001` | `pass` |
| `status-control` | `python3 tools/loom_status.py --target examples/new-project --item INIT-0001` | `pass`, `block` |
| `runtime-parity` | `python3 tools/loom_flow.py runtime-parity validate --target examples/new-project --item INIT-0001` | `pass` |
| `adopt-verify` | `python3 tools/loom_flow.py adopt verify --target examples/new-project --item INIT-0001` | `pass` |
| `carrier-refresh` | `python3 tools/loom_flow.py carrier refresh --target examples/new-project --item INIT-0001 --dry-run` | `pass` |
| `host-binding-validate` | `python3 tools/loom_flow.py host-binding validate --target . --owner MC-and-his-Agents --repo Loom --branch main` | `pass`, `block` |
| `host-binding-inspect` | `python3 tools/loom_flow.py host-binding inspect --target . --owner MC-and-his-Agents --repo Loom --branch main` | `pass`, `block` |
| `goal-derive` | `python3 tools/loom_flow.py goal derive --target examples/new-project --item INIT-0001` | `pass`, `block` |
| `goal-validate` | `python3 tools/loom_flow.py goal validate --target examples/new-project --item INIT-0001` | `pass`, `block` |
| `governance-profile-status` | `python3 tools/loom_flow.py governance-profile status --target examples/new-project` | `pass` |
| `governance-profile-upgrade-plan` | `python3 tools/loom_flow.py governance-profile upgrade-plan --target examples/new-project` | `pass`, `block` |
| `governance-profile-upgrade` | `python3 tools/loom_flow.py governance-profile upgrade --target examples/new-project --to standard --dry-run` | `pass` |
| `governance-profile-binding` | `python3 tools/loom_flow.py governance-profile binding --target .` | `block` |
| `flow-pre-review` | `python3 tools/loom_flow.py flow pre-review --target examples/new-project --item INIT-0001` | `pass`, `block`, `fallback` |
| `flow-review` | `python3 tools/loom_flow.py flow review --target examples/new-project --item INIT-0001` | `pass`, `block`, `fallback` |
| `flow-resume` | `python3 tools/loom_flow.py flow resume --target examples/new-project --item INIT-0001` | `pass` |
| `flow-handoff` | `python3 tools/loom_flow.py flow handoff --target examples/new-project --item INIT-0001` | `pass`, `block` |
| `flow-merge-ready` | `python3 tools/loom_flow.py flow merge-ready --target examples/new-project --item INIT-0001` | `pass`, `block`, `fallback` |
| `admission` | `python3 tools/loom_flow.py checkpoint admission --target examples/new-project --item INIT-0001` | `pass` |
| `build` | `python3 tools/loom_flow.py checkpoint build --target examples/new-project --item INIT-0001` | `pass`, `block`, `fallback` |
| `merge` | `python3 tools/loom_flow.py checkpoint merge --target examples/new-project --item INIT-0001` | `pass`, `block`, `fallback` |
| `locate` | `python3 tools/loom_flow.py workspace locate --target examples/new-project --item INIT-0001` | `pass` |
| `attach` | `python3 tools/loom_flow.py workspace attach --target examples/new-project --item INIT-0001` | `pass` |
| `review-read` | `python3 tools/loom_flow.py review read --target examples/new-project --item INIT-0001` | `pass` |
| `host-lifecycle` | `python3 tools/loom_flow.py host-lifecycle --target examples/new-project --item INIT-0001` | `pass` |
| `purity` | `python3 tools/loom_flow.py purity-check --target examples/new-project --item INIT-0001` | `pass` |

Current fixture groups inside the same bucket:

| Candidate group | Current role | Split risk |
| --- | --- | --- |
| `repo-local-runtime-chain` | Runtime state, fact-chain, runtime evidence, state-check, status, runtime parity. | Order and target binding are part of coverage. |
| `adoption-and-carrier` | `adopt verify`, `carrier refresh`, generated companion consumption, repo-interface locator consumption. | Must not hide missing adoption inputs. |
| `host-binding` | Host binding validate/inspect against `main`, allowing host read unavailability only where code already allows it. | Host read availability is not proof of product behavior. |
| `goal-and-governance-profile` | Goal derive/validate and governance-profile status/upgrade/binding. | Strong upgrade missing host enforcement remains expected evidence. |
| `flow-lifecycle` | Flow pre-review/review/resume/handoff/merge-ready plus checkpoint admission/build/merge and workspace locate/attach. | Flow step order is asserted and cannot be silently relaxed. |
| `review-read` | Review read and review record contract checks. | Review evidence is separate from merge-ready and closeout consumption. |
| `installed-runtime-positive-chain` | Installed skill route and flow checks for pre-review, spec-review, review, merge-ready, checkpoint merge, controlled merge, and retained result consumption. | This is slow/full candidate until a later PR proves smaller authoritative grouping. |
| `installed-negative-boundaries` | Missing suite, missing review, PR-body/raw-evidence bypass, stale review, CI bypass, missing install-layout, dirty retire samples. | Negative tests must not be moved into fast-only proof without full aggregation. |
| `retire-and-workspace` | Installed purity-check, workspace cleanup, workspace retire, Loom-owned residue, non-Loom residue. | Mutating fixture setup is internal to temporary targets and must not become repo truth. |

Boundary decision: keep the current aggregate bucket as full coverage until a later implementation PR emits child surface evidence and proves aggregation preserves every group above.

Review-run fixture group mapping for #1250:

| Stable group name | Current locator | Coverage boundary |
| --- | --- | --- |
| `positive-default-review` | `check_review_run_fixture()` positive chain | Default Codex exec adapter, default profile, review record input, context pack, prompt guidance, and source suite/setup contract remain covered. |
| `shadow-adapter` | `check_review_run_fixture()` shadow adapter and shadow unavailable cases | Shadow review evidence must remain non-authoritative, non-blocking, and unable to replace the default review record input. |
| `codex-app-host-default` | `check_review_run_fixture()` embedded JSON, host default, CI host default, and authoritative Codex App cases | Valid Codex App host proof can select the app adapter and expose thread/model proof metadata without authoring merge-ready truth before a review record exists. |
| `codex-app-fallbacks` | `check_review_run_fixture()` CI missing proof and app-server unavailable fallback cases | Missing or unavailable Codex App proof falls back to default Codex exec with explicit diagnostics, without treating workstation/session state as repo truth. |
| `codex-app-fail-closed` | `check_review_run_fixture()` proof conflict, high-risk unverified proof, missing proof, and invalid raw cases | Runtime conflicts, missing proof, unverified high-risk model proof, and invalid raw evidence must block rather than fallback silently. |
| `repeated-blocker-context` | `check_review_run_fixture()` repeated blocker context pack fixture | Prior normalized findings are summarized as repeated blocker candidates in the review context pack. |
| `profile-policy` | `check_review_run_fixture()` profile override, repo-owned profile, invalid repo profile, and local config cases | Profile selection must preserve override evidence, repo-owned policy precedence, and local Codex config opt-in boundaries. |
| `engine-output-fail-closed` | `check_review_run_fixture()` engine unavailable, schema drift, and tracked edit cases | Missing engine, invalid engine output, and tracked repository edits must fail closed with stable failure reasons. |

Unknowns:

- Exact runtime cost of each candidate group is not measured here.
- Which groups become always-run daily versus targeted slow/full surfaces is not confirmed.
- Host binding read outcomes can vary by API availability; this inventory records existing allowed results only.

Later PR slice recommendation: PR-L should add named progress/evidence around the existing `daily-execution-cli` aggregate without changing command membership. Any extraction of `installed-*` groups should be separate from the main command inventory because it carries slow fixture setup and host boundary risk.

## #1268 Check CLI Contract

Current bucket: `check-cli-contract`.

Primary locator: `tools/check_cli_contract.py`, function `main()`.

Current group inventory:

| Stable group name | Current locator | Coverage boundary |
| --- | --- | --- |
| `help-matrix` | `main()` command matrix assertions | `REQUIRED_COMMANDS`, implemented command status, domain checks for suite commands, and scenario command families. |
| `version-and-pr-metadata` | `version --json`; `pr metadata-preflight --body-file` | Repo version context and PR body-file artifact validation without a live PR. |
| `suite-path-and-suite-validate` | `run_suite_inspect_fixture`, `run_suite_validate_fixture`, minimal/full helpers | Unknown, conflicting, minimal, not_applicable, full, advisory, missing, invalid, mapping, and failure taxonomy coverage. |
| `suite-evidence` | `run_suite_evidence_*` helpers | Evidence inspect/scaffold/validate, missing map, stale evidence, head/PR drift, validation summary drift, missing source locator, scaffold write boundaries. |
| `suite-carrier` | `run_suite_carrier_*` helpers | Carrier inspect/validate, carrier type/status/relationship, primary conflicts, host signal conflicts, deferred-as-completed. |
| `suite-scaffold` | `run_suite_scaffold_*` helpers | Minimal/full dry-run and apply behavior, preserve-existing policy, traversal/absolute/symlink/directory fail-closed cases, truth write boundary. |
| `installed-state-and-adoption` | `installed-state`, `detect`, `doctor`, `repair`, `verify`, `adopt verify` | Missing, legacy, mixed-legacy, current install classification, declared suite support, required suite validation, metadata-only adoption. |
| `host-and-skills-surface` | `host list/doctor/install/verify/register`; `skills list/generate/check/package/release-check` | Host adapter inventory, managed plugin install, workstation registration, generated skills parity, release authority. |
| `scenario-wrappers-and-gates` | `route`, `status`, `fact-chain`, `profile`, `story/spec/plan/build/pre-review/handoff/retire/closeout`, `gate *`, `merge-ready` | CLI wrapper contracts, active item suite gate consumption, PR head drift fixture, closeout gate consumption. |
| `shared-fixture-helpers` | Top-level helper functions before `main()` | Suite writers, governance chain fixture, legacy/downstream/plugin metadata fixtures, forbidden truth fixture, JSON runners. |

Boundary decision: future splits should preserve these group names and keep helper ownership explicit. `unknown` suite path, missing inputs, stale evidence, and host conflicts remain fail-closed cases, not confirmed pass cases.

Unknowns:

- The current file does not emit per-group elapsed time.
- Some helpers are shared by multiple groups; ownership must be assigned before code extraction.
- Active item wrapper checks depend on the current repo carrier and should not be treated as static fixture-only proof.

Later PR slice recommendation: PR-M should introduce group-level labels or reporting for `check-cli-contract` before moving code. Helper extraction should follow only after group evidence proves no group was lost.

## #1275 Non-Daily Source-Self Fixture Groups

Current bucket: `source-self-fixture`.

Primary locator: `skills/shared/scripts/loom_check.py`, function `collect_source_failures()`.

Current source-self fixture steps outside the daily bucket:

| Step label | Current callable | Ownership note |
| --- | --- | --- |
| `py-compile-cache-hygiene-pre` | `check_py_compile_cache_hygiene(root)` | Runs before daily execution CLI. |
| `py-compile-cache-hygiene` | `check_py_compile_cache_hygiene(root)` | Runs after daily execution CLI. |
| `repo-companion` | `check_repo_companion_interface_contracts(root)` | Repo companion contract surface. |
| `repo-interop` | `check_repo_interop_contracts(root)` | Repo interop contract surface. |
| `external-orchestrator-interop` | `check_external_orchestrator_interop_fixture_contract(root)` | External orchestrator interop fixture. |
| `external-orchestrator-conformance` | `check_external_orchestrator_conformance_contract(root)` | External orchestrator conformance fixture. |
| `external-runtime-devendor` | `check_external_runtime_devendor_contract(root)` | Runtime devendor boundary. |
| `behavior-first-locators` | `check_behavior_first_locator_contracts(root)` | Locator behavior contract. |
| `adversarial-adoption` | `check_adversarial_adoption_fixture(root)` | Heavy adversarial fixture group. |

Overlap boundary:

- `daily-execution-cli` is itself a `source-self-fixture` step, but #1248 owns its internal command and fixture inventory.
- `closeout-reconciliation` is itself a `source-self-fixture` child surface, but #1278 owns its command and payload inventory.
- #1275 owns the non-daily step labels above and the boundary that they remain outside #1248 unless a later PR explicitly moves them with full aggregation proof.
- The #1275 issue body mentions overlap with #1247; this inventory treats that as an unresolved locator mismatch because the active requested target is #1248.

Unknowns:

- Runtime cost and flake profile per non-daily fixture group are not measured here.
- Whether `py-compile-cache-hygiene-pre` and `py-compile-cache-hygiene` should remain separate is not decided here.
- No new source-self selector is confirmed by this inventory.

Later PR slice recommendation: PR-N should add source-self fixture group evidence for the non-daily labels without moving `daily-execution-cli` internals. Any ownership correction for #1247 versus #1248 should be made in issue comments before implementation.

## #1278 Closeout/Reconciliation Source Surface

Current bucket: `closeout-reconciliation`.

Primary locator: `skills/shared/scripts/loom_check.py`, function `check_closeout_reconciliation_fixture()`.

Current source-surface entry: `collect_source_failures(... SOURCE_SURFACE_CLOSEOUT_RECONCILIATION ...)` exposes `closeout-reconciliation` as a focused source surface. The aggregate `source-self-fixture` includes `review-run`, `merge-gate`, `closeout-reconciliation`, and the remaining source-self fixture steps.

Current always-read command inventory:

| Label | Command | Allowed result |
| --- | --- | --- |
| `closeout-check` | `python3 tools/loom_flow.py closeout check --target . --skip-gate` | `pass`, `block` |
| `closeout-sync` | `python3 tools/loom_flow.py closeout sync --target . --skip-gate` | `pass`, `block` |
| `reconciliation-audit` | `python3 tools/loom_flow.py reconciliation audit --target .` | `block` |
| `status-control-closeout` | `python3 tools/loom_status.py --target examples/new-project --item INIT-0001` | `pass`, `block` |

Current fixture groups inside the same bucket:

| Stable group name | Current locator | Coverage boundary |
| --- | --- | --- |
| `closeout-check-sync` | `check_closeout_reconciliation_fixture()` repo-local closeout commands | Closeout check/sync must keep runtime-state, repo, repo-specific closeout requirements, and reconciliation payload validation fail-closed. |
| `reconciliation-audit` | `check_closeout_reconciliation_fixture()` repo-local reconciliation command | Reconciliation audit remains allowed to return `block` for current source repo state, but payload schema and taxonomy must stay stable. |
| `historical-closeout-samples` | `check_closeout_reconciliation_fixture()` installed runtime live opt-in samples | Live historical issue/PR/project samples run only with explicit `LOOM_CHECK_LIVE_GITHUB=1` and non-GitHub Actions auth. |
| `safe-sync-dry-run` | `installed reconciliation sync dry-run` | Dry-run must expose `loom-safe-sync-plan/v1` and must not report applied actions. |
| `synthetic-fail-closed-payloads` | `require_closeout_reconciliation_contract()` samples | `fix-needed` and `block` reconciliation results must force closeout `block` with the correct fallback; `warn` must not block. |
| `status-closeout-binding` | `check_status_closeout_binding_contract(root)` | `loom_status` closeout status must forward issue, PR, Project, branch, owner/repo, and skip-gate inputs to closeout payload generation. |

Boundary decision: keep closeout/reconciliation as a focused source surface without treating it as release readiness. `closeout-reconciliation` is a fixture surface; authoritative closeout remains owned by scheduler-controlled gate and post-merge consumption.

Unknowns:

- Live historical closeout samples depend on explicit local GitHub auth and remain skipped in CI by design.
- Target-branch closeout semantics embedded in the broader adversarial adoption fixture remain aggregate `source-self-fixture` coverage unless a later split extracts that sub-scenario directly.

Later PR slice recommendation: #1279 retire/workspace and #1280 installed-runtime should remain separate named surfaces; do not fold them into `closeout-reconciliation`.

## #1281 Repo Local CLI CI Command Contract

Current bucket: `repo-local-cli`.

Primary locator: `.github/workflows/loom-check.yml`, job `repo-local-cli`.

Current CI shell block inventory:

| Order | Command | Dependency |
| --- | --- | --- |
| 0 | `make loom-demo-new-project-check` | Generates or refreshes `examples/new-project` before repo-local CLI commands. |
| 1 | `cd examples/new-project` | All following commands run from the generated demo target. |
| 2 | `python3 .loom/bin/loom_init.py runtime-state --target .` | Requires generated `.loom/bin`. |
| 3 | `python3 .loom/bin/loom_init.py verify --target .` | Requires generated target and init result. |
| 4 | `python3 .loom/bin/loom_init.py fact-chain --target .` | Requires generated target. |
| 5 | `python3 .loom/bin/loom_flow.py runtime-state --target . --item INIT-0001` | Requires `INIT-0001`. |
| 6 | `python3 .loom/bin/loom_flow.py fact-chain --target . --item INIT-0001` | Requires `INIT-0001`. |
| 7 | `python3 .loom/bin/loom_flow.py runtime-evidence --target . --item INIT-0001` | Requires runtime/fact-chain carriers. |
| 8 | `python3 .loom/bin/loom_flow.py state-check --target . --item INIT-0001` | Requires status/progress carriers. |
| 9 | `python3 .loom/bin/loom_flow.py flow pre-review --target . --item INIT-0001` | Depends on earlier runtime and state evidence. |
| 10 | `python3 .loom/bin/loom_flow.py checkpoint admission --target . --item INIT-0001` | Depends on item carriers. |
| 11 | `python3 .loom/bin/loom_flow.py workspace locate --target . --item INIT-0001` | Depends on item/workspace locators. |
| 12 | `python3 .loom/bin/loom_flow.py purity-check --target . --item INIT-0001` | Must run after generated target exists; order-sensitive with setup. |
| 13 | `LOOM_SOURCE_REPO_ROOT="$PWD" LOOM_INSTALLED_SKILLS_ROOT="$PWD/skills" LOOM_RUNTIME_SCENE=upgrade-rehearsal python3 skills/shared/scripts/loom_flow.py runtime-state --target examples/new-project --item INIT-0001` | Negative scene conflict check from repo root; expected to fail closed. |

Boundary decision: a future CI split must preserve every command and the setup dependency on `make loom-demo-new-project-check`. The scene conflict negative check is part of the current contract and cannot be dropped as "only environment setup".

Unknowns:

- Which commands can run independently in separate CI steps is not confirmed.
- Whether any command depends on side effects from a prior command beyond generated fixture presence is not proven here.
- No CI semantic change is authorized by this inventory.

Later PR slice recommendation: split the CI shell block only after adding readback that proves all commands remain present and order-sensitive commands keep setup before use.

## Release Decision

No release is required for this inventory batch. The change is documentation/evidence only and does not ship CLI, skills, package, workflow, release validation, npm payload, runner behavior, or other user-visible runtime behavior.

## Verification Plan

Minimum verification for this inventory batch:

- `git diff --check`
- Readback of issue bodies for #1248, #1268, #1275, #1281, #1255, #1264, #1265, #1266.
- Readback of `docs/methodology/harness/regression-surface-contract.md`.
- Readback of `skills/shared/scripts/loom_check.py`, `tools/check_cli_contract.py`, and `.github/workflows/loom-check.yml` locators above.

Full `loom_check` is intentionally not required because this PR does not change runtime or tooling behavior.
