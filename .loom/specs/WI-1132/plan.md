# WI-1132 Plan

- Suite path: minimal

## Implementation Plan

- Add host truth signal vocabulary to carrier inspect/validate payloads.
- Read Work Item/recovery terminal state as validation context without making host writes.
- Classify Project/checklist/issue/PR mirror conflicts from task-carrier row source/provenance/freshness text.
- Block Project Done with issue open, checklist checked with evidence missing, PR merged with issue open, and active recovery versus terminal host claims as `carrier_truth_conflict`.
- Extend `tools/check_cli_contract.py` with a host signal conflict fixture.
- Update CLI surface docs to record #1132 behavior.

## Scenario Mapping

- Scenario S1 -> structural validation evidence: `python3 tools/check_cli_contract.py` host signal conflict fixture.
- Scenario S2 -> structural validation evidence: checklist/evidence conflict row in the host signal fixture.
- Scenario S3 -> structural validation evidence: PR/issue conflict row in the host signal fixture.

## Acceptance Mapping

- A1 -> test evidence: carrier inspect/validate payload includes `recognized_truth_signals`.
- A2 -> test evidence: carrier validate payload includes `truth_signal_classifications` and `host_signal_conflicts`.
- A3 -> test evidence: `project-done-issue-open` host conflict id.
- A4 -> test evidence: `checklist-checked-evidence-missing` host conflict id.
- A5 -> test evidence: `pr-merged-issue-open` host conflict id.
- A6 -> test evidence: existing carrier pass/missing/invalid/primary/deferred/truth conflict fixtures remain in `python3 tools/check_cli_contract.py`.
- A7 -> structural check evidence: focused `rg` for `host_signal_conflicts`, `carrier_truth_conflict`, `/speckit`, and `.specify`.

## Validation Commands

- `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `python3 tools/check_cli_contract.py`
- `python3 tools/loom.py suite validate --target . --item WI-1132 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1132 --json`
- `python3 tools/loom.py suite carrier inspect --target . --item WI-1132 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1132 --json`
- `git diff --check`
- focused `rg`
- `python3 tools/skills_surface.py check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .`
