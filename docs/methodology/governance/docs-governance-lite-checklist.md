# Docs-Governance Lite Checklist

This file defines the Loom docs-governance lightweight path checklist.

It consumes the generic change intensity model in
[change-governance-intensity.md](./change-governance-intensity.md), the Loom
mapping in
[loom-governance-intensity-mapping.md](./loom-governance-intensity-mapping.md),
and the gate consumption contract in
[tiered-gate-consumption-contract.md](../harness/tiered-gate-consumption-contract.md).

The checklist is a governance-path decision aid. It does not implement gate
parser behavior, metadata carriers, fixtures, runtime behavior, generated
skills, release mechanics, or parent closeout.

## 1. Position

`docs-governance` means a documentation change that freezes or clarifies how
Loom governance, harness orchestration, templates, adoption, evidence, or skill
entrypoints should be interpreted.

The lightweight path exists for low-risk governance documentation where the
formal suite artifacts are not useful for the current scope, but the change
still needs review, fact-chain evidence, PR binding, checks, no-release
judgment, and closeout.

It is narrower than general docs-only:

- general docs-only can include copy, links, formatting, examples, or local
  explanations
- docs-governance changes alter how agents should classify, execute, review, or
  close out work
- docs-governance lite is allowed only when that governance clarification is
  local, reversible, and not a machine-consumed gate or runtime contract

## 2. Applicability

The docs-governance lightweight path may be used only when all conditions below
are true:

- The diff is limited to methodology docs, template explanations, landing links,
  or current Work Item carrier/review/status evidence.
- The change clarifies an existing Loom governance boundary rather than creating
  a new machine-consumed field, parser requirement, runtime behavior, fixture
  expectation, release behavior, or generated skill contract.
- The change can be reviewed from the current diff and existing upstream
  contracts without requiring a new formal spec, implementation plan, fixture
  matrix, or runtime proof.
- The Work Item, branch, workspace, PR, PR head SHA, review record, and status
  surface can be bound to the same fact-chain.
- `Suite path: not_applicable` can be justified with rationale, consumer
  boundary, recheck condition, scope proof, and review requirement.
- No security, privacy, permission, data, migration, deployment, release,
  external account, production profile, or external-visible action is touched.
- The PR can record a no-release judgment with evidence that no runtime,
  package, CLI, generated skill, API, migration, or user-visible product surface
  changed.

Typical allowed examples:

- Adding a checklist that helps agents decide whether docs-governance lite is
  available.
- Linking the checklist from the governance landing page.
- Clarifying that docs-governance lite still requires current-head review,
  fact-chain, PR gate, controlled merge, no-release judgment, and closeout.
- Recording Work Item carrier evidence for the same docs-governance PR.

## 3. Upgrade Conditions

The path must upgrade to `standard` or `reinforced`, or return to intake, when
any condition below appears:

- The diff touches runtime code, `tools/`, gate implementation, parser behavior,
  CLI metadata, fixtures, generated runtime copies, packaged skill payloads,
  release mechanics, AGENTS root rules, or host automation behavior.
- The change defines a new machine-consumed field or changes allowed values for
  a gate, carrier, PR body machine block, schema, or fixture.
- The change becomes a shared upstream contract that downstream Work Items will
  consume before review has frozen the current head.
- The not-applicable rationale cannot prove scope, consumer boundary, recheck
  condition, or review requirement.
- Review finds that the final reviewer would need to make admission, scope, risk,
  or product behavior judgments that should have been settled before review.
- PR body, Work Item, recovery entry, status surface, review record, branch,
  workspace, or head SHA disagree.
- Hosted checks, PR gate, controlled merge, release/no-release evidence, or
  closeout cannot consume the same fact-chain.
- Any external-visible, security, permission, data, deployment, migration,
  release, or irreversible state risk is discovered.

Upgrade is not a failure. It means the lightweight evidence no longer matches
the actual risk.

## 4. Minimum Evidence

A docs-governance lite PR must retain the evidence below.

| Evidence | Minimum requirement |
| --- | --- |
| Goal and scope | Issue and Work Item state identify the docs-governance checklist scope and forbidden implementation areas. |
| Path rationale | PR or carrier states `governance_intensity: light` or equivalent rationale, `change_class: docs_governance`, and why formal suite artifacts are not useful for this scope. |
| Scope proof | Current diff shows only methodology docs, landing links, and current carrier/review/status evidence; no runtime, gate, CLI metadata, fixture, release, generated payload, or external-visible surface changed. |
| Suite decision | `Suite path: not_applicable` is recorded with rationale, consumer boundary, recheck condition, scope proof, and review requirement. |
| Fact-chain | Work Item, recovery entry, status surface, branch, workspace, PR, and head SHA resolve to the same item. |
| Review | Authored current-head review or equivalent review record approves the exact PR head and validation summary. |
| PR metadata/readback | PR body binds issue, Work Item, branch, workspace, head SHA, validation, and no-release judgment; readback matches the rendered body before review/merge-ready. |
| Validation | `git diff --check` and focused docs/static checks pass; additional checks run only when the diff expands into their surface. |
| PR gate and hosted checks | Required PR gate and hosted checks pass or produce a classified blocker; they are not replaced by the lightweight path. |
| Release judgment | PR records `no_release` with evidence that no runtime, CLI, package, generated skill, API, migration, release, or user-visible product surface changed. |
| Controlled merge | Merge uses the controlled merge wrapper and consumes fresh PR gate/check/readback evidence. |
| Closeout | Post-merge closeout consumes PR merge commit, target branch, issue state, no-release evidence, and terminal repo carrier truth. |

Missing evidence is not satisfied by saying "docs-only". Each missing or
not-applicable input needs a rationale and a recheck condition.

## 5. Not-Applicable Locator

For docs-governance lite, the suite decision should be expressed as:

```text
Suite path: not_applicable
Rationale: The change is a docs-governance checklist or clarification that does
not define runtime behavior, gate parser behavior, CLI metadata, fixtures,
generated skill payloads, release mechanics, or external-visible behavior.
Consumer boundary: Review, PR gate, merge-ready, and closeout may consume this
as a formal-suite artifact bypass only. They must still require fact-chain,
current-head review, checks, no-release evidence, controlled merge, and
post-merge closeout.
Recheck condition: Re-evaluate and upgrade if the diff expands into runtime,
tools, gate/parser fields, metadata carriers, fixtures, generated payloads,
release mechanics, AGENTS root rules, external-visible behavior, or downstream
machine-consumed semantics.
Scope proof: Current diff and PR body show only allowed docs-governance and
current carrier/review/status evidence changes.
Review requirement: Current-head docs/governance review is required.
```

The locator proves only that formal suite artifacts are not applicable. It does
not prove review approval, merge readiness, no-release, or closeout.

## 6. Follow-Up Boundary

If this checklist reveals a need for a new field, enum, parser diagnostic, gate
behavior, fixture, or release evidence format, record the dependency for the
owning follow-up instead of implementing it here:

- #1321 owns governance intensity metadata carrier implementation.
- #1322 owns docs-governance lightweight gate behavior.
- #1323 owns upgrade and misuse fixture coverage.
- #1324 owns parent closeout and release/no-release evidence convergence.

Until those implementation issues are complete, this checklist is the reviewed
docs-governance source contract, not proof that automation already consumes the
new semantics.

## 7. One-Line Rule

Docs-governance lite can make formal suite evidence lighter, but it cannot make
review, fact-chain, head binding, PR gate, checks, no-release judgment,
controlled merge, or closeout optional.
