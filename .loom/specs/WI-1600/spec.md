# WI-1600 Spec

## Suite Path

- Suite path: minimal
- Full-suite-artifacts not_applicable: rationale: WI-1600 is a focused dependency parser/provenance hardening slice with deterministic parser fixtures, CLI contract coverage, generated runtime parity, and demo fixture validation; consumer boundary: suite validate, spec review, implementation review, PR gate, hosted checks, #1598 convergence, and milestone closeout may consume this minimal suite only for dependency source semantics; recheck condition: require broader suite artifacts if scope expands into closeout PR role behavior, release resume/publishing, PR metadata dry-run semantics, host auth, controlled merge behavior, or external tracker mutation.

## Objective

Ensure active issue dependencies come only from GitHub native relationships or structured Loom machine blocks, not prose.

## Acceptance Scenarios

### S1: Prose does not create active dependencies

Given issue prose mentions blocked-by-like text, Loom does not promote that prose into active dependency truth.

### S2: Native and structured dependencies remain consumable

Given GitHub native dependency relationships or a structured Loom machine block is present, Loom records dependency provenance and consumes it as an active dependency source.

## Acceptance Criteria

- A1: issue prose dependency inference is disabled for active dependency graph construction.
- A2: GitHub native dependencies remain active dependency input.
- A3: structured Loom machine dependency blocks remain active dependency input.
- A4: fixtures and docs distinguish prose notes from active dependency truth.
