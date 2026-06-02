# WI-1204 Plan

## Suite Contract

- Suite path: minimal
- Suite path consumed: minimal
- Spec locator: .loom/specs/WI-1204/spec.md
- Plan locator: .loom/specs/WI-1204/plan.md
- Full-suite-artifacts not_applicable: rationale: #1204 is a bounded downstream plugin layout iteration with explicit child Work Items and concrete verification commands; consumer boundary: build, review, merge-ready, PR/CI, target branch validation, and issue closeout consume this plan plus fixture evidence; recheck condition: require full path if migration apply, workstation registration semantics, or host-private truth behavior changes.

## Steps

1. Freeze downstream plugin layout contract in docs: plugin embedded skills at `plugins/loom/skills/`, target root `skills/` is not default and remains target namespace.
2. Change Codex plugin install so plugin mode writes only plugin payload paths and `.loom/installed-state.json`.
3. Change installed-state graph so plugin mode uses `plugin-embedded-skills` and no required root `skills` layer.
4. Update verify, skills check, detect, doctor, repair plan, and upgrade-plan to consume the plugin embedded payload.
5. Add safe migration planning for old top-level Loom `skills/`, with manual review for mixed or target-owned skills.
6. Add regression fixtures for new plugin layout and old HotCP-style duplicate layout.
7. Run required local checks, open PR, validate CI, merge, validate target branch, and close #1205-#1211 then #1204 with evidence.

## Scenario Mapping

- S1 -> Steps 1, 2, and fixture install assertions.
- S2 -> Steps 3, 4, `host verify`, `installed-state validate`, and `skills check`.
- S3 -> Steps 4, 5, `detect`, `doctor`, `repair plan`, and `upgrade-plan`.
- S4 -> Steps 1, 6, 7, docs checks, release surface checks, and skills surface checks.

## Acceptance Mapping

- AC-1 -> test evidence: `loom host install --host codex --mode plugin --target <fixture> --apply --json` plus managed_writes/tree assertions.
- AC-2 -> test evidence: `loom installed-state validate --target <fixture> --json` plus graph assertions.
- AC-3 -> test evidence: `loom host verify`, `loom skills check`, `loom detect`, `loom doctor`, `loom repair plan`, and `loom upgrade-plan` fixture assertions.
- AC-4 -> test evidence: HotCP-style duplicate layout fixture and mixed target-owned skill fixture.
- AC-5 -> test evidence: `make loom-check`, `python3 tools/check_cli_contract.py`, `python3 tools/check_release_surface.py`, `python3 tools/skills_surface.py check`, docs surface checks, `git diff --check`, PR/CI, and target branch validation.

## Applicability Boundary

- Full-suite-artifacts not_applicable: rationale: the implementation is constrained to plugin layout, installed-state, checks, docs, and fixtures; consumer boundary: no full research or contracts artifact is required to review this bounded change; recheck condition: require full suite artifacts if the change introduces a new host profile system or mutating deletion workflow.
