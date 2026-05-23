# WI-859 Implementation Contract

## Must Preserve

- Loom source repositories continue to run the source/distribution self-check by default.
- Consumer repositories do not receive source asset failures from default `loom_check.py [repo-root]`.
- Existing generated skill surface contracts remain synchronized from `src/skills`.
- Consumer `make loom-check` semantics remain based on consumer validation chain behavior, not raw source self-check.

## Must Block

- Ambiguous or partial profiles must fail with actionable scope guidance instead of emitting broad source asset failures.
- Consumer runtime artifact hash drift must fail the consumer profile.
- Strong consumer maturity must still run blocking shadow parity.
- PR merge must not proceed without fresh authored review evidence bound to the PR head or an accepted carrier-only delta.

## Evidence

Validation evidence is recorded in `.loom/reviews/WI-859.json`, `.loom/reviews/WI-859.spec.json`, PR #960, and the final closeout state for #859/#860/#861.
