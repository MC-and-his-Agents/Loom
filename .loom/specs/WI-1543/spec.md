# WI-1543 Spec

## Suite Path

- Suite path: minimal
- Full-suite-artifacts not_applicable: rationale: WI-1543 is a bounded CLI/read-only queue status slice with explicit issue scope, deterministic fixture coverage, generated runtime parity, and no host or carrier mutation behavior; consumer boundary: suite validate, build checkpoint, review, merge-ready, PR/CI, target branch validation, issue closeout, and milestone closeout consumers may use this minimal suite plus Work Item evidence without separate full-suite artifacts; recheck condition: require full suite artifacts if scope expands into queue apply/sync behavior, hosted admission, classifier taxonomy, closeout freeze profile semantics, release behavior, security/privacy behavior, or external host writes.

## Objective

Expose a read-only post-merge closeout residue queue/status command that classifies retained Work Items and suggests the next safe command without mutating GitHub, Project, PR, issue, worktree, or versioned Loom carriers.

## Acceptance Scenarios

### S1: Queue status is explicitly bounded before scanning

Given an operator runs `loom closeout queue status` without `--issue`, `--item`, or `--queue-file`, the command fails closed with `queue_input` instead of scanning every retained Work Item.

### S2: Closeout modes are machine-readable

Given retained Work Item fixtures for completed terminal metadata, terminal carrier missing metadata, active carrier with host completion, incomplete host completion, and missing host completion, the command emits `auto_no_op`, `light_carrier_sync`, `batched_closeout`, `full_closeout`, and `blocked` classifications with next action guidance.

### S3: Explicit filters fail closed when nothing matches

Given an operator supplies a nonexistent `--item` or `--issue`, the command returns `block` with the missing filter rather than reporting `auto_no_op`.

### S4: The command is read-only on all tested paths

Given normal fixtures, missing input, filter miss, or missing target paths, the command reports no host mutations and no carrier mutations; fixture snapshots do not change.

## Non-Goals

- No automatic PR merge, issue close, Project update, release publish, or host sync.
- No `apply` implementation for queue entries.
- No classifier taxonomy freeze beyond this command's local closeout mode vocabulary.
- No hosted admission or closeout freeze profile semantic changes.
