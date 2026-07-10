# WI-1844 Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1844.md`
- Host issue locator: `https://github.com/MC-and-his-Agents/Loom/issues/1844`
- Scope: release closeout-sync aftercare wrapper, focused regression coverage, and documentation boundary.
- Suite path: minimal.
- Current branch: `work/1844-release-closeout-sync`
- PR locator: pending

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| Work Item | `.loom/work-items/WI-1844.md` | required | authored Loom truth | Recheck after issue, branch, PR, release, or closeout state changes. |
| suite path decision | `.loom/specs/WI-1844/spec.md` | minimal | authored Loom truth | Recheck if scope expands beyond release closeout carrier synchronization. |
| implementation contract | `.loom/specs/WI-1844/implementation-contract.md` | required | authored Loom truth | Recheck after command behavior, output payload, or readback classification changes. |
| PR metadata | PR body | pending | GitHub host truth | Recheck after PR body or head SHA changes. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py` | S1-S2 and A1-A5 in `.loom/specs/WI-1844/spec.md`; docs boundary in `README.md`, `README.zh-CN.md`, and `docs/methodology/harness/cli-command-matrix.md` | work_item=WI-1844; issue=#1844; branch=`work/1844-release-closeout-sync`; head_sha=current PR head at review time | present | review; PR gate; merge-ready; closeout | Re-run focused checks and review after release closeout-sync behavior or documentation boundary changes. |
| EV-002 | test_evidence | `tools/check_cli_contract.py` | validation and test strategy in `.loom/specs/WI-1844/plan.md`; py_compile, release-readback contract, suite validate, and carrier validate commands recorded in `.loom/progress/WI-1844.md` | work_item=WI-1844; scope=release closeout-sync wrapper; validation_summary=.loom/progress/WI-1844.md | present | review; PR gate; merge-ready; closeout | Rerun the listed checks after code, docs, suite, carrier, or review input changes. |
| EV-003 | behavior_evidence | `.loom/progress/WI-1844.md` | EV-001 EV-002 dogfood dry-run for published release carrier terminalization with `loom release closeout-sync --target /Users/mc/dev/Loom --version v0.24.0 --commit 1aafb7fb031d997b7b497e277a525e308f766407 --item WI-1834 --pr 1840 --json --full-output` | work_item=WI-1844; dogfood_target=WI-1834 main worktree; release_pr=#1840; release_commit=1aafb7fb031d997b7b497e277a525e308f766407 | present | review; PR gate; merge-ready; closeout | Rerun after release readback, carrier closeout-sync, or wrapper behavior changes. |
| EV-004 | fresh_verification_input | `.loom/status/current.md` | EV-001 EV-002 EV-003 current validation summary and fact-chain status | work_item=WI-1844; reviewed_head=current PR head at review time; pr=pending | present | merge-ready; closeout; status | Mark stale and rerun validation/review if PR head, scope, or validation summary changes. |

## Suite Applicability

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| formal suite | minimal | Bounded release aftercare wrapper with focused regression coverage and no new publish or host mutation authority. | Suite path decision, evidence map, implementation contract, review, PR metadata, hosted checks, controlled merge, release readback, and closeout remain required. | Expand if scope grows into publishing, republishing, GitHub Release/npm mutation, automatic merge, multi-repo orchestration, new carrier/DSL, or release policy semantics. | `.loom/specs/WI-1844/spec.md` |
