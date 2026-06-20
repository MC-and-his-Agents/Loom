# WI-1481 Evidence Map

| Evidence ID | Requirement | Locator | Command | Current Result | Freshness Rule |
| --- | --- | --- | --- | --- | --- |
| EV-001 | Normal output envelope includes summary, result, failure classification, key gaps, and full-output availability. | `test/output_envelope_test.py` | `python3 test/output_envelope_test.py` | pass on 2026-06-20 local branch | Rerun after `tools/loom.py` output helper changes. |
| EV-002 | Full output artifact persists original payload and returns a locator. | `test/output_envelope_test.py` | `python3 -m unittest discover -s test -p 'output_envelope_test.py'` | pass on 2026-06-20 local branch | Rerun after artifact path or payload schema changes. |
| EV-003 | Over-budget helper returns summary plus artifact locator without inline diagnostic payload. | `test/output_envelope_test.py` | `python3 test/output_envelope_test.py` | pass on 2026-06-20 local branch | Rerun after budget or envelope fields change. |
| EV-004 | Syntax, whitespace, suite, carrier, and broad CLI contract surfaces remain clean. | `tools/loom.py`; `test/output_envelope_test.py`; `.loom/specs/WI-1481/*` | `python3 tools/py_compile_clean.py tools/loom.py test/output_envelope_test.py`; `git diff --check`; `python3 tools/loom.py suite validate --target . --item WI-1481 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1481 --json`; `python3 tools/check_cli_contract.py --surface aggregate` | pass on 2026-06-20 local branch; aggregate took 422.95s | Rerun before PR gate. |
