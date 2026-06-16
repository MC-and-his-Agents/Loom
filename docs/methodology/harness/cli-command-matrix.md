# Loom CLI Command Matrix

The `loom` CLI is the primary control plane for the CLI-first operating layer. The current matrix is exposed mechanically through:

```bash
python3 tools/loom.py help --json
```

The JSON output is the canonical machine-readable matrix for tests and downstream consumers. This document freezes the naming rules and command families for human review.

Regression bucket / named surface / fast-vs-full validation semantics for long-running black-box checks are frozen in [regression-surface-contract.md](./regression-surface-contract.md). The command matrix may expose selectors or aggregate outputs for those surfaces, but it does not redefine that vocabulary here.

## Naming Rules

- Commands are verb-first where the domain is implicit: `loom detect`, `loom doctor`, `loom verify`.
- Domain commands use `<domain> <verb>`: `loom installed-state validate`, `loom host doctor`, `loom skills release-check`.
- Gate and checkpoint commands use the stable gate name as the subcommand: `loom gate merge`, `loom checkpoint admission`.
- Host-control commands keep the host object name: `loom issue inspect`, `loom pr gate`, `loom workspace check`.
- Scenario commands keep the skill-facing scenario names: `loom spec-review`, `loom merge-ready`, `loom handoff`.

## Core And Installation

| Command | Status | Contract |
| --- | --- | --- |
| `loom version` | implemented | Emits repository, skills, plugin, host-adapter, runtime, and package version context. |
| `loom help` | implemented | Emits the full command matrix and fail-closed rules. |
| `loom installed-state show` | implemented | Reads `loom-installed-state/v2` from the target repo. |
| `loom installed-state validate` | implemented | Validates schema, layers, graph, and version metadata. |
| `loom installed-state export` | implemented | Emits valid installed-state plus installation graph. |
| `loom detect` | implemented | Detects current, legacy, symlink, single-skill, metadata-only, embedded plugin, and mixed installed surfaces. |
| `loom doctor` | implemented | Diagnoses installed-state, declared adoption mode, runtime provider mode (`global-cli` or `repo-local-wrapper`), provider readiness, and legacy surface readiness with fail-closed repair fallback. |
| `loom repair plan` | implemented | Emits a non-mutating repair plan for missing, invalid, legacy, or runtime-provider carrier drift. |
| `loom repair apply` | implemented | Fails closed until write ownership and rollback semantics are approved by a later Work Item. |

## Implemented Phase Commands

#893 implements the host-control command family:

```text
loom workspace create|locate|check|retire
loom issue inspect|bind|reconcile
loom project status|reconcile
loom pr inspect|metadata-preflight|gate
loom merge check|run
loom reconcile
```

These commands use JSON wrappers over existing harness control-plane readers. GitHub and git remain the host-owned truth sources; Loom only freezes the command names, output shape, fail-closed reasons, and fallback names.

#894 implements the host adapter command family:

```text
loom host list|doctor|install|verify|upgrade|remove
```

`host list` and `host doctor` are read-only. Adapter-managed mutations fail closed unless explicit `--apply` is present. Full-repo/native discovery remains operator-owned and is not mutated by the CLI.

#895 implements the generated SKILLS command family:

```text
loom skills list|generate|sync|check|doctor|package|release-check
```

`skills generate` and `skills sync` require `--apply`; check, doctor, package, and release-check are read-only.

#1261 splits the generated SKILLS validation bucket into named diagnostic surfaces without changing the aggregate command contract:

```text
python3 tools/skills_surface.py check --surface docs-reference-sync
python3 tools/skills_surface.py check --surface generated-tree-drift
python3 tools/skills_surface.py check --surface package-metadata
python3 tools/skills_surface.py check --surface cache-artifacts
python3 tools/skills_surface.py check --surface launcher-smoke [--skill <id>]
```

`python3 tools/skills_surface.py check`, `make skills-check`, and `loom skills check --target . --json` remain the aggregate generated SKILLS validation path for merge-ready and release-readiness evidence. The named commands are evidence labels for diagnosis, PR metadata, and closeout consumption; they do not add new skill packaging semantics.

