# WI-780 Plan

1. Remove default release target files and `release_targets` declarations from adoption scaffolds.
2. Mark `.loom/companion/releases/**` intentionally absent for default adoption profiles.
3. Update governance surface handling so absent release targets remain absent, not present via the repo-interface locator.
4. Refresh generated skills and `examples/new-project` from source truth.
5. Update adoption docs and source references to state the default absence contract.
6. Validate with py_compile, targeted adoption fixtures, skills surface check, `make skills-check`, and `make loom-check`.
