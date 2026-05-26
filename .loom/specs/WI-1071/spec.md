# WI-1071 Spec

## Goal

Distinguish GitHub `mergeStateStatus == BLOCKED` from Loom semantic merge readiness in the controlled merge path.

## Requirements

- `DIRTY` and `DRAFT` host mergeability states remain hard blocks.
- `BLOCKED` is treated as a delegated host policy signal only after Loom-authored approval, required checks, PR head binding, and host enforcement readback pass.
- GitHub review comments, including author `COMMENTED`, remain evidence-only and never satisfy authored approval truth.
- `controlled-merge merge` continues to delegate the final host result to `gh pr merge`.
- Source, generated skill runtime, installed `.loom/bin`, and harness reference surfaces stay synchronized.

## Acceptance

- Positive fixture covers author `COMMENTED` guardian evidence, green required checks, green `loom-pr-merge-gate`, GitHub `BLOCKED`, and controlled merge check pass.
- Negative fixture coverage keeps `DIRTY`, `DRAFT`, missing or failing required checks, and head drift as blocking conditions.
- Harness docs explain host `BLOCKED` versus Loom semantic readiness without implying bypass of GitHub protection.
