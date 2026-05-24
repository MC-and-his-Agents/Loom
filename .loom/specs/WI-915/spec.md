# WI-915 Spec

## Acceptance Contract

- `loom init`, `loom adopt verify`, and `loom route` are implemented CLI-first entries over the existing initialization and adoption runtime.
- `loom profile status|upgrade-plan|upgrade` are implemented CLI-first entries over the existing governance profile runtime.
- `loom status` and `loom fact-chain` emit structured JSON and fail closed when carriers are unreadable or missing.
- `loom checkpoint admission|build|merge` consume the existing checkpoint payloads without creating another fact source.
- `loom gate pre-review|spec-review|review|pr|merge|closeout` expose stable gate names and delegate to the existing flow, PR gate, controlled merge check, and closeout check.
- Missing target carriers, missing PR/head input, and missing closeout target input return structured `block` payloads with executable fallback names.
