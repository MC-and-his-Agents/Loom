# WI-1065 Plan

1. Read #1065, the #1064 CLI-only install contract, and current CLI/package surfaces.
2. Add the root npm package manifest and `loom` bin shim.
3. Add a package payload checker that validates manifest authority, required files, forbidden files, and `npm pack --dry-run` output.
4. Add Loom work item, progress, spec, plan, implementation contract, and review carriers.
5. Run package checks, local npm install smoke, existing release/version/CLI checks, and PR gates.
6. Merge and close #1065 with evidence for #1066.
