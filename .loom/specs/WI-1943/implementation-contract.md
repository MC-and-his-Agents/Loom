# WI-1943 Implementation Contract

- Suite path: minimal

## Ownership

- Owns terminal closeout carrier PR consumption in controlled merge.
- Owns closeout readback fallback to implementation PR host checks when the final closeout carrier PR has no retained merge-ready execution attempt.
- Owns focused CLI contract fixtures for the retained terminal closeout PR gate and closeout backlink readback paths.

## Contract

- A retained PR gate may satisfy controlled merge through `terminal_closeout_consumption` only when the terminal closeout result passed, the closeout-specific gate passed, and `closeout_pr_allowed` is true.
- Ordinary implementation PR retained gates still require the embedded merge checkpoint and current-head semantic review binding to pass.
- Final closeout carrier PR readback may consume the implementation PR host checks as legacy merge-ready evidence only when `merge_ready_expected_source == "implementation_pr"` and the retained merge-ready execution attempt is absent.
- Runtime copies and plugin payload hash must stay synchronized with the source `loom_flow.py` implementation.

## Non-Goals

- Do not change GitHub rulesets or branch protection.
- Do not relax ordinary implementation PR merge checkpoint requirements.
- Do not redesign closeout, release, or Work Item retirement semantics.

## Validation Binding

- A1: `python3 tools/check_cli_contract.py --surface controlled-merge` covers ordinary retained gate blocking and terminal closeout retained gate acceptance.
- A2: `python3 tools/check_cli_contract.py --surface governance-closeout` covers closeout readback fallback to implementation PR host checks for final closeout carrier PRs.
- A3: `python3 tools/loom.py merge check 1942 ... --pr-gate-result-file .loom/tmp/pr/pr-1942-gate-retained-154cc46e.json --json` replays the observed terminal closeout PR gate evidence.
- A4: `python3 tools/loom.py closeout --target . --item WI-1903 --issue 1903 --pr 1942 ... --json` replays the observed post-merge closeout readback.
