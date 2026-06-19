# Native Dependency Contract

Loom treats GitHub native issue dependency as a host control mirror. It can prove blocker state and drift, but it does not become repo-authored truth.

## Vocabulary

Stable dependency drift kinds:

- `missing_native_edge`
- `unexpected_native_edge`
- `stale_native_edge`
- `open_blocker_executable_conflict`
- `native_dependency_unreadable`

Stable native read states and capability judgments:

- `present`
- `missing`
- `unsupported`
- `permission_denied`
- `unreadable`
- `read-only`
- `read-write`

## Read Semantics

The native dependency reader prefers GitHub GraphQL `blockedBy` / `blocking` and falls back only when the host capability is unreadable. It compares:

- repo-authored dependency statements
- issue body dependency machine blocks
- GitHub native `blockedBy` / `blocking` edges
- Project status when a Project read is requested

Unsupported or permission-denied native dependency reads are not interpreted as “no blockers.” They remain explicit host mirror gaps and must be visible to status, Project drift, merge-ready, and closeout.

`dependency_graph.findings[*].kind` uses the same vocabulary. `project_drift.findings[*].drift_kind` may project those findings into Project drift when the same evidence affects Project / merge-ready consumption.

## Gate Consumption

- `github-intake issue` reads dependency state before choosing a route and blocks on open blockers or unreadable host mirror capability.
- `resume` exposes dependency drift as a visible status step without requiring a Project read.
- `merge-ready` blocks when an open native blocker exists under a blocking governance profile or when a stale native dependency mirror would make the merge basis ambiguous.
- `closeout` blocks when Work Item, FR, or Phase closeout still has an open blocker or stale dependency mirror.
- Safe sync plans may propose dry-run `addBlockedBy` / `removeBlockedBy` actions only when proof comes from repo-authored or issue-authored dependency truth, or when a stale native edge points to a closed blocker. Every planned action must carry a proof locator and a verification step.

Project ordering can support diagnosis, but it is never sufficient proof for writing native dependency edges.
