# WI-966 Plan

1. Add a Node-only regression runner under `packages/loom-installer/scripts/` that acquires a package-root `.installer-regression-lock`, creates a unique npm cache, and runs `npm ci`, `npm test`, and `npm pack --dry-run`.
2. Route Node installer PR/release workflows through the runner instead of separate unlocked npm install/test/pack steps.
3. Add matching `loom_check` locking around root self-plugin installer build/install paths and call the regression runner from `check_node_installer`.
4. Extend the runtime purity contract and generated skill runtime references with the installer regression lock requirement.
5. Validate lock-busy diagnostics, installer regression, payload drift, skills surface, py-compile, and full source `loom_check`.
