# Plan

## Steps

1. Extend fact-chain parsing with optional terminal closeout metadata while preserving legacy progress carrier compatibility.
2. Add `carrier closeout-sync` to the shared runtime and root CLI with dry-run default, explicit apply semantics, and no host mutations.
3. Update CLI contract tests for help matrix, dry-run no-write behavior, apply carrier write behavior, and structured metadata output.
4. Update methodology docs to define command responsibility boundaries.
5. Sync generated runtime copies and activate WI-1230-1231 carriers.
6. Run targeted local validation, then PR metadata/gates, hosted checks, controlled merge, and post-merge closeout.

## Acceptance Mapping

- AC-1 -> structural evidence: parser support in `fact_chain_support.py` and apply fixture in `tools/check_cli_contract.py`.
- AC-2 -> structural evidence: optional `Terminal Closeout Metadata` parsing preserves legacy Dynamic Facts parsing.
- AC-3 -> test evidence: `carrier closeout-sync` dry-run/apply fixture in `tools/check_cli_contract.py`.
- AC-4 -> test evidence: fixture asserts `host_mutations: false` and empty `host_actions`; docs boundary records host sync separation.
- AC-5 -> structural evidence: help matrix, CLI docs, closeout/workspace/host-action docs, and runtime copy parity.
