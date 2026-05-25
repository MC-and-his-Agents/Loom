# WI-1001 Plan

1. Add a Loom CLI release surface document that selects the minimal root GitHub Release channel.
2. Update version authority and README surfaces to separate `loom` CLI release evidence from installer npm evidence.
3. Add `loom-cli-release` workflow for release judgment and explicit publish runs.
4. Narrow installer release and version-bump behavior to installer shim/package changes.
5. Add a release surface checker and wire it into local/PR validation.
6. Validate with release surface, version surface, CLI contract, installer checks, workflow parsing, and `make check`.
7. Open PR, consume required checks and release/no-publish judgment, then close #1001 with evidence.
