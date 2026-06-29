# WI-1790 Spec

## Suite Path Decision

- Suite path: minimal
- Rationale: WI-1790 is a bounded installed CLI/package repair. The failure is localized to wrapper runtime script resolution and package payload coverage; a full suite would duplicate the observed reproduction, package smoke, and release validation without adding a new product contract.
- Consumer Boundary: review, PR metadata, hosted checks, PR gate, controlled merge, release workflow, npm readback, Codex plugin payload refresh, and installed CLI smoke.
- Recheck Condition: Re-run package smoke, package payload checks, release surface checks, demo fixture drift, PR metadata preflight, and installed CLI smoke after any change to wrapper entrypoints, packaged skills paths, `VERSION`, `package.json`, plugin payload metadata, generated runtime copies, or demo bootstrap fixtures.
- Scope Proof: `git diff origin/main...HEAD` stays limited to wrapper runtime path resolution, generated runtime parity, package smoke/checks, v0.21.1 release metadata, demo bootstrap fixture sync, and WI-1790 carriers.
- Review Requirement: current_head_review_required
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: the public contract remains the existing `loom init bootstrap --target ... --json` CLI behavior and the patch only reconnects the wrapper to packaged runtime locations. consumer boundary: suite validate, review, PR gate, hosted CI, release judgment, controlled merge, publish, and closeout may consume this minimal suite while still requiring fact-chain, current-head review, PR metadata, release judgment, hosted checks, and post-release readback. recheck condition: require full suite artifacts if the work expands into a new init/bootstrap architecture, host adapter behavior, credentials, permissions, or multi-release migration.

## Scenarios

- S1: Installed npm package wrappers resolve init/bootstrap runtime scripts from packaged `src/skills` or `plugins/loom/skills` when top-level `skills/` is absent.
- S2: Repo-local development wrappers continue to use top-level `skills/` and retain repo-local runtime classification.
- S3: Successful bootstrap JSON includes an agent-safe pass result and summary.
- S4: npm package payload validation and tarball smoke cover `loom init bootstrap --target <fixture> --json`.
- S5: v0.21.1 release metadata and plugin payload hash identify the fixed package candidate before publish.

## Acceptance

- [x] A1: The installed-package `FileNotFoundError` is reproduced and fixed at the shared wrapper entrypoint.
- [x] A2: Source, generated, and plugin runtime copies stay in sync for the bootstrap output change.
- [x] A3: Packed npm tarball smoke proves bootstrap no longer fails due to a missing runtime script.
- [x] A4: Package, release surface, plugin payload metadata, and demo fixture checks pass locally.
- [ ] A5: Hosted checks, PR gate, controlled merge, npm publish, plugin payload refresh, and installed CLI readback pass.
