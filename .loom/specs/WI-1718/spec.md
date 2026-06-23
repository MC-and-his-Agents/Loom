# WI-1718 Spec

## Suite Path Decision

- Suite path: minimal
- Rationale: WI-1718 is a bounded release closeout Work Item for the already implemented plugin payload freshness issue tree. It changes release authority, package metadata, release workflow stamping, release validation evidence, and Work Item carriers without adding new product behavior beyond publishing the completed capability.
- Consumer Boundary: review, PR gate, release judgment, controlled merge, main-push release workflow, release readback, FR closeout, and milestone closeout.
- Recheck Condition: Re-run release/package validation after any change to `VERSION`, `package.json`, plugin payload metadata/hash, release workflow, package payload, release evidence, or WI-1718 carriers.
- Scope Proof: Changes are limited to v0.19.0 release authority, plugin payload release metadata/hash, publish-time stamping for release metadata, release readiness evidence, release workflow contract guard, and WI-1718 carriers.
- Review Requirement: current_head_review_required
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1718 is a release closeout slice with a frozen FR scope and is fully reviewable through spec, plan, implementation contract, evidence map, release readiness evidence, package validation, and release readback. consumer boundary: suite validate, spec review, implementation review, PR metadata, hosted checks, PR gate, controlled merge, release workflow, release readback, issue closeout, FR closeout, and milestone closeout may consume this minimal suite without treating skipped full-path artifacts as completed. recheck condition: require full suite artifacts if this work expands into new product behavior, npm publish mechanics beyond metadata stamping, host plugin install mutation semantics, credentials handling, or a multi-release migration.

## Scenarios

- S1: The release PR advances root Loom CLI authority from `v0.18.0` to `v0.19.0`.
- S2: The Codex plugin payload metadata reports `source_package_version=0.19.0`, `plugin_payload_version=0.19.0`, and a deterministic payload hash while plugin surface version remains `0.4.0`.
- S3: The publish workflow stamps `source_git_sha` to the release commit and recomputes `plugin_payload_hash` before npm publish.
- S4: Release readiness evidence consumes the completed #1711 tree, including #1732 tombstone installer work, while leaving legacy npm deprecation as a separate confirmation action.
- S5: After merge, the main-push release workflow publishes tag, GitHub Release, npm package, and plugin payload metadata/hash readback before #1718 and #1711 close.

## Acceptance

- [x] A1: `VERSION` is `v0.19.0` and `package.json` is `0.19.0`.
- [x] A2: Plugin payload metadata and hash are aligned for the v0.19.0 candidate.
- [x] A3: Publish-time stamping writes the final release commit SHA and recomputes payload hash before `npm publish`.
- [x] A4: `docs/evidence/v0.19.0-release-readiness.md` records scope, issue tree readback, validation, publish boundary, npm deprecate boundary, and post-merge closeout contract.
- [ ] A5: Release/package validation, suite validation, PR gate, hosted checks, and controlled merge pass at PR head.
- [ ] A6: Post-merge release readback passes before #1718 and #1711 close.
