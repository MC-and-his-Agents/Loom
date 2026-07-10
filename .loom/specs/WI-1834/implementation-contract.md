# WI-1834 Implementation Contract

## Ownership

- Owns `runtime-upgrade status|prepare|check|closeout` command behavior in `tools/loom.py`.
- Owns runtime-upgrade CLI contract coverage in `tools/check_cli_contract.py`.
- Owns shared runtime metadata vocabulary and `runtime-upgrade-only` PR intent profile across `loom_flow.py` runtime copies.
- Owns `loom -v` / `loom --version`, `help --json`, CLI matrix, README, and README.zh-CN updates.
- Owns Codex plugin/cache diagnosis guidance as advisory upgrade experience output.
- Owns plugin payload metadata/hash and examples/new-project fixture synchronization required by this implementation PR.
- Owns WI-1834 carriers required for fact-chain, review, PR gate, merge-ready, and release handoff.

## Boundaries

- Do not add multi-repo batch mode in this milestone.
- Do not lower review, PR metadata, head binding, CI rollup, release readback, or closeout requirements.
- Do not run `loom host install` or `loom host register` from repo `runtime-upgrade prepare/check`.
- Do not write user-level Codex plugin/cache state from repo PR commands.
- Do not represent plugin/cache advisory status as a repository merge fact.
- Do not reuse `INIT-0001` or a product Work Item for runtime-upgrade maintenance.
- Do not publish v0.24.0 until PR #1839 merges to `main`.

## Release Metadata Rule

- v0.24.0 release metadata is prepared by this milestone but must be finalized only in #1838 after PR #1839 merges.
- Publishing GitHub Release/npm and writing terminal release closeout evidence must consume main-branch version/package/plugin metadata, tag, npm package readback, hosted workflow evidence, and carrier state.
