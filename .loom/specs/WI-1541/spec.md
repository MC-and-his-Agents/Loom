# WI-1541 Spec

## Suite Path

- Suite path: minimal
- Full-suite-artifacts not_applicable: rationale: WI-1541 is a bounded PR metadata carrier CLI/productization slice with deterministic wrapper/runtime contract coverage and no hosted admission, closeout gate, release, or post-merge mutation behavior; consumer boundary: suite validate, review, merge-ready, PR/CI, target branch validation, docs/skills convergence, and milestone closeout may consume this minimal suite only for PR metadata render/update/readback behavior; recheck condition: require broader suite artifacts if scope expands into hosted admission behavior, closeout-specific gate semantics, release behavior, security/privacy behavior, or non-PR host mutations.

## Objective

Make Loom expose a safe PR metadata render/update/readback surface so operators can generate the repo-specific machine carrier, write it to a host PR, read it back, and preflight the rendered/readback pair without manually editing the JSON block.

## Acceptance Scenarios

### S1: PR metadata can be rendered without host mutation

Given a Work Item id, branch, head SHA, and governance fields, `loom pr metadata-render` writes a repo-relative PR body artifact and validates the machine block locally.

### S2: PR metadata can be read back from an artifact or host PR

Given a rendered/readback body artifact, `loom pr metadata-readback` parses the machine block, legacy bindings, and governance fields, then reuses metadata preflight for comparison.

### S3: PR metadata can be updated end to end

Given a resolvable host PR, `loom pr metadata-update` renders the body, applies it through `gh pr edit --body-file`, reads the host body back, and validates the readback.

### S4: Closeout PRs can reuse the existing merge-ready carrier

Given a closeout surface, render/readback/preflight consume the repo's existing `merge_ready` PR metadata machine carrier without inventing a duplicate schema.

## Acceptance Criteria

- A1: `tools/loom.py pr --help` exposes `metadata-render`, `metadata-readback`, and `metadata-update`.
- A2: Runtime `pr-metadata` supports `render`, `readback`, `update`, and existing `preflight` without breaking `inspect` or `gate`.
- A3: Rendered machine blocks use `loom-repo-pr-metadata/v1` and parser `loom-pr-metadata-parser/v1`.
- A4: `metadata-update` writes only the target PR body and immediately reads it back for comparison.
- A5: Focused `tools/check_cli_contract.py --surface pr-metadata` covers wrapper/runtime contract behavior without live host writes.
- A6: Generated runtime copies stay in sync with the shared runtime source.

## Non-Goals

- Do not implement hosted gate admission #1512.
- Do not implement closeout-specific gate behavior #1533.
- Do not implement one-shot post-merge closeout run #1555.
- Do not change release/no-release closeout #1515 or final docs convergence #1514/#1534 beyond PR template guidance.
