# WI-1883 Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1883.md`
- FR / parent locator: https://github.com/MC-and-his-Agents/Loom/issues/1882
- Implementation issue locator: https://github.com/MC-and-his-Agents/Loom/issues/1883
- Release issue locator: https://github.com/MC-and-his-Agents/Loom/issues/1884
- Scope: generated host AGENTS execution guidance, root-entry generator parity, fixture/test updates, plugin payload metadata, and PR #1885 carrier evidence.
- Suite path: see `.loom/specs/WI-1883/spec.md` for the formal-suite bypass decision.
- Current implementation `HEAD`: `d3743a42cf1c16dc393c7284c47efbd4e52c7b2a` before WI-1883 carrier sync; final PR metadata must bind to the repaired PR head.
- PR locator: https://github.com/MC-and-his-Agents/Loom/pull/1885
- Host state locator: GitHub issue #1883 and PR #1885

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1883/spec.md` | formal-suite bypass decision | issue #1883 and WI-1883 carrier | Recheck if the PR expands beyond generated AGENTS guidance, runtime generator parity, fixture/test updates, or plugin payload metadata. |
| `plan.md` | `.loom/specs/WI-1883/plan.md` | present | issue #1883 and implementation plan | Recheck after validation strategy or ownership boundary changes. |
| suite path decision | `.loom/specs/WI-1883/spec.md` | formal-suite bypass | rationale in `.loom/specs/WI-1883/spec.md` | Recheck if full suite artifacts become required by scope, gate semantics, release mechanics, permissions, host writes, or downstream behavior. |
| execution breakdown / task carrier | `.loom/specs/WI-1883/task-carrier.md` | present | issue tree and PR #1885 | Recheck before merge and closeout. |
| review record | `.loom/reviews/WI-1883.json` | required before merge | implementation review | Recheck after semantic code, generated artifact, fixture, PR body, or validation summary changes. |
| merge-ready basis | PR #1885 hosted and local PR gate | required before merge | PR metadata and gate readback | Recheck after PR body, branch head, review, fact-chain, shadow, or evidence-map changes. |
| release handoff | issue #1884 | required after merge | issue tree | Recheck before release and final closeout. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py`; `skills/shared/scripts/loom_init.py`; `src/skills/shared/scripts/loom_init.py`; `plugins/loom/skills/shared/scripts/loom_init.py`; `.loom/bin/loom_init.py`; `docs/adoption/global-cli-user-plugin-contract.md` | generated host AGENTS execution guidance contract and suite path decision in `.loom/specs/WI-1883/spec.md` | work_item=WI-1883; scope=host-agents-execution-guidance; head=current PR head at merge-ready; pr=1885 | present | review; merge-ready; release handoff | Recheck after generated AGENTS wording, route/resume guidance, spec/review/gate freshness guidance, or root-entry generation changes. |
| EV-002 | test_evidence | `tools/check_cli_contract.py`; `examples/new-project/AGENTS.md`; `examples/new-project/.loom/bin/loom_init.py`; `plugins/loom/.codex-plugin/plugin.json`; validation commands listed in `.loom/progress/WI-1883.md` | validation strategy in `.loom/specs/WI-1883/plan.md` | work_item=WI-1883; scope=fixture-and-contract-parity; head=current PR head at merge-ready; pr=1885 | present | review; merge-ready; release handoff | Rerun skills surface, fixture drift/generation/canonicalization, adoption-host-metadata, aggregate CLI contract, release/package surfaces, and full `make loom-check` after code, fixture, or payload hash changes. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1883.md` | EV-001 EV-002 current validation summary and PR head binding | work_item=WI-1883; head=current carrier-sync PR head after review; implementation_head=d3743a42cf1c16dc393c7284c47efbd4e52c7b2a; validation_summary_sha256=d6f2babb954f4bdf56e328cdac289a680457a2c83a3c4cab3d08711fa54bc536; pr=1885 | present | PR gate; merge-ready; closeout | Refresh evidence-map, PR metadata, shadow carriers, review consumption, and hosted checks after branch head, validation summary, or PR body changes. |

## Deferred

No deferred evidence rows are claimed for WI-1883. Publishing the updated plugin/runtime payload is not deferred from the overall user request; it is owned by release Work Item #1884 after PR #1885 merges.
