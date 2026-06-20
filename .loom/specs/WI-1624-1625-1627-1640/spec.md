# WI-1624-1625-1627-1640 Suite Path Decision

- Suite path: not_applicable
- Rationale: This Work Item is a narrow CLI contract cutover that removes old install modes and old installed-state validity. It does not introduce a new product workflow beyond the already-frozen milestone #14 install contract.
- Consumer boundary: The implementation is covered by targeted CLI contract fixtures, smoke commands, host adapter check, release surface check, py_compile, and diff hygiene. Formal spec/plan artifacts are not required for this bounded cutover.
- Recheck condition: Reopen formal suite if this PR starts implementing Codex user-level plugin install/register, plugin payload generation, npm package content changes, release mechanics, or milestone closeout.
- Scope proof: Changed implementation files are limited to `tools/loom.py` and `tools/check_cli_contract.py`; carrier changes are limited to this Work Item and `.loom/status/current.md`.
- Review requirement: current-head review required before merge-ready.
