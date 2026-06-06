# WI-1289-1291 Implementation Contract

## Contract Boundary

- Suite path: minimal
- Consumes:
  - Spec locator: `.loom/specs/WI-1289-1291/spec.md`
  - Plan locator: `.loom/specs/WI-1289-1291/plan.md`
  - Evidence map locator: `.loom/specs/WI-1289-1291/evidence-map.md`
  - Task carrier locator: `.loom/specs/WI-1289-1291/task-carrier.md`
- Produces:
  - Controlled merge consumes current PR gate and retained PR gate evidence before host merge delegation.
  - PR gate, closeout, and reconciliation expose post-merge review bypass diagnostics with repair guidance.
  - Review records include `authored_at` for timing diagnostics.
  - Generated runtime copies and bootstrap manifests remain hash-aligned.

## Runtime Contracts

- `loom merge check` and `loom merge run` must fail closed when the retained PR gate result is stale, missing, bound to a different PR/head, or lacks authored semantic review approval.
- Controlled merge must evaluate `controlled_merge_consumption` before invoking `gh pr merge`.
- PR gate approval must come from an authored Loom review artifact with `decision: allow`, implementation review kind, matching validation summary, and consumable `semantic_review_disposition`.
- CI, GitHub review state, PR body text, shadow review output, or raw host status must not replace authored Loom semantic review approval.

## Post-Merge Diagnostics

- A merged PR whose Loom review is missing or authored after `mergedAt` must produce a post-merge review bypass diagnostic.
- The repair plan must classify such evidence as post-merge closeout/reconciliation evidence only.
- The repair plan must forbid backdating review records, treating CI/GitHub review as Loom approval, or marking a historical bypass as merge-before-review compliant.

## Parity Contracts

- `skills/shared/scripts/loom_flow.py`, `src/skills/shared/scripts/loom_flow.py`, `.loom/bin/loom_flow.py`, generated skill runtimes, and `examples/new-project/.loom/bin/loom_flow.py` must stay behaviorally synchronized for this surface.
- `.loom/bootstrap/manifest.json`, `.loom/bootstrap/init-result.json`, and example bootstrap manifests must record the current generated runtime hash.

## Validation Binding

- Automated strategy: `python3 tools/check_cli_contract.py`.
- Runtime parity strategy: `python3 .loom/bin/loom_flow.py runtime-parity validate --target .`.
- Generated fixture strategy: `python3 tools/check_demo_bootstrap_fixture.py` and `make loom-demo-new-project-check`.
- Surface strategy: `python3 tools/skills_surface.py check`, `python3 tools/check_release_surface.py`, `python3 tools/check_npm_package.py`, and `git diff --check`.
- Recheck condition: rerun validation after any change to PR gate, controlled merge, review artifact semantics, post-merge diagnostics, generated runtime copies, bootstrap manifests, PR body metadata, or carrier bindings.
