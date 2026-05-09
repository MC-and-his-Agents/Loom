# Execution Attempt Envelope

`execution_attempt` is Loom's runtime evidence envelope for one command attempt. It records what a flow tried, which Work Item and workspace it was bound to, the result classification, and where the evidence can be re-read.

It is evidence, not authored progress. The envelope must never carry recovery-owned fields such as `current_stop`, `next_step`, `blockers`, `latest_validation_summary`, `current_checkpoint`, `current_lane`, `recovery_boundary`, or `closing_condition`. Those fields remain authored only in the Work Item fact chain and recovery/status carriers.

## Stable Contract

Each envelope uses `schema_version: loom-execution-attempt/v1` and includes:

- `attempt_id`: stable identifier for this command attempt.
- `item_id`: active Work Item consumed from the fact chain.
- `command`: Loom command surface, for example `flow`.
- `operation`: command operation, for example `resume`, `review`, or `merge-ready`.
- `result`: one of `pass`, `block`, or `fallback`.
- `created_at`: UTC timestamp for evidence ordering.
- `head_sha`: git HEAD at the time the attempt was emitted, or `unknown-head`.
- `workspace`: read-only binding summary with `entry` and resolved `path`.
- `failure`: `{category, execution_classification, execution_summary, missing_inputs, fallback_to}`.
  `category` is `none`, `runtime_state`, `fact_chain`, `state_check`, `runtime_evidence`, `checkpoint`, `review`, `repo_specific`, `recovery_readiness`, or `unknown`.
  `execution_classification` is `none`, `stall`, `timeout`, `retry_exhaustion`, or `unknown`.
- `evidence`: `{locator, status}` pointing to the persisted attempt evidence. Missing or unreadable evidence must be reported as `missing`; it must not be treated as fresh.

## Persistence And Freshness

Runtime implementations may persist attempts under `.loom/runtime/attempts/<item-id>/`. This path is runtime evidence and may be ignored by git. A `latest.json` pointer may be used as the status read surface, but it is fresh only when:

- the envelope is valid JSON and satisfies the stable contract;
- `item_id` matches the current fact-chain item;
- `head_sha` matches current git HEAD;
- the envelope contains no recovery-authored progress fields.

Stale attempts may be shown as stale evidence, but status must not present them as current execution truth.

## Provenance Rules

- Attempts can summarize command results, steps, failures, fallback targets, and evidence locators.
- Attempts may classify execution failures such as `stall`, `timeout`, or `retry_exhaustion`, but they do not create a scheduler state machine and do not authorize automatic retry.
- Attempts can reference authored carriers by locator but must not duplicate their authored progress values.
- Attempts are append-only runtime evidence for observability. They do not advance checkpoints, close Work Items, change review decisions, or satisfy merge-ready by themselves.
