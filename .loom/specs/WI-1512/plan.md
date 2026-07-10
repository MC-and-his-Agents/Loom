# WI-1512 Plan

## Suite Contract

- Suite path consumed: minimal
- Consumes:
  - Spec locator: `.loom/specs/WI-1512/spec.md`
  - Scenario ids: S1, S2, S3
  - Acceptance ids: A1-A5
  - Story Readiness: issue-graph provenance in #1512 and #1505.
  - Story Business Confirmation: issue-graph provenance in #1512 and #1505.
- Produces:
  - Hosted admission runtime implementation.
  - Workflow readback wiring.
  - CLI contract fixture evidence.
  - Generated runtime/demo fixture refresh.
- Locator:
  - Plan locator: `.loom/specs/WI-1512/plan.md`
- Freshness rule: update this plan if hosted admission schema, workflow inputs, or classifier fields change.

## Implementation Goal

Deliver a hosted admission slice that lets CI recompute current gate freeze inputs from trusted PR readback artifacts and fail closed on stale PR body or retained snapshot evidence.

Explicitly deferred: closeout freeze admission profiles (#1532), closeout-specific gates (#1533), docs/skills convergence (#1514/#1534), and one-shot post-merge closeout run (#1555).

## Suite Path

- Full-suite-artifacts not_applicable: rationale: WI-1512 uses the minimal suite because the implementation is a bounded runtime/workflow gate hardening slice with targeted contract fixtures and no independent product story, research dossier, readiness checklist, or multi-contract design package; consumer boundary: suite validate, spec review, implementation review, merge-ready, hosted CI, downstream #1532/#1533 consumers, and milestone closeout may consume this minimal plan only for hosted PR gate admission; recheck condition: require full suite artifacts if scope expands into closeout profile semantics, one-shot closeout run orchestration, release/no-release behavior, security/privacy behavior, external host writes beyond readback, or a user-facing workflow.

## Phases

### Phase 1: Runtime Hosted Admission

- Objective: Add hosted admission payload construction inside `pr-gate check`.
- Deliverable: `loom-hosted-freeze-admission/v1` payload with recomputed freeze, carrier refresh, shadow freshness, readback, artifact comparison, blocking inputs, and classifier output.
- Exit condition: focused fixture passes for positive hosted admission.

### Phase 2: Drift And Snapshot Failure Coverage

- Objective: Fail closed on hosted PR body drift and retained freeze snapshot mismatch.
- Deliverable: targeted fixture cases and classifier categories.
- Exit condition: targeted fixture blocks the intended drift cases without weakening normal PR gate checks.

### Phase 3: Host Workflow Consumption

- Objective: Make hosted `loom-pr-merge-gate` provide PR JSON/body readback to runtime.
- Deliverable: workflow step writes `.loom/runtime/pr/pr-readback.json` and `.loom/runtime/pr/pr-body-readback.md`, then invokes `pr-gate check` with hosted admission arguments.
- Exit condition: hosted gate consumes readback inputs and no longer relies only on local PR body artifacts.

### Phase 4: Generated Runtime Sync

- Objective: Keep source, installed skill runtime copies, and demo bootstrap fixture aligned.
- Deliverable: generated runtime copies and `examples/new-project` bootstrap hash refresh.
- Exit condition: generated-tree-drift and demo bootstrap checks pass.

## Constraints

- Do not mutate shared GitHub truth or PR body from subagents.
- Do not directly edit `/Users/mc/dev/Loom`; implementation stays in `/Users/mc/dev/Loom-1512-hosted-freeze-admission-v2`.
- Do not invent a duplicate freeze schema; consume `loom-gate-freeze/v1`.
- Do not loosen fact-chain, review, PR metadata, or merge checkpoint enforcement to make hosted admission pass.

## Validation

- Automated checks:
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`
  - `make loom-demo-new-project-check`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py skills/loom-adopt/.loom-runtime/shared/scripts/loom_flow.py skills/loom-build/.loom-runtime/shared/scripts/loom_flow.py skills/loom-handoff/.loom-runtime/shared/scripts/loom_flow.py skills/loom-init/.loom-runtime/shared/scripts/loom_flow.py skills/loom-merge-ready/.loom-runtime/shared/scripts/loom_flow.py skills/loom-pre-review/.loom-runtime/shared/scripts/loom_flow.py skills/loom-resume/.loom-runtime/shared/scripts/loom_flow.py skills/loom-retire/.loom-runtime/shared/scripts/loom_flow.py skills/loom-review/.loom-runtime/shared/scripts/loom_flow.py skills/loom-spec-review/.loom-runtime/shared/scripts/loom_flow.py skills/loom-story/.loom-runtime/shared/scripts/loom_flow.py tools/check_cli_contract.py`
  - `git diff --check`
- Runtime evidence:
  - `python3 .loom/bin/loom_flow.py fact-chain --target . --item WI-1512`
  - `python3 tools/loom.py pr metadata-readback 1572 --surface merge_ready --readback-file .loom/runtime/pr/WI-1512-pr-readback.md --json`
  - `python3 tools/loom.py pr gate 1572 --surface merge_ready --item WI-1512 --body-file .loom/runtime/pr/WI-1512-pr-body.md --compare-body-file .loom/runtime/pr/WI-1512-pr-readback.md --json`
- Scenario validation mapping:
  - S1 -> targeted hosted admission fixture pass case.
  - S2 -> targeted hosted admission readback drift fixture.
  - S3 -> targeted hosted admission snapshot mismatch fixture.
- Fresh verification evidence:
  - PR #1572 head, PR body metadata readback, local validation summary, hosted check run ids.

## Test Strategy

- TDD expectation: fixture cases are authored in `tools/check_cli_contract.py` and run under `--surface pr-metadata`.
- Regression coverage:
  - Preserve existing PR metadata parser/preflight cases.
  - Add hosted admission inputs to fixture payload helper.
  - Cover pass, body drift, and snapshot mismatch.
- Acceptance test mapping:
  - A1 -> test evidence: fixture helper invokes runtime `pr-gate check` with hosted inputs.
  - A2 -> structural check: wrapper contract and `tools/loom.py pr gate` argument pass-through.
  - A3 -> structural check: workflow diff and hosted check evidence.
  - A4 -> test evidence: `tools/check_cli_contract.py --surface pr-metadata`.
  - A5 -> validation evidence: generated-tree-drift and demo bootstrap checks.

## Subagent Output Integration

- Owned outputs:
  - Read-only #1512 impact audit from Laplace.
  - #1512 v2 implementation from Ptolemy, reviewed and corrected by main thread.
  - Fact-chain blocker diagnosis from Mill.
  - CI classification from Franklin.
- Integration owner: main thread.
- Required evidence from each subagent: summary, locator, validation/failure classification, scope boundary statement.
- Review or reconciliation needed before merge-ready: main thread records formal review after implementation and carriers are stable.
- Handoff notes locator: current Codex milestone/12 thread.

## Dependencies

- Hard dependency consumed: #1510 stable gate freeze inputs.
- Soft dependency consumed: #1513 classifier categories and next-action style.
- Downstream consumers: #1532/#1533 closeout freeze/gate work and #1514/#1534 docs/skills convergence.
- Rollback boundary: hosted admission runtime/workflow wiring only; do not roll back completed #1510/#1513/#1554 work.

## Ready For Implementation

- [x] Spec is stable enough to implement.
- [x] Scope and non-goals are clear.
- [x] Story Readiness is covered by issue-graph provenance.
- [x] Story business semantics are covered by issue-graph provenance.
- [x] Validation path is defined.
- [x] Scenarios map to validation.
- [x] Regression coverage maps to fixture evidence.
- [x] Risks and dependencies are explicit.
