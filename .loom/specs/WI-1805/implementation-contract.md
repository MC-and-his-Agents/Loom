# WI-1805 Implementation Contract

## Ownership

- Owns host governance capability diagnosis in `governance_surface.py` runtime copies, including capability status classification and setup guidance.
- Owns governance capability profile contracts for `host-enforced` and `advisory/local-enforced` in docs, fixtures, and tests.
- Owns merge check/run consumption of governance profiles in `loom_flow.py` runtime copies and `tools/loom.py`.
- Owns governance mode evidence fields in PR metadata, closeout policy, docs/readback surfaces, and v0.23.0 release readiness evidence.
- Owns v0.23.0 version, npm package metadata, plugin metadata, and plugin payload hash preparation for release.
- Owns WI-1805 Loom carriers needed for fact-chain, review, PR gate, release readiness, and closeout.

## Boundaries

- Do not add a large policy DSL or a truth carrier parallel to existing suite, PR metadata, review, closeout, and release evidence.
- Do not make advisory/local-enforced a normal strong-governance path; it is explicit low-assurance fallback only.
- Do not let advisory fallback bypass semantic review, PR gate, current-head binding, CI rollup, head drift checks, release readback, or closeout evidence.
- Do not permit high-risk release/security/payment/data-migration fallback without explicit approval and evidence.
- Do not write HotCP-specific behavior into Loom core.
- Do not close issues, merge, publish, or terminalize release evidence until PR #1831 and hosted/readback gates prove the current head.

## Release Metadata Rule

- v0.23.0 metadata may be prepared in this PR.
- Publishing GitHub Release/npm and writing terminal release closeout evidence must happen only after #1831 merges to `main` and release readback confirms tag, package, plugin metadata/hash, workflow, and carrier state.
