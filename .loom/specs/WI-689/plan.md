# WI-689 Plan

1. Add `loom-installed-surface-status/v1` and upgrade rehearsal result fields to installer output types.
2. Extend the installer CLI with `upgrade-plan` and `verify-upgrade` operations that read installed metadata and compare payload files without mutating the target.
3. Write installed status metadata during installer-managed plugin and single-skill installs.
4. Document installed Loom status and upgrade rehearsal semantics under adoption docs and installer README files.
5. Add installer tests for current, upgrade-available, drift, and missing metadata fail-closed states.
6. Run installer package validation, CLI smoke, and full `make check` on a clean tracked baseline.
