# WI-1684 Implementation Contract

## Runtime Contract

- `workflow`, `metadata_schema`, `host_write`, and `permissions` are recognized `change_class` values.
- Each new class is high-risk and requires standard or reinforced governance when attempted under `light`.
- The light allowlist remains limited to `docs_only`, `docs_governance`, and bounded `fixture`.

## Fixture Contract

- Metadata preflight has negative fixtures for each new high-risk class declared as `light`.
- PR gate abuse cases have named negative fixtures for workflow, PR metadata schema, host write, and permissions changes declared as `light`.
- Existing positive light fixtures continue to pass.