#1263 preserves the aggregate runtime regression bucket while documenting named
diagnostic runtime surfaces for parent closeout evidence:

```text
python3 tools/check_loom_check_runtime_regressions.py --surface single-flight-locking
python3 tools/check_loom_check_runtime_regressions.py --surface worktree-local-lock-paths
python3 tools/check_loom_check_runtime_regressions.py --surface installer-regression-lock-output
python3 tools/check_loom_check_runtime_regressions.py --surface subprocess-env-purity
python3 tools/check_loom_check_runtime_regressions.py --surface temp-dir-cleanup
python3 tools/check_loom_check_runtime_regressions.py --surface demo-fixture-cleanliness
```

`python3 tools/check_loom_check_runtime_regressions.py`,
`make loom-check-runtime-regression`, and `make loom-check` remain the aggregate
runtime regression validation path. The checker has no `--surface aggregate`
selector; evidence summaries must cite the no-filter command or Make target for
aggregate proof.

#890 implements the adoption and governance profile command family:

```text
loom init
loom adopt verify
loom route
loom profile status|upgrade-plan|upgrade
```

`init`, `route`, and `adopt verify` are CLI-first wrappers over the existing initialization and adoption runtimes. `loom adopt verify` is the adoption contract verifier; bootstrap remains under `loom init bootstrap` to avoid mixing adoption verification with repository scaffolding.

`profile status`, `profile upgrade-plan`, and `profile upgrade` wrap the existing governance profile runtime. `profile upgrade` inherits the underlying dry-run-by-default semantics and does not promote validation-only parity into a blocking gate.

#891 implements the fact-chain, checkpoint, and gate command family:

```text
loom status
loom fact-chain
loom checkpoint admission|build|merge
loom gate pre-review|spec-review|review|pr|merge|freeze check|freeze write|closeout
```

`status` and `fact-chain` are derived reads over the existing Loom carriers. `checkpoint` commands consume the established checkpoint payloads. `gate merge` checks host merge readiness through controlled-merge check but does not execute a merge. `gate freeze check` validates the hosted gate input snapshot without writing. `gate freeze write` writes only a repo-local runtime snapshot under `.loom/runtime/gate-freeze/`. `gate closeout` checks closeout state but does not sync or close host objects.

For #1229, the contract now reserves an explicit idle repository state for these read surfaces:

- `loom fact-chain`
  - may return `fact_chain.mode = idle` with `current_item_id = no_active_item`
- `loom status`
  - may render repository execution state `idle` without inventing an active Work Item

`workspace retire` remains local-only. Versioned terminal carrier updates use the explicit `carrier closeout-sync` command so local cleanup, host closeout sync, and repo carrier closeout sync do not share an ambiguous command name.

Idle closeout recovery is intentionally split into three layers:

| Layer | Command family | Writes host state | Writes versioned carriers | Primary use |
| --- | --- | --- | --- | --- |
| Local worksite retirement | `loom workspace retire` | no | no | Produce local-only cleanup/retire evidence while leaving `.loom/progress/**`, `.loom/status/current.md`, and `.loom/bootstrap/init-result.json` unchanged. |
| Host closeout sync | host-owned merge/readback plus `reconciliation audit|sync` / `closeout check|sync` | yes, only through explicit host sync paths | no | Align GitHub issue, PR, Project, target branch, and merge commit truth. |
| Repo carrier closeout sync | `loom carrier closeout-sync` | no | yes, only with `--apply` | Repair HotCP-style stale active carriers after host truth already proves completion. |

The HotCP-style stale carrier regression fixture covers this sequence: `workspace retire` stays `local_only`; `repair plan/apply` or `carrier closeout-sync` exposes repo-local `carrier_closeout_sync`; the final fact-chain reads `idle` with `current_item_id = no_active_item`.

## Carrier Commands

```text
loom carrier closeout-sync
```

