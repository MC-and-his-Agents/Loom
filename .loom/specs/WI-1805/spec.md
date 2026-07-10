# WI-1805 Spec

## Suite Path Decision

- Suite path: minimal
- Rationale: WI-1805 changes bounded Loom runtime contracts for host governance capability diagnosis, governance capability profiles, merge runtime enforcement, and release/evidence surfaces. A minimal suite is sufficient because the user-facing scope is already frozen in GitHub issue tree #1805/#1826-#1830 and the behavior is covered by executable contract tests.
- Consumer Boundary: suite validate, review, PR metadata, PR gate, merge-ready, release readiness, and closeout may consume this suite together with the focused tests and release readback.
- Recheck Condition: Re-run targeted unittest, npm smoke, package/release/version checks, CLI contract, PR metadata preflight/readback, review, and merge gate after any change to diagnosis classification, profile fields, advisory fallback policy, merge runtime enforcement, evidence wording, or package/plugin metadata.
- Scope Proof: `git diff origin/main...HEAD` must stay limited to #1805 host governance capability implementation, docs/fixtures/tests, v0.23.0 release metadata, and WI-1805 Loom carriers.
- Review Requirement: current_head_review_required
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: host governance capability is represented by existing Loom CLI/runtime/docs contracts plus focused executable tests, not by a new DSL or separate policy system. consumer boundary: review, PR gate, merge-ready, release readiness, and closeout consume this as minimal suite evidence only. recheck condition: require full suite artifacts if the work expands into a new policy DSL, credential model, host mutation automation, cross-host adapter, security/payment/data-migration profile, or unrelated milestone.

## Scenarios

- S1: Loom diagnoses GitHub host governance capability as `host_enforced`, `unconfigured`, `unavailable`, or `unreadable`, with setup guidance for missing or unreadable controls.
- S2: Loom defines `host-enforced` and `advisory/local-enforced` governance capability profiles, where advisory mode is explicitly low assurance and not strong governance.
- S3: `loom merge check/run` consumes governance capability profiles, defaults to host-enforced, fail-closes on unproven strong claims, and requires explicit advisory opt-in.
- S4: Advisory/local-enforced mode still checks current head, semantic review, PR gate, CI rollup, and head drift; it only relaxes proof of host-enforced controls.
- S5: PR metadata, merge evidence, release/readback surfaces, closeout/status docs, and v0.23.0 release readiness record governance mode without misrepresenting advisory fallback as host-enforced.

## Acceptance

- [x] A1: Host governance diagnosis is machine-readable and classifies configured, unconfigured, unavailable, and unreadable GitHub control-plane states.
- [x] A2: Profile contract documentation distinguishes host-enforced from advisory/local-enforced and records high-risk fallback boundaries.
- [x] A3: Merge runtime consumes governance mode/profile inputs and blocks strong claims when host enforcement cannot be proven.
- [x] A4: Advisory/local-enforced remains explicit opt-in and does not bypass review, PR gate, CI rollup, current-head, or head drift checks.
- [x] A5: PR metadata, closeout policy, status/readback docs, and release readiness evidence record governance mode.
- [ ] A6: PR #1831 passes current-head review, hosted gates, merge, v0.23.0 publish/readback, and #1805/#1826-#1830/milestone closeout.
