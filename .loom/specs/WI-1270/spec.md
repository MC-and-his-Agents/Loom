# WI-1270 Suite Decision

- Suite path: not_applicable

- Suite-level not_applicable: rationale: WI-1270 is a narrow CLI contract surface decomposition in `tools/check_cli_contract.py`, not a product behavior or formal spec-suite implementation slice; consumer boundary: this decision only skips formal suite artifacts and does not skip current-head review, fact-chain, PR metadata, local validation, hosted checks, controlled merge, or closeout evidence; recheck condition: scope expands beyond named surface registration or changes runtime suite semantics; scope proof: implementation changes are limited to `tools/check_cli_contract.py` plus WI-1270 carrier binding, with no changes to `tools/loom.py`, `.loom/bin/loom_flow.py`, hosted workflows, release surfaces, metadata schema, or sibling issue scopes; review requirement: current_head_review_required.
