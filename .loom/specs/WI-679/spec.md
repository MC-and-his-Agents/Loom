# WI-679 Spec

## Goal

Add an MVP review context pack so formal review consumes recent findings, dispositions, reviewed heads, validation summaries, and repeated blocker candidates before producing another verdict.

## Acceptance Criteria

- The context pack schema is `loom-review-context-pack/v1`.
- The repeated blocker signal schema is `loom-repeated-blocker-signal/v1`.
- `review run` writes context pack evidence before invoking the review engine.
- The default review prompt includes recent finding summaries, disposition state, and repeated/root-cause classification guidance.
- Engine metadata and review output expose the context pack locator.
- Repeated block finding patterns are summarized with source locators and recommended root-cause handling.
- Repeated blocker enforcement remains advisory in v0.8.0 and does not become a hard merge gate.
- Fixtures prove repeated finding history produces a repeated blocker/root-cause candidate.
- `make check` passes with no tracked verification drift.

## Non-Goals

- Do not create a second review truth source.
- Do not make repeated blocker fallback blocking until v0.9 hardening.
- Do not expand deterministic engine profile behavior; that belongs to #675.
