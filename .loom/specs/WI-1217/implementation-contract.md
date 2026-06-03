# WI-1217 Implementation Contract

## Ownership

WI-1217 owns metadata-only adoption mode, installed-state representation, CLI mode split, diagnostic checks, docs, fixtures, plugin manifest metadata, and root governance carriers for PR #1227.

## Non-Goals

- Do not make metadata-only write or require `plugins/loom/skills`, `.agents/skills`, or root `skills`.
- Do not encode Codex Desktop workstation registration as repository truth.
- Do not remove or rewrite downstream repo-owned governance evidence.
- Do not remove embedded payload mode.
- Do not publish a release without release readiness and credentials.

## Validation

- Metadata-only fixture install/validate/host verify/skills check/detect.
- Metadata-only unexpected embedded payload pollution fixture.
- Embedded payload fixture host install/verify.
- `git diff --check`.
- `python3 tools/check_release_surface.py`.
- `python3 tools/skills_surface.py check`.
- `python3 tools/check_cli_contract.py`.
- `make loom-check`.
- PR/CI and target branch validation.
