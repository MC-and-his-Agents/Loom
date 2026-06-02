# WI-1204 Spec

## Suite Contract

- Suite path: minimal
- Work Item / FR locator: #1204 / #1205-#1211
- Path decision provenance: #1204 changes downstream plugin layout behavior and diagnostics but remains bounded to CLI payload layout, installed-state graph, docs, and regression fixtures.
- Full-suite-artifacts not_applicable: rationale: this iteration has a bounded CLI/layout contract and does not need research, external API contracts, or a full readiness checklist beyond the issue tree; consumer boundary: suite validate, build checkpoint, review, merge-ready, PR/CI, target branch validation, and issue closeout consume this minimal suite plus Work Item evidence; recheck condition: promote to full suite if the work changes workstation registration semantics, destructive migration behavior, or host-private Codex truth handling.

## Scope

Make downstream Codex plugin mode use `plugins/loom/skills/` as the canonical Loom skills payload and stop writing or requiring downstream top-level `skills/` by default.

## Scenarios

- S1: `loom host install --host codex --mode plugin --target <fixture> --apply --json` writes `plugins/loom/.codex-plugin/plugin.json`, `plugins/loom/skills/`, and `.loom/installed-state.json`, but not target root `skills/`.
- S2: `loom host verify`, `loom skills check`, and `loom installed-state validate` pass for a plugin fixture without top-level `skills/`.
- S3: `loom detect`, `loom doctor`, `loom repair plan`, and `loom upgrade-plan` classify old duplicate top-level Loom `skills/` as legacy migration residue, while mixed or target-owned `skills/` fails closed to manual review.
- S4: README, Codex install docs, unified install docs, host adapter matrix, installed-state v2 docs, release checks, and generated skills docs agree with the downstream plugin layout and #1196 workstation registration boundary.

## Acceptance Criteria

- AC-1: Plugin install no longer writes or plans downstream top-level `skills/` for plugin mode.
- AC-2: Plugin-mode installed-state exports a graph with `plugin-embedded-skills` at `plugins/loom/skills/` and no required top-level `skills` layer.
- AC-3: Verification, skills check, detection, doctor, repair plan, and upgrade-plan handle plugin fixtures without top-level `skills/`.
- AC-4: HotCP-style old duplicate layout receives a non-mutating migration recommendation, and target-owned `skills/` is not deleted or treated as Loom-owned.
- AC-5: Required checks pass locally and on PR/target branch before #1205-#1211 and #1204 closeout.

## Applicability Boundary

- Full-suite-artifacts not_applicable: rationale: the issue tree already decomposes layout contract, write boundary, installed-state graph, diagnostics, migration planning, fixtures, and docs closeout; consumer boundary: review and merge-ready must verify those surfaces through code, docs, fixture, and command evidence; recheck condition: require full suite artifacts if this expands into a new profile system, destructive repair apply, or host-private workstation registration redesign.
