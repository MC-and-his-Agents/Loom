# WI-875 Spec

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md, consistency-analysis.md, execution-breakdown.md; rationale: #875 is a focused regression fixture hardening slice for the already-defined #876/#877/#874 PR metadata carrier/parser contract; consumer boundary: #957 may consume the resulting preflight evidence later, but readiness/cost guard behavior is out of scope; recheck condition: switch to full suite if this Work Item starts changing frozen core contracts, review/merge-ready/closeout semantics, host merge execution, or #1107 suite CLI structure.
- Consumes: issue #875, #876 machine carrier contract, #877 parser preflight, #874 body-file/readback validation.
- Produces: parser and fixture evidence consumable by review, merge-ready, and closeout.

## Goal

Prove that PR metadata preflight has regression coverage for Markdown drift, broken machine carrier envelopes, hash/readback drift, and legacy Markdown-only migration modes without letting parser or CLI output replace authored Loom truth.

## Scope

- In scope:
  - Positive fixture for intact machine block / artifact schema.
  - Markdown drift fixture for human-only Markdown changes around an unchanged machine block.
  - Negative fixtures for malformed JSON, missing schema, missing required fields, readback hash mismatch, and unsupported parser version.
  - Legacy fixtures for advisory and dual-read migration modes that do not bulk-fail old Markdown-only PR bodies.
  - Diagnostics evidence for locator/hash, expected format, missing fields, parser version, and repair fallback.
- Out of scope:
  - #957 pre-review readiness/cost guard.
  - #1107 full spec suite CLI tree.
  - Rewriting frozen Work Item, review, merge-ready, closeout, or docs/source truth contracts.
  - Making free Markdown a substitute for declared machine carrier truth.

## Scenarios

### S1: Machine Carrier Stays Stable Through Human Markdown Drift

Given a PR body with a valid repo metadata HTML comment JSON block
When human sections change headings, list indentation, backticks, command-substitution-looking text, or Chinese punctuation
Then metadata preflight still passes because the declared machine block is unchanged.

### S2: Broken Machine Carrier Fails Closed With Locators

Given a PR body where the declared metadata block is malformed, incomplete, or uses an unsupported parser version
When metadata preflight runs
Then it blocks with diagnostics that identify the block locator, raw excerpt hash, expected format, missing fields, parser version issue, and repair fallback.

### S3: Legacy Markdown-Only PRs Enter Migration Mode

Given an old PR body that has no machine block
When the repo companion declares advisory or dual_read migration mode
Then metadata preflight remains advisory/pass with legacy_mode evidence, while required mode still blocks.

## Acceptance

- A1: `loom_check` covers machine carrier pass, Markdown drift pass, and machine block hash mismatch block.
- A2: `loom_check` covers missing schema, missing required field, malformed JSON, and unsupported parser version diagnostics.
- A3: `loom_check` covers advisory and dual_read legacy migration without bulk-failing old Markdown-only PR bodies.
- A4: Parser diagnostics include locator/hash, expected format, missing fields or parser-version reason, and repair fallback.
- A5: Parser and CLI evidence remains preflight evidence only and does not replace Work Item, review, merge-ready, closeout, or docs/source truth.