`carrier closeout-sync` writes structured terminal closeout metadata to versioned `.loom/progress/<item>.md` carriers only under explicit `--apply` semantics. Its default dry-run emits the planned carrier diff and never mutates GitHub, Project, PR, issue, worktree, or other host state.

## Delivery Commands

#889 implements the install, upgrade, rollback, and verify command family:

```text
loom install
loom upgrade-plan
loom upgrade
loom rollback
loom verify
```

`install` writes `loom-installed-state/v2` only when `--apply` is present and
the target artifact/scope is explicit. Metadata-only repository adoption,
embedded repository payload, compatibility skills export, single-skill export,
workstation registration, and runtime carrier changes are separate operations
under the [installation taxonomy](../../adoption/installation-taxonomy.md).
The runtime provider mode is also explicit: `global-cli` repositories expect the
installed root `loom` command and do not require `.loom/bin`, while
`repo-local-wrapper` repositories keep `.loom/bin` or equivalent wrappers only
when installed-state declares that carrier role.
`upgrade-plan` is non-mutating and emits ordered repair /
legacy-classification / no-op actions. `verify` consumes `doctor` so
installed-state, declared adoption mode, provider readiness, and legacy-surface
readiness stay aligned. `upgrade` requires `--apply` and refuses to mutate while
installed-state is invalid or legacy surfaces remain unclassified. `rollback`
remains a structured fail-closed command because rollback/delete ownership
cannot be inferred from installed surface detection.

Copyable validation commands for a `global-cli` repository:

```bash
loom installed-state validate --target . --json
loom detect --target . --json
loom doctor --target . --json
loom verify --target . --json
loom repair plan --target . --json
```

## Scenario Commands

#892 implements the CLI-backed scenario command family:

```text
loom story
loom spec
loom plan
loom build
loom pre-review
loom closeout
loom handoff
loom retire
```

`story`, `build`, `pre-review`, and `handoff` wrap the existing `loom_flow.py flow` runtime and preserve structured JSON. `spec` and `plan` expose the expected `.loom/specs/<item>/` locators and fail closed when authoring carriers are absent. `closeout` wraps the closeout check surface and does not close host objects. `retire` exposes a non-mutating handoff / cleanup contract and points callers to `workspace retire` for explicit worksite lifecycle handling; it does not write terminal carrier metadata.

## Reserved Phase Commands

No command in the #889/#892/#896 implementation batch remains reserved. Later phase issues may still reserve additional names outside #885 scope.

## Gate Freeze Surface

#1507 freezes the `loom-gate-freeze/v1` snapshot contract in
[gate-freeze.md](./gate-freeze.md). The implemented command family is:

```text
loom gate freeze check
loom gate freeze write
```

These names are present in `loom help --json` and covered by CLI contract
checks. Consumers must still read the current command matrix before suggesting
either command as an executable repair command. If a freeze snapshot needs to suggest an
unimplemented command, it must emit `unsupported_command_surface` and provide an
existing supported alternative path.

## Planned Suite Commands

#1052 planned the full spec suite CLI command surface. #1109-#1111 implement the first read-only command and add it to the mechanical help matrix and CLI contract checks:

```text
loom suite inspect
```

`suite inspect` is read-only. It reports the current suite path decision, repo-relative artifact locators, task carrier locators, and inspect-only missing input/advisory gaps. It does not decide readiness, scaffold missing artifacts, mutate host state, write review truth, write merge-ready truth, or write closeout truth.

#1114 implements the dry-run planning surface for the first scaffold command:

```text
loom suite scaffold
```

`suite scaffold` defaults to dry-run, emits `mutates: false`, and plans suite artifacts under `.loom/specs/<item>/`. Its JSON reports planned writes, source templates, consumed locators, required versus conditional artifacts, overwrite policy, `apply_required`, rollback note, and `created_locators`. #1115 implements `--apply` for repo-local minimal scaffold writes: missing `spec.md` and `plan.md` files are created from the Loom templates, existing files are preserved, and the response reports only the locators actually created. #1116 implements `--suite full` for the standard full suite scaffold artifacts: `suite-index.md`, `spec.md`, `plan.md`, `research.md`, `contracts.md`, and `readiness-checklist.md`. Traversal items, absolute items, symlink paths, and non-file artifact placeholders fail closed before writes.

