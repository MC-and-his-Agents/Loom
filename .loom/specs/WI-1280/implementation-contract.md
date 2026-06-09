# WI-1280 Implementation Contract

- Suite path: minimal

## Contract Surface

- `tools/loom_check.py` and shared runtime copies expose `--source-surface installed-runtime`.
- `installed-runtime` executes installed route, installed flow, runtime parity, bootstrapped embedded runtime, installed pre-merge chain, and install-layout dependent fixture checks under a stable named source surface and step name.
- `source-self-fixture` remains an aggregate and continues to include `review-run`, `merge-gate`, `closeout-reconciliation`, `retire-workspace`, `installed-runtime`, and the remaining source-self fixture checks.
- Existing `review-run`, `merge-gate`, `closeout-reconciliation`, `retire-workspace`, and aggregate `source-self-fixture` names are not renamed.
- Generated skills runtime `loom_check.py` copies stay aligned with the canonical shared runtime.
- Embedded bootstrapped runtime and repo-local demo compatibility remain intact.

## Consumer Boundary

- Review and merge gates consume this contract through the focused `installed-runtime` source surface, the aggregate `source-self-fixture` surface, generated skills parity, PR metadata, hosted checks, and WI-1280 carriers.
- #1258 does not consume this contract until #1280 is merged and read back.

## Non-Goals

- Do not implement parent #1258 closeout fixture surfaces in WI-1280.
- Do not change release, package, workflow, or user-visible runtime behavior beyond exposing the named diagnostic source surface.
- Do not run scheduler-owned review artifacts, guardian/loom_check gate consumption, controlled merge, post-merge readback, or closeout.

## Validation Binding

- `python3 tools/loom_check.py --profile source --source-surface installed-runtime .`
- `python3 tools/loom_check.py --profile source --source-surface source-self-fixture .`
- `python3 tools/loom.py skills check --target . --json`
