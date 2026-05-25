# WI-889 Plan

1. Bind PR #997 to `WI-889` so the fact chain matches the #889/#892/#896 batch.
2. Keep delivery commands in `tools/loom.py` as the user-facing CLI contract and delegate verification to existing doctor/runtime surfaces.
3. Keep scenario commands in `tools/loom.py` as wrappers around existing flow/checkpoint/locator behavior.
4. Keep installer compatibility in the existing Node installer package and host adapter path; do not make it the owner of top-level semantics.
5. Extend `tools/check_cli_contract.py` with command and fail-closed assertions for #910-#914, #924-#928, and #944-#947.
6. Validate with CLI contract checks, version surface checks, installer package checks, full repository checks, adoption verification, shadow parity, and PR gate evidence.
7. Merge PR #997 only after fresh or carrier-only review evidence, PR checks, and issue/PR/head bindings are all consistent.
