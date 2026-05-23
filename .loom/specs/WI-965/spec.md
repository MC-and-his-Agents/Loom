# WI-965 Spec

## Acceptance

- Default `make loom-check` must not rewrite `examples/new-project` or leave it dirty.
- Demo bootstrap drift must still be detected by rebuilding the fixture in an isolated temporary target and comparing it with the stable fixture.
- Intentional stable fixture refresh must use an explicit sync entrypoint.
- GitHub `demo-bootstrap` and `repo-local-cli` jobs must consume the isolated check path before using the stable demo fixture.

## Non-Goals

- Do not remove `examples/new-project`.
- Do not reduce repo-local demo CLI coverage.
- Do not implement #966 Node installer write isolation or #968 regression matrix.
