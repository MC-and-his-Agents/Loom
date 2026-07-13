# Repo Companion

This repository uses Loom's host-derived lifecycle. GitHub owns issue, PR,
head, check, merge, and historical delivery facts; the current worktree owns
only session-local execution state.

The retained repository-specific inputs are:

- `.loom/companion/repo-interface.json` for PR metadata and issue taxonomy;
- `.loom/review-profiles.json` for the repository-owned review policy.

There are no repository execution carriers, shadow parity files, or declared
external result sources. Runtime output stays in ignored workstation state or
GitHub Actions artifacts.
