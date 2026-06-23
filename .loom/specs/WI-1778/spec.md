# WI-1778 Spec

## Suite Path Decision

- Suite path: minimal
- Rationale: WI-1778 is a bounded release closeout Work Item for the already implemented closeout readback issue tree. It changes release authority, package metadata, plugin payload metadata/hash, release readiness evidence, and Work Item carriers without adding new product behavior beyond publishing the completed capability.
- Consumer Boundary: review, PR gate, release judgment, controlled merge, main-push release workflow, release readback, FR closeout, and milestone closeout.
- Recheck Condition: Re-run release/package validation after any change to `VERSION`, `package.json`, plugin payload metadata/hash, release workflow, package payload, release evidence, closeout/readback regression, or WI-1778 carriers.
- Scope Proof: Changes are limited to v0.21.0 release authority, plugin payload release metadata/hash, release readiness evidence, and WI-1778 carriers.
- Review Requirement: current_head_review_required
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1778 is a release closeout slice with a frozen FR scope and is fully reviewable through spec, plan, implementation contract, evidence map, release readiness evidence, package validation, and release readback. consumer boundary: suite validate, spec review, implementation review, PR metadata, hosted checks, PR gate, controlled merge, release workflow, release readback, issue closeout, FR closeout, and milestone closeout may consume this minimal suite without treating skipped full-path artifacts as completed. recheck condition: require full suite artifacts if this work expands into new product behavior, release workflow mutation, credentials handling, or a multi-release migration.

## Scenarios

- S1: The release PR advances root Loom CLI authority from `v0.20.0` to `v0.21.0`.
- S2: The Codex plugin payload metadata reports `source_package_version=0.21.0`, `plugin_payload_version=0.21.0`, and a deterministic payload hash while plugin surface version remains `0.4.0`.
- S3: Release readiness evidence consumes the completed #1774 tree and names the closeout readback behavior being published.
- S4: Release/package validation proves the package payload, release surface, and closeout/readback regressions remain valid for the release candidate.
- S5: After merge, the main-push release workflow publishes tag, GitHub Release, npm package, and release readback before #1778, #1774, and milestone #18 close.

## Acceptance

- [x] A1: `VERSION` is `v0.21.0` and `package.json` is `0.21.0`.
- [x] A2: Plugin payload metadata and hash are aligned for the v0.21.0 candidate.
- [x] A3: `docs/evidence/v0.21.0-release-readiness.md` records scope, issue tree readback, validation, publish boundary, and post-merge closeout contract.
- [ ] A4: Release/package validation, closeout/readback regression, suite validation, PR gate, hosted checks, and controlled merge pass at PR head.
- [ ] A5: Post-merge release readback passes before #1778, #1774, and milestone #18 close.
