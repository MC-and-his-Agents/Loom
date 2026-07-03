# Current Status

## Derived Fact Chain View

- Item ID: WI-1900
- Goal: Rewrite repo-facing Loom carriers so long command output is represented by command/time/head/summary/artifact hash/global locator instead of inline logs.
- Scope: Update carrier/output artifact summarization paths for repo-local progress/status/review-facing evidence so long diagnostics live in global .loom tmp artifacts while repo truth stores concise summaries and locators.
- Execution Path: issue #1900 -> branch work/1900-carrier-artifact-locators -> PR -> review/merge-ready/closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1900.md
- Review Entry: .loom/reviews/WI-1900.json
- Validation Entry: python3 tools/check_cli_contract.py --surface governance-closeout; python3 tools/check_cli_contract.py --surface runtime-paths; python3 tools/loom.py suite validate --target . --item WI-1900 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1900 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1900 --json; git diff --check
- Closing Condition: Repo carriers store concise command/time/head/summary/hash/global locator evidence for long outputs, focused contract fixtures pass, PR is merged, and #1900 is closed.
- Current Checkpoint: merge
- Current Stop: Implementation, spec review, code review, PR metadata readback, and local validation are complete for PR #1937.
- Next Step: Re-run PR gate against the refreshed PR head, wait for hosted checks, then controlled-merge and closeout.
- Blockers: None recorded.
- Latest Validation Summary: 2026-07-03T08:56:54Z on PR #1937 head dae0eaa1fcb4356ec15b7a67f5dfd907c2779f5d, passed `python3 -m unittest test/output_envelope_test.py`, `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py test/output_envelope_test.py`, `python3 tools/check_cli_contract.py --surface runtime-paths`, `python3 tools/check_cli_contract.py --surface governance-closeout`, `python3 tools/loom.py suite validate --target . --item WI-1900 --json`, `python3 tools/loom.py suite evidence validate --target . --item WI-1900 --json`, `python3 tools/loom.py suite carrier validate --target . --item WI-1900 --json`, `python3 tools/loom.py pr metadata-readback 1937 --target . --work-item WI-1900 --branch work/1900-carrier-artifact-locators --head-sha dae0eaa1fcb4356ec15b7a67f5dfd907c2779f5d --surface merge_ready --json`, and `git diff --check`.
- Recovery Boundary: Continue from the WI-1900 committed diff for `tools/loom.py`, `tools/check_cli_contract.py`, `test/output_envelope_test.py`, and `.loom/specs/WI-1900/`.
- Current Lane: carrier-output-contract

## Runtime Evidence

- Run Entry: 2026-07-03T08:47:31Z WI-1900 implementation validated in `/Users/mc/dev/Loom` on branch `work/1900-carrier-artifact-locators`.
- Logs Entry: Long agent-safe full output remains artifact-backed; repo-facing envelope stores summary, locator, sensitivity marker, and artifact SHA-256 metadata.
- Diagnostics Entry: WI-1900 changes `tools/loom.py`, `tools/check_cli_contract.py`, output envelope tests, and WI-1900 suite carriers only; broad status/progress redesign and #1901 gate independence proof remain out of scope.
- Verification Entry: 2026-07-03T08:56:54Z local checks passed: output envelope unittest, py_compile_clean for touched Python files, runtime-paths, governance-closeout, suite validate/evidence/carrier validate, PR metadata readback for #1937, and git diff --check.
- Lane Entry: carrier-output-contract

## Sources

- Static Truth: .loom/work-items/WI-1900.md
- Dynamic Truth: .loom/progress/WI-1900.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
