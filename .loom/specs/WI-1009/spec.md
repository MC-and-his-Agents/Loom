# WI-1009 Spec

## Intent

Publish the first `loom` CLI release through the #1008 main-push automatic release workflow.

## Scope

- Root `VERSION`
- Generated skill package repo-version surfaces
- CLI contract/version checks that pin the current repo version
- `docs/evidence/v0.13.0-cli-release-readiness.md`
- Loom WI-1009 carriers and status surfaces

## Required Behavior

- Select an unpublished root `VERSION` candidate after the already-published `v0.12.0` release.
- Keep the release candidate on the single active `loom` CLI release line.
- Ensure pull-request checks judge the release but do not create tag/release evidence.
- Ensure the merge to `main` can create a new GitHub `v*` tag and GitHub Release for the selected `VERSION`.
- Preserve installer sunset behavior: no npm publish, no new `loom-installer-v*` tag, and no installer GitHub Release.
- Record enough evidence for #1003 closeout to cite the first CLI release.

## Non-Goals

- Do not add a new npm package, Homebrew formula, or standalone binary.
- Do not restore or advance the deprecated `loom-installer` publish line.
- Do not perform npm deprecation work; #1010 owns npm deprecate or permission-block evidence.
- Do not expand into profile or repo-specific rewrites outside #1003.
