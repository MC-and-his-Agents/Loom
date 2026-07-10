# WI-1891 Spec

## Suite Contract

- Suite path: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1891 is a narrow publication-catalog Work Item under FR #1889 that adds one Codex marketplace catalog file for the already packaged Loom plugin and does not introduce a new runtime workflow, CLI behavior, or repo adoption mechanism; consumer boundary: suite validate, review, PR gate, merge-ready, #1892 follow-up planning, and closeout may consume this minimal suite together with the retained #1890 marketplace-contract checker evidence; recheck condition: require full suite artifacts if this work expands into workstation upgrade orchestration, automatic plugin installation, repo adoption mutation, broader install-boundary documentation, or legacy migration behavior.
- Consumes:
  - Work Item / FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1891
  - Parent FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1889
  - Parent Phase locator: https://github.com/MC-and-his-Agents/Loom/issues/1888
  - Story Readiness consumed state: not required for this catalog-publication WI; rationale: the GitHub issue tree and #1890 contract define the accepted scope; consumer boundary: suite validate, review, PR gate, and closeout for #1891; recheck condition: require story readiness if this expands into user-facing installation or upgrade behavior.
  - Story Business Confirmation consumed state: not required for this catalog-publication WI; rationale: the accepted business semantic is publishing the already packaged Loom plugin as a Codex marketplace source; consumer boundary: suite validate, review, PR gate, and closeout for #1891; recheck condition: require business confirmation if repo adoption or workstation upgrade behavior changes.
- Produces:
  - Scenario ids / locators: S1 published marketplace catalog, S2 Codex marketplace parse, S3 installed-state boundary.
  - Acceptance ids / locators: A1-A5 below.
  - Behavior evidence expectation: catalog file, targeted plugin manifest, temporary-home Codex parse, and source checker validation.
- Locator:
  - Spec locator: `.loom/specs/WI-1891/spec.md`
- Provenance:
  - Source issue / PR / doc / conversation locator: #1888, #1889, #1890, #1891, milestone #25 planning discussion.
  - Freshness rule: rerun validation after any catalog, plugin manifest, checker, PR metadata, review, hosted-check, or closeout change.

## Goal

Publish a Codex marketplace catalog from the Loom source repository so Codex can discover the existing `plugins/loom` plugin from this repository root.

## Scope

In scope:

- Add `.agents/plugins/marketplace.json`.
- Declare exactly one plugin entry named `loom`.
- Point the entry to local source path `./plugins/loom`.
- Use `policy.installation: AVAILABLE`, `policy.authentication: ON_INSTALL`, and `category: Productivity`.
- Verify Codex can parse the repository marketplace root without writing user Codex configuration.

Out of scope:

- Changing the Loom plugin payload.
- Installing or upgrading the plugin in the user's real Codex profile.
- Implementing workstation registry, global runtime cache, upgrade orchestration, or legacy migration behavior.
- Documenting the broader marketplace/plugin/CLI/repo adoption boundary; #1892 owns that slice.

## Scenarios

### S1: Published Marketplace Catalog

Given the Loom source repository contains `.agents/plugins/marketplace.json`
When the catalog is parsed
Then it exposes exactly the `loom` plugin and points to `./plugins/loom`.

### S2: Codex Marketplace Parse

Given a temporary Codex home
When `codex plugin marketplace add /Users/mc/dev/Loom` runs against this repository
Then Codex accepts the marketplace root as `loom` without modifying the user's real Codex configuration.

### S3: Installed-State Boundary

Given the catalog is source distribution metadata
When Loom source checks inspect it
Then it is accepted as a published catalog and does not contain workstation installed-state or cache fields.

## Acceptance

- [ ] A1: `.agents/plugins/marketplace.json` is valid JSON and contains only the `loom` plugin entry.
- [ ] A2: The entry source is local `./plugins/loom`.
- [ ] A3: Codex accepts the repository root as a marketplace in a temporary home.
- [ ] A4: `loom_check --profile source --source-surface source-self-fixture .` passes with the catalog present.
- [ ] A5: #1892 remains open for install-boundary documentation.

## Behavior Evidence

- Story scenario mapping: no separate story artifact; #1891 is an issue-defined catalog publication Work Item.
- Story readiness locator or rationale: no separate story artifact exists; #1889/#1890/#1891 provide the accepted scope; consumer boundary: suite validate, review, PR gate, and closeout for #1891; recheck condition: require story readiness if user-facing installation behavior is added.
- Story business confirmation locator or rationale: business semantics are limited to making Loom discoverable as a Codex marketplace source while leaving install-boundary documentation to #1892; consumer boundary: suite validate, review, PR gate, and closeout for #1891; recheck condition: require business confirmation if adoption or workstation upgrade behavior changes.
- Scenario coverage:
  - S1 -> `.agents/plugins/marketplace.json` and JSON validation.
  - S2 -> temporary-home `codex plugin marketplace add /Users/mc/dev/Loom`.
  - S3 -> source `loom_check` validation after #1890 checker contract.
- Expected evidence locator: `.loom/specs/WI-1891/evidence-map.md`
- Freshness rule: refresh validation after any catalog, plugin manifest, checker, PR metadata, review, hosted-check, or closeout change.
- Execution ledger acceptance locator: `.loom/progress/WI-1891.md`
