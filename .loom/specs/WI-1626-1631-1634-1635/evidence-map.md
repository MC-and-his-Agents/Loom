# WI-1626-1631-1634-1635 Evidence Map

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py` | issues #1626/#1635 | `host verify` checks metadata-only repository adoption and Codex user-level provider registration; repo-local residue remains hard-blocking. | present | PR5 host verification and legacy gate | Recheck if host parser, doctor, installed-state, or legacy surface classification changes. |
| EV-002 | behavior_evidence | `package.json` | issue #1631 | npm package omits root `skills/`, includes `src/skills` and `plugins/loom`, and validates plugin payload parsing through package checks. | present | PR5 package surface and release preflight | Recheck after package files, npm dry-run contents, plugin manifest, or registry changes. |
| EV-003 | behavior_evidence | `docs/adoption/legacy-install-migration.md` | issue #1634 | Old repo-local install migration path is explicit: install global CLI, install/register Codex user plugin, metadata-only adopt, verify, then explicitly migrate/remove residue. | present | PR5 docs and release notes input | Recheck after installation command semantics or legacy gate output changes. |
| EV-004 | test_evidence | `.loom/progress/WI-1626-1631-1634-1635.md` | EV-001; EV-002; EV-003 | Static, CLI contract, package, host adapter, release surface, doc sync, suite, carrier, build, review, and shadow checks are recorded in the Work Item progress carrier. | present | review, PR gate, hosted checks, closeout | Refresh progress, review, shadow, and PR metadata after head or validation evidence changes. |
| EV-005 | fresh_verification_input | `.loom/progress/WI-1626-1631-1634-1635.md` | EV-001; EV-002; EV-003; EV-004 | Current-head verification combines behavior evidence, package evidence, migration docs, and aggregate test evidence for PR5. | present | merge-ready, hosted gate, and closeout | Re-run validation after any implementation, package, docs, carrier, or PR metadata change. |
