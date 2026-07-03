# WI-1900 Implementation Contract

## Required Runtime Fields

When `agent_safe_payload` emits a short envelope with `full_output.available = true`, the `full_output` object must include:

- `artifact_locator`: logical locator for the complete artifact.
- `artifact_sha256`: SHA-256 of the saved artifact file bytes.
- `truncated`: whether stdout was shortened.
- `sensitive`: whether the artifact may contain sensitive diagnostics.

## Required Artifact Behavior

- Artifact files keep the existing `loom-output-artifact/v1` schema.
- Hash verification is performed against the artifact file bytes.
- The artifact payload remains readable through the logical locator resolver.
- `.loom/tmp/**` locators are resolved through the global runtime cache when applicable.

## Required Contract Checks

- Missing `artifact_locator` blocks validation.
- Missing `artifact_sha256` blocks validation.
- Hash mismatch blocks validation.
- The short envelope does not include the complete long payload body.
- Existing consumers that call `runtime_payload_from_agent_safe_output` continue to receive the full runtime payload after hash verification.
