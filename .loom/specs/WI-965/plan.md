# WI-965 Plan

1. Add a repo-local helper that copies `examples/new-project` to an isolated temporary target, reruns bootstrap there, and compares the result with the stable fixture.
2. Change default Makefile and CI demo bootstrap paths to use the isolated check helper.
3. Preserve an explicit `make loom-demo-new-project-sync` target for intentional stable fixture rewrites.
4. Update harness documentation and generated skill runtime references.
5. Validate py-compile, skills surface, isolated demo check, default `make loom-check`, and clean fixture status.
