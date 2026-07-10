# WI-1800 Implementation Contract

## Ownership

- Owns #1793 target/context fallback fixes and checkpoint alias compatibility.
- Owns #1794/#1795 global-cli metadata-only bootstrap and CI verification split.
- Owns #1797/#1798 active-ruleset strong detector and adversarial adoption evidence.
- Owns #1799 audited repair-pr evidence recording and validation.
- Owns #1801 runtime parity, v0.21.2 release readiness, package metadata, and plugin payload hash.
- Owns #1803/#1804 PR/merge target/readback behavior and metadata-only companion init-result consumption.
- Owns opaque path-safe Work Item ID compatibility in PR metadata and merge fixtures.

## Boundaries

- Do not close #1800 or #1802 before post-merge release evidence exists.
- Do not include #1806 or #1807-#1810 in this release.
- Do not turn repair-pr mode into a gate bypass or automatic GitHub ruleset mutation path.
- Do not rely on repo-local `.loom/bin` for metadata-only/global-cli bootstrap success.
- Do not require `WI-`, `INIT-`, issue, or `GH-` prefixes for repo-native Work Item IDs unless a stricter companion schema explicitly declares that requirement.

## Release Metadata Rule

- `VERSION`, root `package.json`, and `plugins/loom/.codex-plugin/plugin.json` must identify v0.21.2 before merge.
- `docs/evidence/v0.21.2-release-readiness.md` is pre-merge readiness evidence only; post-merge release evidence belongs to #1802.
- After merge, `loom-cli-release` on `main` must publish/read back `v0.21.2` before #1802 and #1800 closeout.
