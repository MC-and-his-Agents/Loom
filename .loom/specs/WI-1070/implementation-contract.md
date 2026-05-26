# WI-1070 Implementation Contract

- Version input is limited to root `VERSION` and `package.json`.
- Publishing is performed by the merged `loom-cli-release` workflow, not by a local manual npm publish.
- The first npm publish must match the GitHub v* tag, GitHub Release, `VERSION`, and `package.json`.
- If npm auth or provenance fails, record the workflow run and permission evidence before asking for owner-side action.