#1120 implements the first validate command:

```text
loom suite validate
```

`suite validate` is read-only. It reuses the suite inspect state and returns a readiness envelope with `pass`, `block`, `advisory`, or `not_applicable`, plus `failed_layer`, `fail_closed_reason`, `missing_inputs`, `blocking_gaps`, `advisory_gaps`, `findings`, and `failure_taxonomy`. The #1120/#1121/#1122/#1123/#1124/#1125 slice covers core path, artifact, not_applicable, spec/plan mapping validation, stable failure taxonomy output, and spec-review consumer integration: missing, invalid, or conflicting suite path decisions block; missing or non-file required artifacts block; full path conditional artifacts are inventoried; minimal and suite-level `not_applicable` records must carry rationale, consumer boundary, and recheck condition; `deferred` cannot satisfy a `not_applicable` readiness gap; authored scenario and acceptance ids in `spec.md` must map to `plan.md` validation or test strategies; every emitted finding carries failure kind, default result, failed layer, source locator, consumer impact, remediation direction, fallback, and binding; `flow spec-review`, `gate spec-review`, and spec-review record allow consume the suite validation result before approval. Later evidence, consistency, carrier, and merge-ready integration checks remain owned by later Work Items. It does not write suite files, review truth, merge-ready truth, closeout truth, host state, `/speckit.*`, or `.specify/` surfaces.

#1127 implements the first evidence-map read and validation commands:

```text
loom suite evidence inspect
loom suite evidence validate
```

`suite evidence inspect` is read-only. It reports the evidence-map locator, row count, normalized rows, required evidence types, freshness vocabulary, consumed contracts, and inspect-only missing input/advisory gaps. `suite evidence validate` is read-only and returns the shared readiness envelope for behavior evidence, test evidence, and fresh verification input rows. Missing evidence-map rows, incomplete required row fields, missing repo-local source locators for present evidence, stale/conflicting evidence freshness, explicit current-head / PR-head / reviewed-head drift, validation-summary digest drift, and fresh verification rows that do not consume present behavior and test evidence block with machine-readable findings. These commands do not scaffold evidence-map files, write review truth, write merge-ready truth, write closeout truth, mutate host state, or create `/speckit.*` or `.specify/` surfaces.

#1129 implements the evidence-map scaffold command:

```text
loom suite evidence scaffold
```

`suite evidence scaffold` defaults to dry-run, emits `mutates: false`, and plans exactly one repo-local artifact: `.loom/specs/<item>/evidence-map.md`. `--apply` is required before writing. Existing files are preserved, symlink or non-file targets fail closed, and the response reports planned writes, source template, consumed suite locators, preserve-existing overwrite policy, rollback note, and created locators. Seed rows for behavior evidence, test evidence, and fresh verification input start with `missing` freshness, so the scaffold itself cannot satisfy evidence validation or replace authored evidence truth.

#1131 implements the task-carrier read and validation commands; #1132 deepens the validation payload with host signal conflict classification:

```text
loom suite carrier inspect|validate
```

`suite carrier inspect` is read-only. It reports the task-carrier locator, normalized carrier rows, recognized carrier types, normalized status vocabulary, relationship vocabulary, Work Item/recovery truth locators, consumed contracts, recognized truth signals, and the explicit boundary that carrier/project/checklist `done` does not satisfy Work Item, evidence, review, merge-ready, or closeout truth. `suite carrier validate` is read-only and returns the shared readiness envelope for carrier locator, normalized status, relationship, Work Item backlink, breakdown/spec/plan/validation locators, provenance, freshness rule, primary-carrier uniqueness, deferred-as-completed, carrier truth conflict findings, and Project/checklist/issue/PR host signal conflicts such as Project Done with issue open, PR merged with issue open, issue closed with Project in progress, or checklist checked with evidence missing. These commands do not write task-carrier files, host state, review truth, merge-ready truth, closeout truth, `/speckit.*`, or `.specify/` surfaces.

