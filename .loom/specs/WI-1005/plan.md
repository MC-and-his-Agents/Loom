# WI-1005 Plan

1. Replace installer release-state resolution with a sunset/no-publish judgment.
2. Remove write permissions, npm token exposure, package publication, installer tag creation, and installer GitHub Release creation from `node-installer-release`.
3. Extend `check_release_surface.py` to require the sunset judgment and reject active installer publish capability.
4. Validate release surface, version surface, CLI contract, installer checks, YAML parsing, `make check`, and Loom carrier checks.
5. Open the issue-scoped PR for #1005 and consume PR/merge evidence before closing the issue.
