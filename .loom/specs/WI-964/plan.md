# WI-964 Plan

1. Add a per-root `.loom/runtime/loom_check.lock` around `loom_check` source and consumer execution.
2. Use atomic lock creation with fail-fast behavior and structured owner payload.
3. Recover stale locks when the recorded owner process is gone.
4. Add a local self-check for lock owner fields, busy output, and stale lock replacement.
5. Sync generated skills surfaces and validate with targeted checks plus source `loom_check`.
