# WI-1720 Spec

## Suite Contract

- Suite path: minimal
- Suite index locator, or N/A rationale: `.loom/specs/WI-1720`
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1720 is a bounded CLI/docs/fixture command-boundary change over existing install, upgrade, upgrade-plan, and host codex commands. consumer boundary: suite validate, build checkpoint, review, PR gate, merge-ready, and closeout may consume this minimal spec, plan, implementation contract, task carrier, evidence map, Work Item carriers, and targeted validation output. recheck condition: require full suite artifacts if scope expands into payload hash/freshness implementation, host source/cache readback, destructive migration apply semantics, release/version publishing, or a new `loom plugin` command surface.
- Consumes:
  - Work Item / FR locator: GitHub issue #1720.
  - Story Readiness confirmed locator, blocking locator, or N/A rationale: N/A; issue #1720 is already scoped as a bounded Work Item.
  - Story scenario locator, or N/A rationale: N/A; scenarios are authored below.
  - Story Business Confirmation confirmed locator, blocking locator, or N/A rationale: N/A; this is CLI boundary clarity, not business-domain behavior.
- Produces:
  - Scenario ids / locators: S1-S3.
  - Acceptance ids / locators: A1-A4.
  - Behavior evidence expectation: target install/upgrade outputs state they manage repository metadata only and point Codex plugin refresh intent to host commands.
- Locator:
  - Spec locator: `.loom/specs/WI-1720/spec.md`
- Provenance:
  - Source issue / PR / doc / conversation locator: GitHub issue #1720 and user execution request.
  - Freshness rule: Recheck after changes to `tools/loom.py`, `tools/check_cli_contract.py`, README docs, or WI-1720 carriers.

## Goal

- Make `loom install/upgrade --target <repo>` clearly mean target repository installed-state/adoption metadata management.
- Make `loom host doctor|install|register --host codex --scope user` the authoritative Codex workstation plugin provider path.

## Scope

- In scope:
  - CLI output summaries, failure reasons, and short host refresh guidance payloads.
  - `upgrade-plan --host codex` action wording that avoids implying target repo upgrade refreshes the Codex plugin cache.
  - Targeted contract checks and minimal README/source skills docs sync.
- Out of scope:
  - #1715 freshness report.
  - #1714 hash semantics or payload hash implementation.
  - `packages/loom-installer/**`, release version, npm publish, GitHub release, and release files.
  - New `loom plugin ...` command surface.

## Key Scenarios

### Scenario S1

Given a user runs `loom install --target <repo> --host codex`

When the command reports dry-run or apply output

Then it states that install writes target repository adoption metadata only and exposes a short action pointing plugin refresh to `loom host ...` commands.

### Scenario S2

Given a user runs `loom upgrade-plan --target <repo> --host codex`

When the plan is generated

Then it keeps installed-state and legacy surface actions separate from a `host-plugin-refresh-boundary` guidance action.

### Scenario S3

Given a user runs `loom upgrade --target <repo> --host codex`

When the command blocks without `--apply` or applies

Then the output says target repository installed-state metadata is being refreshed and does not imply Codex plugin cache refresh.

## Acceptance Criteria

- [x] A1: Target `install` output identifies repository adoption metadata as its mutation boundary.
- [x] A2: Target `upgrade-plan --host codex` includes a short host refresh boundary action pointing to `loom host doctor|install|register --host codex --scope user`.
- [x] A3: Target `upgrade` output identifies repository installed-state metadata as its mutation boundary.
- [x] A4: README, README.zh-CN, and `src/skills/README.md` agree on install/upgrade versus host plugin refresh command ownership.
