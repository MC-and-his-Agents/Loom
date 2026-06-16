# WI-1235 Implementation Contract

- Work Item: WI-1235
- Issue: #1235
- Branch: work/1235-safe-repair-sync
- Suite path: full

## Approved Spec

This implementation consumes:

- `.loom/specs/WI-1235/suite-index.md`
- `.loom/specs/WI-1235/spec.md`
- `.loom/specs/WI-1235/plan.md`
- `.loom/specs/WI-1235/contracts.md`
- `.loom/specs/WI-1235/evidence-map.md`
- `.loom/specs/WI-1235/task-carrier.md`

The implementation review record must bind to the current PR head, or later drift must be limited to review/status/shadow carrier paths accepted by the gate.

## Write Scope

The implementation may write only:

- `tools/loom.py`
- `tools/check_cli_contract.py`
- `src/skills/shared/scripts/loom_flow.py`
- `skills/shared/scripts/loom_flow.py`
- `skills/loom-adopt/.loom-runtime/shared/scripts/loom_flow.py`
- `skills/loom-build/.loom-runtime/shared/scripts/loom_flow.py`
- `skills/loom-handoff/.loom-runtime/shared/scripts/loom_flow.py`
- `skills/loom-init/.loom-runtime/shared/scripts/loom_flow.py`
- `skills/loom-merge-ready/.loom-runtime/shared/scripts/loom_flow.py`
- `skills/loom-pre-review/.loom-runtime/shared/scripts/loom_flow.py`
- `skills/loom-resume/.loom-runtime/shared/scripts/loom_flow.py`
- `skills/loom-retire/.loom-runtime/shared/scripts/loom_flow.py`
- `skills/loom-review/.loom-runtime/shared/scripts/loom_flow.py`
- `skills/loom-spec-review/.loom-runtime/shared/scripts/loom_flow.py`
- `skills/loom-story/.loom-runtime/shared/scripts/loom_flow.py`
- WI-1235 Loom work item, progress, build evidence, suite, status, shadow, and review carriers

## Runtime Contract

- `loom repair plan` must remain non-mutating.
- `loom repair apply` may mutate only repo-local carrier closeout files for the explicit host-complete issue selected by `--issue`.
- The carrier repair write set is limited to the retained progress carrier, `.loom/status/current.md`, and `.loom/bootstrap/init-result.json`.
- Host truth may be read through GitHub APIs, but the repair command must not close issues, update Projects, merge PRs, create releases, tag, publish npm packages, or perform any other host mutation.
- Explicit issue ownership is required for active carrier repair. Missing, mismatched, ambiguous, or multi-issue locator evidence must fail closed.
- Mixed carrier repair and installed-surface repair actions must fail before any write.
- Generated skills runtime copies must match the source shared runtime behavior.

## Validation Plan

Required validation before review/merge-ready consumption:

- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/loom.py tools/check_cli_contract.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py`
- `python3 tools/loom.py suite validate --target . --item WI-1235 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1235 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1235 --json`
- `python3 tools/loom.py fact-chain --target . --json`
- `python3 tools/loom.py build --target . --item WI-1235 --build-evidence .loom/progress/WI-1235-build-evidence.json --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface aggregate`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only`
- PR metadata preflight/readback against the current PR body and head SHA
- Hosted required checks on the current PR head
- Loom review, PR gate, merge-ready, controlled merge, and post-merge closeout readback

## Risks And Rollback

Primary risks:

- repair apply could close out the wrong active carrier if issue ownership is inferred instead of explicit
- mixed repair actions could partially write installed-surface or carrier state
- generated runtime drift could make skill entrypoints behave differently from source
- write ordering could leave progress/status/init-result partially updated

Rollback boundary:

- revert the WI-1235 PR commits before dependent #1236/#1237 work consumes the behavior
- no host issue, Project, release, tag, or npm state needs rollback because the repair command does not mutate host state
- if a gate rejects review-head or PR metadata binding, refresh only the affected carrier/review/PR metadata and rerun the relevant gate

## Host Binding

The implementation binds to:

- GitHub issue #1235
- branch `work/1235-safe-repair-sync`
- parent FR #1228 as dependency context only

The PR body machine carrier must name `loom_work_item: WI-1235`, branch `work/1235-safe-repair-sync`, the current `head_sha`, `governance_intensity: reinforced`, `change_class: runtime`, `suite_path: full`, `review_requirement: current_head_review_required`, `fact_chain_required: true`, `pr_gate_required: true`, `release_judgment: no_release`, and `closeout_required: true`.
