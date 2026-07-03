# WI-1901 Implementation Contract

## Required Fixture Shape

The runtime-paths surface must include a fixture that:

- Creates a valid metadata-only Loom target repository.
- Includes stable Work Item, progress, status, review, spec, installed-state, and PR payload carriers.
- Deletes target repo-local `.loom/runtime` and `.loom/tmp` before checks run.
- Runs doctor, resume, review read, PR gate, and merge-ready against the cache-absent target.

## Required Runtime Behavior

- Stable truth carriers remain read from the target repository.
- Runtime diagnostics for agent-safe envelopes resolve through the global runtime cache.
- Passing checks must not recreate target repo-local `.loom/runtime` or `.loom/tmp`.
- A missing repo-local cache must not be classified as a gate blocker.

## Required Contract Checks

- Doctor passes after installed-state is present.
- Resume passes and exposes a readable artifact locator/hash.
- Review read passes from the authored review record.
- PR gate passes from the authored review and PR payload fixture.
- Merge-ready passes from the same fresh carrier set.
- The fixture fails if any checked surface writes repo-local runtime/tmp cache directories.