The remaining suite namespace stays planned until later implementation Work Items add those commands to `loom help --json` and the CLI contract checks. The planned namespace is documented in [full-spec-suite-cli-surface.md](./full-spec-suite-cli-surface.md):

```text
loom suite analyze
loom suite consistency inspect|analyze
```

Remaining planned names are planning output only until a later implementation Work Item adds them to `loom help --json` and the CLI contract checks. Implementations must preserve the #1052 behavior classes: read-only, scaffold-write, validate, analyze, and fail-closed.

## Delegated Compatibility Commands

These commands currently route to existing wrappers and remain compatibility paths while the CLI-first execution layer is filled in:

```text
loom resume
loom spec-review
loom review
loom merge-ready
loom check
```

Delegated commands are allowed only when the wrapper is the existing authoritative implementation for that workflow. Missing wrappers fail closed.

## Verification

The command matrix is checked by:

```bash
python3 tools/check_cli_contract.py
```

Daily execution CLI bucket validation exposes explicit local fast / full entrypoints outside the `loom` command matrix:

```bash
make daily-execution-cli-fast
make daily-execution-cli-full
python3 tools/loom_check.py --profile source --source-surface daily-execution-cli-fast .
python3 tools/loom_check.py --profile source --source-surface daily-execution-cli-full .
```

The fast entry is a local smoke surface only. Merge-ready, release readiness, and source full self-checks must continue to consume `daily-execution-cli-full`, `merge-gate`, `source-self-fixture`, `full`, or equivalent full aggregate evidence, plus current PR head, review, fact-chain, hosted checks, PR metadata, release/no-release, and scheduler-owned gate inputs.

The command matrix records these as validation surfaces, not new top-level
`loom` commands. Evidence summaries that cite them must preserve:

- the exact surface name (`daily-execution-cli-fast` or
  `daily-execution-cli-full`);
- the command form that was run (`make ...` or `python3 tools/loom_check.py
  --profile source --source-surface ... .`);
- result, elapsed time, and current head / PR head binding;
- failure summary scoped to the failed surface or child scenario;
- whether the run is focused proof, full bucket proof, hosted-check readback, or
  scheduler-owned gate input.

For merge-ready, fast evidence can support troubleshooting and review context
but cannot satisfy the daily-execution-cli bucket. Full evidence must be paired
with review, fact-chain, PR metadata, hosted checks, release/no-release, and
scheduler-owned gate readback. For closeout, retained evidence must link the
full validation basis to the PR head, merge commit, target branch, and
`no_release` judgment or explicitly record a narrower scope rationale and
remaining risk.

Demo bootstrap fixture validation also exposes explicit local surfaces outside
the `loom` command matrix:

```bash
python3 tools/check_demo_bootstrap_fixture.py --surface generation
python3 tools/check_demo_bootstrap_fixture.py --surface canonicalization
python3 tools/check_demo_bootstrap_fixture.py --surface fixture-drift
python3 tools/check_demo_bootstrap_fixture.py --surface cleanliness
python3 tools/check_demo_bootstrap_fixture.py --surface aggregate
make loom-demo-new-project-generation-check
make loom-demo-new-project-canonicalization-check
make loom-demo-new-project-fixture-drift-check
make loom-demo-new-project-cleanliness-check
make loom-demo-new-project-check
```

The named surfaces are `demo-bootstrap-generation`,
`demo-bootstrap-canonicalization`, `demo-bootstrap-fixture-drift`, and
`demo-bootstrap-examples-cleanliness`; the aggregate surface is
`demo-bootstrap-fixture`. Evidence summaries that cite them must preserve the
exact command, current head / PR head binding, result, elapsed time where
reported, and whether the evidence is focused proof or aggregate bucket proof.

For parent closeout, the focused surface commands explain which behavior was
validated, while `make loom-demo-new-project-check` or
`tools/check_demo_bootstrap_fixture.py --surface aggregate` remains the
fail-closed aggregate proof. `make loom-demo-new-project-sync` is the only
intentional stable fixture refresh entry and must not be cited as validation
evidence for an unchanged fixture.

