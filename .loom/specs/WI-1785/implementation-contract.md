# WI-1785 Implementation Contract

## Scope

- Hosted gate workflow owner: `.github/workflows/pr-merge-gate.yml`.
- Loom carriers: `.loom/work-items/WI-1785.md`, `.loom/progress/WI-1785.md`, `.loom/status/current.md`, `.loom/specs/WI-1785/*`, and `.loom/reviews/WI-1785*.json`.

## Required Behavior

- Hosted `loom-pr-merge-gate` must pass `--surface closeout` to `pr-gate check` when the PR body machine metadata declares `surface: closeout`.
- Hosted `loom-pr-merge-gate` must keep `merge_ready` for ordinary PRs, missing metadata, or malformed metadata.
- The workflow must continue to use the PR body readback from GitHub, not local template assumptions.
- The fix must not change `pr-gate` review semantics, release readback verdicts, or closeout carrier writeback behavior.

## Non-Goals

- No new PR metadata schema.
- No multi-surface PR body format change.
- No release workflow redesign.
- No branch cleanup or terminal cleanup automation.
