# WI-1279 Implementation Contract

- Suite path: minimal

## Contract Surface

- `tools/loom_check.py` and shared runtime copies expose `--source-surface retire-workspace`.
- `retire-workspace` executes retire, purity, and workspace cleanup fixture checks under a stable named source surface and step name.
- `source-self-fixture` remains an aggregate and continues to include `review-run`, `merge-gate`, `closeout-reconciliation`, `retire-workspace`, and the remaining source-self fixture checks.
- Existing `review-run`, `merge-gate`, `closeout-reconciliation`, and aggregate `source-self-fixture` names are not renamed.
- Generated skills runtime `loom_check.py` copies stay aligned with the canonical shared runtime.
- Demo consumer `.loom/bin/loom_check.py` remains manifest-aligned and is not refreshed by #1279.

## Consumer Boundary

- Review and merge gates consume this contract through the focused `retire-workspace` source surface, the aggregate `source-self-fixture` surface, generated skills parity, PR metadata, hosted checks, and WI-1279 carriers.
- #1280 and #1258 do not consume this contract until #1279 is merged and read back.

## Non-Goals

- Do not implement installed-runtime or parent closeout fixture surfaces in WI-1279.
- Do not change release, package, workflow, or user-visible retire/workspace behavior beyond exposing the named diagnostic source surface.
- Do not run scheduler-owned review artifacts, guardian/loom_check gate consumption, controlled merge, post-merge readback, or closeout.

## Validation Binding

- `python3 tools/loom_check.py --profile source --source-surface retire-workspace .`
- `python3 tools/loom_check.py --profile source --source-surface source-self-fixture .`
- `python3 tools/loom.py skills check --target . --json`