This covers #899 and #901 by asserting that required names appear in `loom help --json`, version output is structured, and installed-state positive and negative fixtures behave consistently.

For #906-#909 it also checks:

- empty targets classify as `uninstalled`;
- legacy `.loom/bin` surfaces are detected but not trusted as installed-state;
- mixed `.agents/skills`, skills registry, and plugin manifests classify as mixed legacy surfaces;
- valid installed-state makes `doctor` pass and `repair plan` no-op;
- invalid graph edge endpoints fail closed;
- `repair apply` remains a structured blocking command until mutation semantics are approved.

For #929-#943 it also checks:

- host-control, host, and skills command names are implemented in `loom help --json`;
- `loom host list` emits `loom-host-orchestration/v1`;
- `loom host install` fails closed without `--apply`;
- `loom skills list` emits the generated registry and root entry;
- `loom skills generate` fails closed without `--apply`;
- `loom skills package` emits package metadata for generated skills.

For #910-#914 it also checks:

- `install`, `upgrade`, and `rollback` fail closed before mutating state;
- `upgrade-plan` emits `loom-delivery-control/v1` actions without mutation;
- `verify` consumes `doctor` and returns the same readiness boundary.

For #1137 it also checks:

- `doctor` passes when installed-state does not declare suite command support;
- `doctor` consumes installed-state declared suite commands and `loom help --json`;
- declared suite command drift fails closed without running full suite validation.

For #924-#928 it also checks:

- scenario commands are implemented in `loom help --json`;
- flow-backed scenarios wrap the shared flow runtime;
- `spec` and `plan` fail closed with explicit carrier locators when absent;
- `closeout` is check-only and returns structured fallback guidance;
- `retire` exposes a non-mutating lifecycle contract.

For #1109-#1114 it also checks:

- `suite inspect` is declared as an implemented suite command in `loom help --json`;
- `suite inspect` stays read-only and emits the shared `loom-cli-output/v1` envelope;
- unknown, minimal, full, and missing-required-artifact suite states keep stable repo-relative locator output.
- `suite scaffold` is declared as an implemented suite command in `loom help --json`;
- `suite scaffold` dry-run stays read-only, reports minimal or full planned writes, preserves existing files, and keeps `created_locators` empty;
- `suite scaffold --apply` creates only missing scaffold files for the requested suite path, reports created locators, and preserves existing files;
- `suite scaffold --apply` fails closed for traversal items, absolute items, symlink paths, and non-file artifact placeholders before writing artifacts;
- `suite scaffold --suite full` plans and applies the standard six full-suite scaffold artifacts without creating evidence-map, consistency-analysis, task-carrier, review, merge-ready, closeout, generated skill, `/speckit.*`, or `.specify/` surfaces.
- `suite validate` is declared as an implemented suite command in `loom help --json`;
- `suite validate` stays read-only and covers pass, block, advisory, and not_applicable fixtures with structured readiness gaps.

#1138 wires `loom verify` to consume `suite validate` only when the invocation
passes `--item` or installed-state/profile requirements explicitly mark
`suite_validation` as required. Declared suite command support by itself remains
diagnostic and does not make optional suite parity universally blocking.
#1140 wires scenario skill flows to consume suite CLI JSON instead of embedded
suite readiness fallbacks: `loom build` exposes `suite_validation` and
`suite_carrier_validation`, and review/pre-review/merge-ready gate payloads
continue to consume `suite evidence validate` / `suite carrier validate`.
- `suite evidence validate` stays read-only and blocks stale evidence, HEAD / PR-head / reviewed-head binding drift, validation summary digest drift, missing present evidence source locators, and missing fresh verification evidence.
- `suite carrier validate` stays read-only and blocks missing carrier locators, invalid normalized status or relationship values, missing Work Item backlinks, primary carrier conflicts, deferred-as-completed, carrier truth conflicts, and Project/checklist/issue/PR host signal conflicts without promoting carrier done to completion truth.
