# WI-1687 Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1687 is a bounded CLI metadata repair hardening change for an existing PR body metadata flow. consumer boundary: suite validate, review, PR gate, controlled merge, and closeout may consume this minimal spec, plan, evidence map, task carrier, and focused validation output. recheck condition: require full suite artifacts if scope expands into generic PR body rewriting, host issue mutation, `loom ship`, closeout policy, or release behavior.
- Work Item / FR locator: issue #1687 under FR #1685.
- Scenario locators: S1, S2, S3.
- Acceptance locators: A1, A2, A3.
- Spec locator: .loom/specs/WI-1687/spec.md
- Provenance: GitHub issue #1687.
- Freshness rule: Recheck if PR metadata binding priority, safe repair rules, or host write boundaries change.

## Goal

Let Loom tell an agent exactly how to repair a missing PR body issue backlink when the issue number is explicit and the PR metadata machine carrier plus PR head readback already agree.

## Scope

- In scope: `--issue` input for `pr-metadata`, deterministic `- Issue: #N` rendering, safe repair action diagnostics for missing human backlink, wrapper passthrough, generated mirrors, focused contract fixtures, and predecessor WI-1684 carrier terminalization required for workspace admission.
- Out of scope: automatic repair of head, branch, release, review, or closeout policy conflicts; generic PR body template rewrites; `loom ship`; host issue mutation; release packaging.

## Scenarios

### S1: Missing Issue Backlink Gets a Safe Repair Action

Given metadata preflight receives `--issue`
And the PR body machine carrier, PR head readback, and explicit CLI bindings agree
When the human PR body lacks an issue backlink
Then preflight blocks and returns a `missing_human_backlink` safe repair action with the exact next command.

### S2: Render And Update Preserve Machine Carrier Safety

Given metadata render or update receives `--issue`
When it rewrites the PR body
Then it adds or refreshes `- Issue: #N` while preserving machine carrier preflight and readback requirements.

### S3: Conflicting Bindings Stay Blocked

Given Work Item, branch, head, release, review, or closeout bindings conflict
When preflight runs
Then Loom does not produce a safe issue backlink repair action as a substitute for resolving the conflict.

## Acceptance Criteria

- [ ] A1: `loom pr metadata-*` and runtime `pr-metadata` accept and propagate `--issue`.
- [ ] A2: render/update can add a deterministic Issue backlink to the PR body.
- [ ] A3: metadata preflight emits a safe repair action only for missing issue backlink cases with agreed binding inputs.
