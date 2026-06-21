# WI-1675 Spec

## Suite Path

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts `suite-index.md`, `research.md`, `contracts.md`, and `readiness-checklist.md`; rationale: WI-1675 is a bounded README documentation Work Item that improves product positioning, architecture explanation, workflow explanation, badges, quick start install wording, release-surface README needle alignment, and doc-sync README needle alignment without changing runtime behavior, package release surfaces, install implementation, or legacy migration contracts. consumer boundary: suite validate, review, PR gate, hosted CI, merge-ready, controlled merge, and issue closeout may consume this minimal spec, plan, evidence map, task carrier, WI carriers, README/checker diff, local README readback, release-doc-contract validation, doc-sync validation, and PR evidence. recheck condition: require a full suite if the PR expands into runtime behavior, installer implementation, release packaging, migration contracts, host mutation, permissions, external-visible execution, or downstream repository adoption changes.

## Objective

Make the English and Chinese README versions useful as first-contact documentation for users evaluating and installing Loom.

## Acceptance Scenarios

### S1: user understands Loom's value and operating model

Given a new user opens either README version, the opening sections explain Loom's product value, problem statement, architecture, workflow model, and non-goals before maintainer-oriented links.

### S2: user can install through the supported path

Given a user wants to install Loom, the quick start gives a short prompt for a coding agent and the supported global CLI / Codex user-level plugin commands without legacy compatibility noise.

### S3: Chinese README avoids unnecessary English prose

Given a Chinese reader opens `README.zh-CN.md`, the user-facing prose is primarily Chinese while preserving necessary product names, commands, paths, badges, and platform names.

## Non-Goals

- No runtime behavior changes.
- No package, release, or installer implementation changes.
- No legacy migration contract changes.
- No downstream repository adoption changes.
