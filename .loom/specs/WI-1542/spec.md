# WI-1542 Spec

## Suite Path

- Suite path: minimal
- Full-suite-artifacts not_applicable: rationale: WI-1542 is a bounded startup-audit implementation slice with a read-only CLI/runtime surface, focused regression tests, generated runtime parity, and demo bootstrap fixture evidence; consumer boundary: suite validate, build checkpoint, review, merge-ready, PR/CI, target branch validation, issue closeout, and milestone closeout consumers may use this minimal suite plus Work Item evidence without separate full-suite artifacts; recheck condition: require full suite artifacts if scope expands into hosted admission, closeout queue orchestration, post-merge closeout execution, closeout profile semantics, release behavior, security/privacy behavior, or external host writes.

## Objective

Detect active Work Item carrier drift before an operator starts work so milestone/12 lanes do not repeatedly discover stale terminal carriers, missing closeout sync, or shadow freshness problems during later merge/closeout gates.

## Acceptance Scenarios

### S1: Startup audit reports host-complete carrier residue

Given a retained Work Item has host-complete evidence but its repo-local progress remains non-terminal, `loom workspace audit --target . --json` returns `result=block`, classifies the finding as `carrier_closeout_required`, maps it to the stable classifier `carrier_refresh_needed`, and points the operator to carrier closeout sync.

### S2: Unrelated stale terminal carriers stay nonblocking

Given unrelated closed Work Items have terminal progress whose shadow or carrier freshness is stale, the audit includes only compact nonblocking samples and does not block the current active lane on unrelated terminal residue.

### S3: Current shadow freshness drift blocks with existing vocabulary

Given the current Work Item shadow source hashes are stale, the audit blocks with `shadow_source_hash_drift`, maps the classifier to `shadow_stale`, and directs the operator to refresh carrier/shadow evidence before proceeding.

## Non-Goals

- No hosted freeze admission or hosted gate behavior changes.
- No closeout queue/status UX implementation.
- No one-shot post-merge closeout run implementation.
- No classifier vocabulary expansion beyond consuming existing stable names.
- No closeout freeze profile semantic changes.
- No GitHub issue/PR body writes.
