# Spec

## Suite Path

- Suite path: minimal
- Rationale: WI-1230/WI-1231 are bounded command and carrier contract changes. They alter CLI/runtime parsing, explicit carrier write behavior, documentation, tests, and Loom carriers, but do not introduce new host products, data migrations, or broad runtime behavior.
- Consumer boundary: build, spec review, implementation review, merge-ready, PR checks, controlled merge, and post-merge closeout consume this minimal suite plus command/test evidence.
- Recheck condition: promote to full suite if scope expands into host mutation semantics beyond existing reconciliation sync, repair/apply flows, release behavior, or unrelated closeout gate behavior.
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1230/WI-1231 are bounded CLI/runtime/docs/test changes whose contract is fully carried by this minimal spec, plan, evidence map, task carrier, and methodology docs; consumer boundary: suite validate, spec review, implementation review, PR gate, merge-ready, controlled merge, and closeout may consume the minimal suite without treating skipped full-path artifacts as completed; recheck condition: require the full suite if this Work Item expands into new host mutation semantics, repair/apply flows, release behavior, or unrelated closeout gate behavior.

## Scenarios

- S1: A progress carrier with legacy terminal checkpoint text remains readable without a terminal metadata section.
- S2: `carrier closeout-sync` dry-run emits planned versioned carrier updates and does not mutate progress carriers or host state.
- S3: `carrier closeout-sync --apply` writes `Terminal Closeout Metadata` to the target progress carrier and reports `host_mutations: false`.
- S4: `workspace retire` remains local-only and continues to report no versioned carrier updates.
- S5: host closeout/reconciliation sync remains responsible only for GitHub control-plane alignment and does not write versioned repo carriers.

## Acceptance

- AC-1: Terminal closeout fields can be machine-read from progress carriers when present.
- AC-2: Legacy `retired`, `merged`, `closed`, and `done` checkpoint strings remain readable when structured metadata is absent.
- AC-3: Carrier sync produces reviewable repo diffs only under explicit apply semantics.
- AC-4: Carrier sync never mutates GitHub issue, PR, Project, branch, or worktree state.
- AC-5: CLI help, docs, tests, and generated runtime copies expose separate local retire, host sync, and carrier sync responsibilities.
