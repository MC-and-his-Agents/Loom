# WI-1890 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | src/skills/shared/scripts/loom_check.py | S1 / A1 | published marketplace catalog fixture | present | review / PR gate / #1891 | Rerun source `loom_check` after checker or catalog contract changes. |
| EV-002 | behavior_evidence | src/skills/shared/scripts/loom_check.py | S2 / A2 | installed-state and outside-path rejection fixture | present | review / PR gate / #1891 | Rerun source `loom_check` after checker or catalog contract changes. |
| EV-003 | behavior_evidence | docs/adoption/installation-taxonomy.md; docs/adoption/global-cli-user-plugin-contract.md; docs/evidence/README.md | A3 | adoption contract docs | present | review / #1891 / #1892 / closeout | Recheck docs when marketplace, CLI, plugin, or repo adoption boundary changes. |
| EV-004 | test_evidence | python3 tools/py_compile_clean.py .loom/bin/loom_check.py skills/shared/scripts/loom_check.py src/skills/shared/scripts/loom_check.py plugins/loom/skills/shared/scripts/loom_check.py | S3 / A4 | checker syntax across source/generated/runtime copies | present | review / PR gate | Rerun after checker copy changes. |
| EV-005 | test_evidence | python3 tools/skills_surface.py check; python3 tools/check_npm_package.py --surface runtime-copy-parity; python3 tools/check_npm_package.py --surface plugin-payload-hash | S3 / A4 | generated skills/runtime/plugin payload parity | present | review / PR gate / release consumer | Rerun after generated skills, runtime copy, or plugin payload metadata changes. |
| EV-006 | test_evidence | python3 tools/loom_check.py --profile source --source-surface source-self-fixture . | S1 S2 S3 / A1 A2 A4 | source self-fixture validation | present | review / PR gate / #1891 | Rerun after checker/docs/generated payload changes and before review. |
| EV-007 | fresh_verification_input | .loom/progress/WI-1890.md | EV-001-EV-006 / A5 | current branch / current head / WI-1890 | present | review / merge-ready / closeout | Refresh after final validation, PR metadata, review, hosted checks, and merge readback. |

## Deferred / External Actions

| Subject | Status | Rationale | Consumer Boundary | Recheck Condition | Follow-up Locator |
| --- | --- | --- | --- | --- | --- |
| published marketplace catalog file | deferred | #1890 only freezes checker semantics; the actual `.agents/plugins/marketplace.json` file is owned by the next Work Item. | #1891 planning and review | Start #1891 after #1890 PR is accepted or merged. | https://github.com/MC-and-his-Agents/Loom/issues/1891 |
| end-user install documentation | deferred | #1890 updates minimum contract language; complete install guidance is a separate documentation WI. | #1892 review / milestone closeout | Start #1892 after #1891 catalog behavior is known. | https://github.com/MC-and-his-Agents/Loom/issues/1892 |
| runtime marketplace install evidence | not_required | #1890 does not add a catalog file or run Codex marketplace installation. | review / PR gate / closeout for #1890 | Require runtime install evidence if a future WI executes marketplace installation. | https://github.com/MC-and-his-Agents/Loom/issues/1891 |
