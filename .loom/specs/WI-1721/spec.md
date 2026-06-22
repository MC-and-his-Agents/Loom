# Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1721 is a bounded CLI host readback change with issue-level acceptance and focused contract coverage. consumer boundary: suite validate, build, review, PR gate, hosted checks, and closeout may consume this minimal suite. recheck condition: require full suite if scope expands into version aggregation, upgrade-plan UX, broad fixture catalog, or v0.19.0 release closeout.
- Consumes:
  - Work Item / FR locator: issue #1721, `.loom/work-items/WI-1721.md`
  - Story Readiness: not required; this is a CLI host readback hardening item.
  - Story scenario locator: issue #1721 acceptance bullets.
  - Story Business Confirmation: not required; no business-domain semantics.
- Produces:
  - Scenario ids / locators: S1-S3 in this spec
  - Acceptance ids / locators: A1-A4 in this spec
  - Behavior evidence expectation: targeted CLI contract check plus live `host doctor` readback
- Locator:
  - Spec locator: `.loom/specs/WI-1721/spec.md`
- Provenance:
  - Source issue / PR / doc / conversation locator: GitHub issue #1721
  - Freshness rule: current branch head and PR metadata must match before merge.

## Goal

Let `loom host doctor --host codex` read and compare the three Codex plugin payload layers:

- source payload selected by Loom
- local marketplace source managed by `loom host install`
- Codex-owned runtime cache

## Scope

- In scope: read-only metadata/hash comparison, actionable freshness state, focused CLI contract coverage.
- Out of scope: repo-local plugin install, single SKILL install, Codex runtime cache writes, #1715 aggregate version output, #1716 upgrade-plan UX, v0.19.0 release.

## Key Scenarios

### Scenario S1

Given the source payload, marketplace source, and runtime cache all carry matching `plugin_payload_version` and `plugin_payload_hash`

When `loom host doctor --host codex --scope user --json` runs

Then it reports `plugin_payload_readback.freshness=already_current`.

### Scenario S2

Given the marketplace source is missing or differs from the source payload

When host doctor runs

Then it reports marketplace-source stale or missing and points to `loom host install --host codex --scope user --apply --json`.

### Scenario S3

Given the marketplace source is current but the Codex runtime cache is missing or stale

When host doctor runs

Then it reports runtime-cache missing or stale and points to Codex reload guidance without writing the cache.

## Behavior Evidence

- Scenario coverage:
  - S1 -> `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - S2 -> `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - S3 -> `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
- Expected evidence locator: `.loom/progress/WI-1721.md`
- Freshness rule: rerun targeted checks after any host readback code change.

## Exceptions And Boundaries

- Failure modes: missing source metadata, stale marketplace source, missing runtime cache, stale runtime cache.
- Operational boundaries: Loom reads Codex runtime cache but does not mutate it.
- Rollback or fallback expectations: remove the readback helper and contract assertions; existing host install/register paths remain unchanged.

## Acceptance Criteria

- [x] A1: Host doctor exposes source, marketplace source, and runtime cache layer metadata.
- [x] A2: Marketplace source drift is distinguishable from runtime cache drift.
- [x] A3: Freshness output includes the next minimal action.
- [x] A4: A focused contract check covers current, marketplace-stale, and runtime-stale states.
