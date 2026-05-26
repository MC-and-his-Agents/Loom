# WI-1069 Implementation Contract

- Do not change `VERSION` or `package.json` version.
- Do not publish npm from local development or PR checks.
- Do not modify `node-installer-release` into an active publisher.
- Keep workflow publish mutation behind `publish_allowed`.
- Use `@mc-and-his-agents/loom` and the root `loom` bin as the only active npm CLI release line.
- Preserve #1068 checker guardrails for CLI-only install and package payload surfaces.
