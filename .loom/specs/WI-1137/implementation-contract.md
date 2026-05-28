# WI-1137 Implementation Contract

## Authority Boundary

- `loom doctor` is diagnostic evidence only.
- Doctor must not run `suite validate`, `suite evidence validate`, or `suite carrier validate`.
- Doctor output must not replace Work Item truth, review records, merge-ready results, closeout evidence, or docs/source truth.

## Required Behavior

- Read top-level and layer-level installed-state support declarations.
- Treat absent suite command support as a passing not-required diagnostic state.
- Treat `declared_support.suite_commands` as the explicit command list to compare with `loom help --json`.
- When only a suite support marker is present, compare the current implemented suite command family.
- Fail closed when a declared command is missing from the help matrix or is not `domain: suite`, `status: implemented`, and `json: true`.

## Non-goals

- No verify profile enforcement.
- No full suite validation from doctor.
- No host writes, Project writes, issue writes, review writes, merge-ready writes, or closeout writes.
- No `/speckit.*` command names or `.specify/` layout.
