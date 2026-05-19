# WI-781 Plan

1. Define the `.loom` surfaces version-control policy in adoption docs and generated references.
2. Change bootstrap gitignore handling to add only runtime/tmp/cache scratch ignores.
3. Detect blanket `.loom` ignore patterns and block write by default.
4. Add `--repair-gitignore` to narrow blanket ignores to scratch-only ignores.
5. Make `verify` report blanket `.loom` ignore drift.
6. Add regression coverage for block, repair, stable Git visibility, runtime ignore visibility, and standalone verify drift.
7. Regenerate generated skills surfaces and refresh `examples/new-project`.
8. Validate with targeted fixtures, skills surface check, `loom_check`, `make skills-check`, and `make loom-check`.
