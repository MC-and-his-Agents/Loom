# WI-967 Plan

1. Add a shared subprocess environment sanitizer for `loom_check` command helpers.
2. Preserve explicit fixture opt-in by applying `env=` after default sanitization.
3. Replace fixed missing live target samples with unique absent temp paths.
4. Add source self-check coverage for env sanitization and unique absent paths.
5. Sync generated skills and demo bootstrap runtime surfaces, then validate with targeted checks and source `loom_check`.
