# WI-1070 Spec

## Acceptance

- Root `VERSION` and `package.json` identify a new unpublished Loom CLI version.
- PR checks prove the npm package payload, CLI contract, release surface, and version surfaces.
- Merging the PR allows `loom-cli-release` to create the matching v* tag, GitHub Release, and npm package publication.
- Post-merge evidence proves npm install smoke succeeds for `@mc-and-his-agents/loom`.
- Installer release and npm state remain sunset/non-advancing.
- #1063 closeout consumes child issues, PRs, merge commits, checks, workflow run, npm package, tag, release, and installer non-advancement evidence.

## Non-Goals

- Do not add another package name or distribution surface.
- Do not reactivate `loom-installer`.
- Do not add Homebrew, standalone binary, or profile-level rewrites.
