# WI-827 Spec

## Objective

Complete the middle capability aggregation batch and its prerequisite recovery chain so Loom can consume intake, native dependencies, host binding inspection, Project drift, `/goal` execution contracts, and advanced Governance Lint as one merge-readiness-centered flow.

## Required Outcomes

- #827 freezes the GitHub native dependency contract and taxonomy consumed by host binding and Project drift.
- #829/#830 expose native dependency graph state through `host-binding inspect` and Project drift checks, including missing, unexpected, stale, and native open-blocker conflicts.
- #848/#849/#850 define the repo companion / repo interop boundary and advanced architecture/boundary lint surface, including a Loom core hardcoding guard.
- #795/#796 route GitHub intake into `next_action` so host binding can consume intake provenance.
- #798/#799 provide `host-binding inspect` with `loom-host-binding-inspection/v1`, binding chain, Project item, dependency graph, provenance, freshness, findings, and fixed fallback semantics.
- #801/#802/#803 expose Project drift through status, resume/pre-review advisory surfaces, and merge-ready advisory/blocking consumption.
- #822/#823/#824/#825 define and consume `/goal` schema, resume bootstrap, delegated execution protocol, consistency checks, and closeout completion evidence.
- #797/#800/#820 receive parent progress and verification evidence for the completed child issue set.

## Non-Goals

- Do not bypass native `blocked_by` semantics or treat stale Project state as completed truth.
- Do not turn repo-specific guardian, path, or rule conventions into Loom core defaults.
- Do not replace GitHub, CI, review engines, Projects, or worktree host controls.

## Acceptance

- Runtime scripts, source references, generated `skills/` install surfaces, docs, fixtures, and tests stay aligned.
- `host-binding inspect`, Project drift, `/goal`, closeout, and hardcoding guard fixtures cover stale, drift, missing, unsafe, and hardcoding cases.
- Local validation and PR gate pass for PR #856 with `Loom Work Item: WI-827`.
- PR #856 reaches merge-ready, then controlled merge and issue/Project closeout are attempted; any host or permission blocker is recorded with owner and recovery state.
