# Implementation Contract

## Owned Behavior

- `spec_review_gate_payload` consumes the canonical `suite validate` JSON envelope.
- Legal formal-suite NA results make only the formal spec review gate non-required.
- Blocked suite validation remains blocking for spec review.
- Implementation review remains required and is evaluated by `implementation_review_status_payload`.

## Non-Goals

- Do not weaken PR head binding.
- Do not skip implementation review, CI, fact-chain, release/no-release evidence, or closeout evidence.
- Do not introduce fake minimal suite files for docs-only contract PRs.
- Do not modify the four A-D contract PR branches in this unblocker.

## Verification Contract

- `assert_docs_contract_suite_not_applicable_gate_contract` covers legal formal-suite NA consumption, invalid rationale blocking, and implementation review non-bypass.
- `tools/loom.py suite validate --target . --item WI-1302 --json` covers this unblocker suite.
- `tools/check_cli_contract.py` covers the repo-local CLI contract.
