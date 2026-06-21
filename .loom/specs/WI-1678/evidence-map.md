# WI-1678 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1678.md
- Host issue locator: https://github.com/MC-and-his-Agents/Loom/issues/1678
- Scope: README product positioning, badge presentation, quick-start install prompt, and Loom carrier metadata for PR #1679.
- Suite path: formal-suite NA decision; evidence map remains required for review, PR gate, hosted checks, controlled merge, and closeout.
- Current branch: work/1678-agent-install-prompt
- PR locator: https://github.com/MC-and-his-Agents/Loom/pull/1679

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| Work Item | .loom/work-items/WI-1678.md | required | authored Loom truth | Recheck after issue, branch, PR, or closeout state changes. |
| suite path decision | .loom/specs/WI-1678/spec.md | formal-suite NA decision | authored Loom truth | Require minimal or full suite if the PR expands beyond README wording or WI-1678 carriers. |
| task carrier | .loom/specs/WI-1678/task-carrier.md | required | authored Loom truth | Recheck before PR gate, controlled merge, and closeout. |
| review record | .loom/reviews/WI-1678.json | required | authored semantic review | Re-review if non-carrier README or contract inputs change. |
| merge-ready basis | .loom/progress/WI-1678.md | required | current recovery truth | Refresh validation summary after head, PR metadata, or hosted check changes. |
| host state | https://github.com/MC-and-his-Agents/Loom/pull/1679 | required | GitHub PR and checks | Re-read PR head, body, checks, and merge state before controlled merge. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | README.md; README.zh-CN.md; .loom/specs/WI-1678/spec.md | WI-1678 README value proposition, quick-start prompt, badge rendering, and formal-suite NA scope | work_item=WI-1678; scope=README product value and agent install prompt; PR #1679 current head | present | review / merge-ready / PR gate / closeout / status | Recheck README parity, suite path scope, and review record after README or carrier changes. |
| EV-002 | test_evidence | git diff --check; npm --prefix packages/loom-installer run check:docs; python3 tools/check_release_surface.py --surface release-doc-contract; python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; python3 tools/loom_flow.py fact-chain --target . --item WI-1678; CODEX_EXPORT_GH_TOKEN=1 python3 tools/loom_flow.py checkpoint merge --target . --item WI-1678; CODEX_EXPORT_GH_TOKEN=1 python3 tools/loom_flow.py pr-gate check --target . --item WI-1678 --pr 1679 | WI-1678 validation entry and PR gate requirements | work_item=WI-1678; branch=work/1678-agent-install-prompt; PR #1679 current head | present | review / merge-ready / PR gate / hosted checks / closeout | Rerun local validation and PR gate after README, carrier, PR metadata, or review input changes. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1678.md | EV-001 EV-002 | work_item=WI-1678; current PR #1679 head; latest validation summary; authored review record | present | merge-ready / PR gate / controlled merge / closeout / status | Refresh progress/status, PR metadata readback, review binding, and hosted checks after any non-carrier input changes. |

## Suite Applicability

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| formal-suite | not_applicable | README-only documentation iteration; no runtime, installer, package, release, permission, host mutation, or legacy migration behavior changes. | Suite path decision only; review, evidence map, task carrier, fact-chain, PR gate, hosted checks, controlled merge, and closeout remain required. | Require a minimal or full suite if this PR expands beyond README wording, badge rendering, quick-start prompt framing, or WI-1678 carriers. | .loom/specs/WI-1678/spec.md |
