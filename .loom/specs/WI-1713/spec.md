# WI-1713 Spec

## Suite Contract

- Suite path: minimal
- Suite index locator, or N/A rationale: `.loom/specs/WI-1713`
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1713 is a bounded release metadata and checker contract change over an already-scoped plugin payload freshness FR. consumer boundary: suite validate, build checkpoint, review, PR gate, merge-ready, and closeout may consume this minimal spec, plan, implementation contract, task carrier, evidence map, Work Item carriers, and targeted validation output. recheck condition: require full suite artifacts if scope expands into source/cache runtime freshness comparison, plugin refresh commands, legacy installer retirement, release publishing, or new host install state mutation.
- Consumes:
  - Work Item / FR locator: GitHub issue #1713 under FR #1711.
  - Story Readiness confirmed locator, blocking locator, or N/A rationale: N/A; issue #1713 is already scoped as a bounded Work Item.
  - Story scenario locator, or N/A rationale: N/A; scenarios are authored below.
  - Story Business Confirmation confirmed locator, blocking locator, or N/A rationale: N/A; this is release metadata infrastructure, not business-domain behavior.
- Produces:
  - Scenario ids / locators: S1-S3.
  - Acceptance ids / locators: A1-A4.
  - Behavior evidence expectation: plugin manifest exposes package/payload/hash metadata and package checks validate it.
- Locator:
  - Spec locator: `.loom/specs/WI-1713/spec.md`
- Provenance:
  - Source issue / PR / doc / conversation locator: GitHub issue #1713 and user execution request.
  - Freshness rule: Recheck after changes to plugin manifest, plugin payload files, package version, hash checker, version surface checker, or WI-1713 carriers.

## Goal

- Make the Codex plugin payload expose machine-readable release binding metadata.
- Make plugin payload freshness depend on `plugin_payload_version` and `plugin_payload_hash`, not only the `0.4.0` plugin surface version.

## Scope

- In scope:
  - `plugins/loom/.codex-plugin/plugin.json` `x-loom` release metadata.
  - Deterministic plugin payload hash validation with `plugin_payload_hash` self-reference normalization.
  - Version and npm package surface checks that require the metadata.
  - `loom` version context reading payload metadata from the plugin manifest.
- Out of scope:
  - Codex source/cache/runtime readback comparison (#1721).
  - CLI freshness report and short action output (#1715/#1716).
  - Legacy single-skill installer retirement (#1722).
  - Version bump, npm publish, GitHub release, or release tag creation (#1718).

## Key Scenarios

### Scenario S1

Given the repo plugin payload manifest is read

When `x-loom` metadata is inspected

Then it exposes `source_package`, `source_package_version`, `source_git_sha`, `plugin_payload_version`, and `plugin_payload_hash`.

### Scenario S2

Given `plugin_payload_hash` is stored inside the plugin manifest

When the plugin payload digest is computed

Then only the `plugin_payload_hash` value is normalized, while other payload files and metadata still affect the digest.

### Scenario S3

Given `loom` reports version context

When plugin payload version data is emitted

Then it comes from plugin release metadata instead of `skills/registry.json` `registry_version`.

## Acceptance Criteria

- [x] A1: Plugin manifest exposes source package, package version, source git binding state, plugin payload version, and plugin payload hash.
- [x] A2: Hash tests prove payload file changes alter the digest, traversal order does not, ignored cache artifacts do not, and `plugin_payload_hash` self-reference does not.
- [x] A3: `tools/check_npm_package.py` and `tools/version_surface_check.py` fail closed when required release metadata is missing or stale.
- [x] A4: `tools/loom.py` version context reads plugin payload metadata from `x-loom`, preserving registry version as a separate integrity surface.
