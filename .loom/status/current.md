# Current Status

## Derived Fact Chain View

- Item ID: WI-1204
- Goal: Make Codex plugin layout the default downstream Loom install surface so plugin mode uses `plugins/loom/skills/` and no longer writes or requires downstream top-level `skills/`.
- Scope: WI-1204 owns the downstream plugin layout change across `tools/loom.py`, `tools/check_cli_contract.py`, `tools/check_release_surface.py`, `tools/check_npm_package.py`, `package.json`, `VERSION`, `README.md`, `README.zh-CN.md`, `docs/adoption/codex-install.md`, `docs/adoption/unified-install-experience.md`, `docs/adoption/host-adapter-matrix.md`, `docs/adoption/loom-installed-state-v2.md`, `src/skills/README.md`, `src/skills/README.zh-CN.md`, `src/skills/shared/scripts/loom_check.py`, generated `skills/README.md`, generated `skills/README.zh-CN.md`, generated `skills/*/loom-package.json`, generated `skills/*/.loom-runtime/README.md`, generated `skills/*/.loom-runtime/README.zh-CN.md`, generated `skills/*/.loom-runtime/shared/scripts/loom_check.py`, stable demo bootstrap fixture files under `examples/new-project/.loom/`, repo-local `.loom/bin/loom_init.py`, repo-local `.loom/bin/fact_chain_support.py`, `.loom/bootstrap/manifest.json`, `.loom/shadow/merge-ready-loom.json`, `.loom/shadow/closeout-loom.json`, `.loom/progress/WI-1203.md`, `.loom/status/current.md`, and `.loom` WI-1204 carriers. Ownership includes #1214 release version bump for the root `@mc-and-his-agents/loom` CLI and #1215 bytecode-cache prevention for repo-local and installed runtime surfaces. Ownership excludes #1196 workstation registration semantics, Codex Desktop user-level registration truth, npm installer revival, destructive removal of downstream target-owned `skills/`, and any change outside the #1204-#1211/#1214/#1215 issue tree.
- Execution Path: issue #1204 -> branch work/1204-plugin-layout-default -> PR/CI -> target branch validation -> child-to-parent issue closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1204.md
- Review Entry: .loom/reviews/WI-1204.json
- Validation Entry: make loom-check; python3 tools/check_cli_contract.py; python3 tools/check_release_surface.py; python3 tools/skills_surface.py check; loom host install/verify fixture; loom installed-state validate fixture; loom doctor fixture; loom repair plan fixture; HotCP-style fixture checks; docs surface checks; git diff --check; PR/CI.
- Closing Condition: #1205-#1211, #1214, #1215, and #1204 have closeout evidence, target PR is merged, target branch validates plugin mode without writing or requiring downstream top-level `skills/`, repo-local/downstream runtime checks do not generate `__pycache__` or `.pyc`, and the issue tree is closed from child items to parent.
- Current Checkpoint: build
- Current Stop: PR #1216 is open for `work/1204-plugin-layout-default` at head `4d6f2297`; local validation passed, GitHub authentication is restored, and CI merge-gate/doc-sync failures are being repaired.
- Next Step: Refresh PR body, review records, and docs sync evidence; push the repair commit; validate CI; merge; validate target branch; publish `@mc-and-his-agents/loom@0.13.9` or record the explicit publish block; then close #1205-#1211/#1214/#1215 and #1204 with evidence.
- Blockers: None recorded.
- Latest Validation Summary: Passing local evidence: `python3 tools/skills_surface.py check`; `python3 tools/check_cli_contract.py`; `python3 tools/check_release_surface.py`; `python3 tools/check_npm_package.py`; `npm pack --dry-run --json --ignore-scripts` for `@mc-and-his-agents/loom@0.13.9` with 2277 payload entries; plugin fixture `/tmp/loom-1204-fixture.vYoi9M` install wrote only `plugins/loom/.codex-plugin/plugin.json`, `plugins/loom/skills`, and `.loom/installed-state.json`; fixture root `skills/` absent; fixture `host verify`, `installed-state validate`, `doctor`, `repair plan`, `upgrade-plan`, and `skills check` passed; repo-local `python3 .loom/bin/loom_init.py verify --target .`, `fact-chain`, `shadow-parity`, `adopt verify`, and `closeout check --skip-gate` passed; `make loom-check` passed with 40 source/distribution surfaces; `git diff --check` passed; cache scan for `__pycache__`/`.pyc`/`.pyo` was empty after repo-local and fixture checks; PR #1216 opened at head `4d6f2297`. Current repair evidence: `suite evidence validate` passes after replacing the temp fixture locator with `.loom/progress/WI-1204.md`; docs sync repair restored the required `CLI-managed payloads` phrase.
- Recovery Boundary: Do not change #1196 workstation registration command semantics, do not write Codex Desktop user registration state into target repository truth, do not revive `@mc-and-his-agents/loom-installer` as a primary path, and do not delete or overwrite target-owned non-Loom `skills/`.
- Current Lane: loom-hardening/downstream-plugin-layout-default

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: make loom-check
- Lane Entry: loom-hardening/downstream-plugin-layout-default

## Sources

- Static Truth: .loom/work-items/WI-1204.md
- Dynamic Truth: .loom/progress/WI-1204.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
