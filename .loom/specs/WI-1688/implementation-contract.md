# WI-1688 Implementation Contract

## Runtime Contract

- Non-passing root CLI wrapper payloads with actionable evidence emit `actionable_findings` in the agent-safe envelope.
- Passing payloads under the stdout budget keep the original runtime payload.
- `--full-output` returns the original runtime payload without the compact envelope.
- When stdout is compacted, the original payload is written to a full-output artifact locator.

## Extraction Contract

- Actionable findings may be derived from `findings`, repair plans, sync plans, `next_action`, `next_command`, and non-empty `fallback_to` fields.
- Extracted action text is truncated for agent-safe stdout and must not invent commands.
- Over-budget payloads keep a smaller actionable finding subset while preserving the full artifact.

## Boundary Contract

- This Work Item does not change delegated gate decisions, host mutation semantics, closeout policy, release behavior, or `loom ship`.
- Contract consumers that require raw runtime payloads must unwrap the artifact-backed agent-safe output before asserting runtime fields.
