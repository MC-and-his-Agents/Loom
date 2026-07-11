# Spec

## Suite Contract

- Suite path: minimal
- Consumes: [#2062](https://github.com/MC-and-his-Agents/Loom/issues/2062), Core PR #273, App PR #281, and passing Harbor PR #253.
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: this is a bounded regression in one checkpoint classifier with no new public API or governance path. consumer boundary: focused CLI contract tests, semantic review, PR gate, and release judgment consume this spec and plan. recheck condition: require full suite if scope changes review binding, terminal closeout, PR metadata, or host mutation semantics.
- Produces: Correct merge checkpoint consumption for explicit non-blocking status text.

## Goal

Allow reviewed implementation PRs to retain explanatory non-blocking status text without being mistaken for missing execution material.

## Scope

- In scope: blocker text classification, actionable missing-input diagnostics, focused regressions, generated runtime sync.
- Out of scope: semantic-review bypass, required-check bypass, terminal closeout bypass, product repository shims, or arbitrary natural-language blocker inference.

## Acceptance Criteria

- [ ] Core #273 `None. ... does not alter product scope` shape passes blocker classification.
- [ ] App #281 `... does not block this ... slice` shape passes blocker classification.
- [ ] A real blocker remains blocking and appears in `missing_inputs`.
- [ ] Review/carrier-only head binding and normal implementation checkpoint semantics remain enforced.
