# WI-1834 Spec

## Suite Path Decision

- Suite path: minimal
- Rationale: WI-1834 changes bounded Loom CLI/runtime contracts for single-repo runtime-upgrade maintenance, version aliases, PR intent metadata, documentation, plugin/cache guidance, runtime copy parity, and fixture synchronization. A minimal suite is sufficient because the product scope is frozen in GitHub issue tree #1834-#1838 and the behavior is covered by executable CLI/package/runtime checks.
- Consumer Boundary: suite validate, review, PR metadata, PR gate, merge-ready, release readiness, and closeout may consume this suite together with focused tests and hosted check readback.
- Recheck Condition: Re-run runtime-upgrade CLI contract, PR metadata readback, package/runtime-copy checks, demo fixture check, hosted checks, review, and merge gate after any change to runtime-upgrade behavior, PR metadata fields, docs/help surfaces, plugin metadata/hash, or PR head.
- Scope Proof: `git diff origin/main...HEAD` must stay limited to #1834 single-repo runtime-upgrade implementation, docs, CLI contract fixtures, runtime copies, plugin metadata/hash, examples/new-project fixture sync, and WI-1834 Loom carriers.
- Review Requirement: current_head_review_required
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: this is a constrained runtime-maintenance CLI flow represented by existing Loom CLI/runtime/docs contracts plus focused executable checks, not a new policy language or separate planning model. consumer boundary: review, PR gate, merge-ready, release readiness, and closeout consume this as minimal suite evidence only. recheck condition: require full suite artifacts if the work expands into multi-repo batch automation, new host mutation semantics, credential management, cross-host adapters, security/payment/data-migration upgrade profiles, or unrelated milestones.

## Scenarios

- S1: `loom runtime-upgrade status` reports current Loom CLI, target repo workflow pin, and local Codex plugin/cache state as separate freshness layers.
- S2: `loom runtime-upgrade prepare` supports dry-run/apply for repo workflow pin updates and repo-local maintenance carriers without mutating user-level Codex plugin/cache state.
- S3: Stale or unreadable Codex plugin/cache state emits guidance for `loom host doctor/install/register --host codex --scope user` without becoming a repo PR merge fact by default.
- S4: `loom runtime-upgrade check` fails closed on missing real Work Item, head drift, metadata drift, workflow pin drift, and missing PR metadata, while plugin/cache stale remains advisory unless explicitly required.
- S5: `loom runtime-upgrade closeout` guides merge commit, target branch, issue, and evidence locator handoff into closeout sync.
- S6: v0.24.0 release convergence runs only after PR #1839 merges and publishes/readbacks GitHub Release, npm package, package/plugin metadata, carrier terminal state, issue closeout, and milestone closeout.

## Acceptance

- [x] A1: Runtime-upgrade status exposes CLI, repo workflow pin, and Codex plugin/cache freshness separately.
- [x] A2: Runtime-upgrade prepare updates repo workflow pins and repo-local maintenance carriers only under `--apply`.
- [x] A3: Runtime-upgrade prepare/check do not run host install/register or write user-level Codex plugin/cache state.
- [x] A4: Runtime-upgrade check fails closed for repo PR/head/metadata/workflow drift and treats plugin/cache stale as advisory by default.
- [x] A5: `loom -v/--version`, `help --json`, CLI matrix, README, and README.zh-CN are synchronized, including badge sizing.
- [ ] A6: PR #1839 passes current-head review, hosted gates, merge, v0.24.0 release/readback, issue closeout, milestone closeout, and terminal carrier closeout.
