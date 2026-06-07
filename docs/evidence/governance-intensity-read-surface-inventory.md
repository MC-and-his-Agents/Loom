# Governance Intensity Read Surface Inventory

本文件是 #1320 的只读 inventory。它盘点 Loom 支持治理强度字段时需要读取或传播的 CLI、gate、carrier、PR body、review artifact、suite validate、merge-ready 与 closeout 面。

本文件不定义新合同，不实现 parser、gate 行为、metadata schema、fixtures、`.loom/bin` 分发内容或 AGENTS 规则。字段语义以 [tiered-gate-consumption-contract.md](../methodology/harness/tiered-gate-consumption-contract.md) 为准，Loom 路径语义以 [loom-governance-intensity-mapping.md](../methodology/governance/loom-governance-intensity-mapping.md) 为准。

## Scope

- Issue: #1320
- Branch: `work/1320-tier-support-inventory`
- Base readback: branch starts at `origin/main` head `d2191e73024d1d7e747fd8935c051c8c0df3be90`
- Inventory type: docs/carrier only
- Non-goals: no `tools/` behavior change, no `.loom/bin` generated runtime change, no fixtures, no gate/parser/schema implementation, no AGENTS body change

## Contract Baseline

The frozen contract requires a future machine carrier to represent:

| Field | Current contract source | Current implementation status |
| --- | --- | --- |
| `governance_intensity` | `tiered-gate-consumption-contract.md` section 2 | must-change: not present in repo PR metadata contract or Work Item carrier |
| `change_class` | `tiered-gate-consumption-contract.md` section 2 | must-change |
| `suite_path` | `tiered-gate-consumption-contract.md` section 2; existing suite CLI markers | maybe-change: suite CLI reads path markers, but no unified governance carrier field |
| `suite_not_applicable` | `tiered-gate-consumption-contract.md` section 3 | must-change for carrier/schema; suite validate already checks rationale text for suite readiness |
| `review_requirement` | `tiered-gate-consumption-contract.md` section 2 | must-change |
| `fact_chain_required` | `tiered-gate-consumption-contract.md` section 2 | maybe-change: current fact-chain is required by gates, but not expressed as a governance field |
| `pr_gate_required` | `tiered-gate-consumption-contract.md` section 2 | maybe-change: current PR gate is required by process, but not expressed as a governance field |
| `release_judgment` | `tiered-gate-consumption-contract.md` section 2 | must-change: release/no-release evidence exists as text/process, not unified field |
| `closeout_required` | `tiered-gate-consumption-contract.md` section 2 | must-change |
| `upgrade_triggers` | `tiered-gate-consumption-contract.md` section 2 and 6 | must-change |

## Read Surface Matrix

| Surface | Current read path | Current behavior | Governance intensity classification | Notes for implementation issues |
| --- | --- | --- | --- | --- |
| CLI router | `tools/loom.py` `handle_pr`, `handle_merge`, `handle_carrier`, `handle_fact_chain` | Routes to repo-local or generated flow commands and passes flags such as `--item`, `--head-sha`, `--body-file`, `--pr-gate-result-file` | not_applicable | Keep tier logic out of the router unless #1321 needs argument plumbing only. |
| Fact-chain | `.loom/bin/fact_chain_support.py` `parse_work_item`, `parse_recovery_entry`, `parse_status_surface`; `skills/shared/scripts/loom_flow.py` `load_context` | Reads Work Item, recovery entry, status surface, review locator, workspace, validation summary, current checkpoint | maybe-change | If #1321 stores tier in Work Item/progress, parsing may need a new field. Avoid creating parallel truth. |
| Work Item carrier | `.loom/work-items/*.md` `Static Facts` | Reads goal, scope, execution path, workspace, recovery, review, validation, closing condition | must-change | Best candidate for authored governance-strength locator or backlink, but fields must be structured enough for fail-closed consumption. |
| Progress carrier | `.loom/progress/*.md` `Dynamic Facts`, `Execution Ledger`, `Terminal Closeout Metadata` | Reads current checkpoint, validation summary, blockers, lane, terminal metadata | maybe-change | Good for current status and closeout metadata; avoid making it the only source of static tier classification. |
| Status surface | `.loom/status/current.md`; `.loom/bin/loom_status.py` status aggregation | Displays current fact-chain, runtime evidence, release and closeout status | maybe-change | Useful verification surface after #1321/#1322; not ideal as primary authored tier source. |
| Repo interface metadata contract | `.loom/companion/repo-interface.json` `metadata_contract.fields` | Currently `fields: []`; PR metadata preflight has no repo-specific governance block to enforce | must-change | #1321 should define the minimal machine carrier here or an explicitly linked schema. |
| PR template | `.github/PULL_REQUEST_TEMPLATE.md` `PR Metadata Machine Carrier` section | Instructs preserving declared repo-specific machine blocks and readback preflight | must-change | Template lacks governance intensity placeholders and release/no-release machine fields. |
| PR metadata preflight | `skills/shared/scripts/loom_flow.py` `metadata_contract_raw_fields`, `validate_pr_metadata_envelope`, `pr_metadata_preflight_payload` | Reads repo-interface metadata fields, HTML comment JSON blocks, required fields, parser version, rendered/readback hashes | must-change | #1321 should add governance fields to the declared contract and validate missing/unknown/head mismatch. |
| Suite inspect/validate | `tools/loom.py` `suite_path_marker_values`, `suite_inspect_payload`, `suite_validate_payload` | Reads `Suite path: full|minimal|not_applicable`, required artifacts, not_applicable rationale, consumer boundary and recheck condition | maybe-change | Existing suite path support is usable; #1322 may need tier-aware consumption rather than changing suite validation first. |
| Suite gate propagation | `skills/shared/scripts/loom_flow.py` `suite_gate_required_for_surface`, `suite_gate_payload_for_surface`, `suite_gate_not_applicable_payload` | Propagates suite evidence/carrier validation to pre-review, review, merge-ready and closeout surfaces | must-change | #1322 should consume tier here so `not_applicable` narrows only formal suite artifacts. |
| Spec review gate | `skills/shared/scripts/loom_flow.py` `spec_review_gate_payload` | Uses suite validation result and review record state to decide spec review applicability | must-change | Needs to distinguish legal docs-governance not_applicable from missing/invalid suite evidence. |
| Review artifact | `.loom/reviews/*.json`; `skills/shared/scripts/loom_flow.py` `load_review_record` | Requires schema, item, decision, kind, summary, reviewer, `reviewed_head`, validation summary | maybe-change | Current head binding exists. #1321 may add consumed governance carrier fields, but review record should not become the only tier source. |
| Review status and merge checkpoint | `skills/shared/scripts/loom_flow.py` `implementation_review_status_payload`, `checkpoint_payload("merge")`, `build_review_flow_payload` | Consumes review, spec review, suite gate, budget/governance lint and checkpoint state | must-change | #1322 must prove current-head review still blocks when docs-governance path is light. |
| PR gate | `skills/shared/scripts/loom_flow.py` `pr_gate_payload`, `handle_pr_gate` | Reads PR host payload, PR body `Loom Work Item`, `Head SHA`, `Branch`, local checkout head, review artifact, merge checkpoint, PR metadata preflight | must-change | #1322 should ensure tier-aware merge checkpoint and metadata preflight are consumed before PR gate passes. |
| Controlled merge | `skills/shared/scripts/loom_flow.py` `controlled_merge_payload`, `handle_controlled_merge` | Consumes live/retained PR gate, merge gate, PR head, checks, branch protection/ruleset, merge method | maybe-change | If #1322 keeps tier enforcement inside PR gate/merge-ready, wrapper can consume existing results. |
| Release/no-release | `.loom/bin/governance_surface.py` `build_governance_surface`; `.loom/bin/loom_status.py`; `skills/shared/scripts/loom_flow.py` `closeout_payload` | Reads repo interface release targets when present; current root repo interface has no release target contract | must-change | #1321/#1322 need an explicit `release_judgment` field or locator; #1324 can own broader release evidence closeout. |
| Closeout gate | `skills/shared/scripts/loom_flow.py` `closeout_payload`, `closeout_suite_gate_subchecks`, `closeout_reconciliation_result`; `.loom/bin/fact_chain_support.py` terminal metadata parser | Consumes fact-chain, issue/PR/project readback, release target, reconciliation, suite gate, terminal metadata | maybe-change | #1322 should preserve closeout requiredness. #1323 can add negative fixtures for missing closeout/release fields. |
| Carrier closeout sync | `skills/shared/scripts/loom_flow.py` `carrier_closeout_sync_payload` | Writes `Terminal Closeout Metadata` to progress carrier with issue, PR, merge commit, target branch, closed time, evidence locator | not_applicable for tier logic | Do not extend for #1320. Only #1321 should decide whether terminal metadata needs a tier field. |
| Shadow parity | `.loom/shadow/closeout-loom.json`, `.loom/shadow/closeout-repo.json` | Stores source files and hashes only | deferred | Keep as hash/source evidence unless a later issue makes shadow parity a blocking governance-strength surface. |
| `.loom/closeout/` directory | none | Directory absent | not_applicable | Do not create a new closeout artifact tree for #1320. Existing closeout truth is progress/review/status/shadow plus host readback. |
| `scripts/` directory | none | Directory absent | not_applicable | No read surface exists in this repository. |

## Current Sample Evidence

The #1316/#1317 closeout provides useful samples but should not be retroactively edited:

- `.loom/specs/WI-1316-1317/spec.md` records `Suite path: not_applicable` with rationale, consumer boundary, recheck condition, scope proof and review requirement.
- `.loom/reviews/WI-1316-1317.spec.json` approves that suite decision at reviewed head `fc5317a38d413bf4323e9a621cd0410faee18fa5`.
- `.loom/reviews/WI-1316-1317.json` records final closeout review at reviewed head `e208355f956bae6a3d8bf30c8a2e60f2a72f32c5`.
- `.loom/progress/WI-1316-1317.md` terminal metadata records PR #1335, merge commit `52bbff388384e8fa3f0928be83c53aef5501dc9c`, target branch `main`, and closeout evidence.

These samples express suite not_applicable, review/head binding and closeout consumed evidence, but they do not contain the unified governance fields frozen by #1317. They are samples for #1321/#1322/#1323, not schema-complete artifacts.

## Classification Summary

### Must Change

- Add a formal governance-intensity machine carrier in #1321, likely through `.loom/companion/repo-interface.json` metadata contract plus a Work Item/progress locator.
- Add PR body machine fields for `governance_intensity`, `change_class`, `suite_path`, `suite_not_applicable`, `review_requirement`, `release_judgment`, `closeout_required`, and `upgrade_triggers`.
- Make PR metadata preflight fail closed for missing governance fields, unknown enums, invalid `suite_not_applicable`, PR body/head mismatch, and carrier mismatch.
- Make #1322 consume the carrier through suite gate propagation, spec review, implementation review, merge checkpoint and PR gate.

### Maybe Change

- Extend suite validate output only if #1322 needs tier-aware diagnostics. Existing `suite_path` and rationale validation can remain the source for formal suite readiness.
- Extend review artifact consumed inputs to record the governance carrier consumed by review. Keep `reviewed_head` as the review binding source.
- Extend status output as a verification/readback surface after #1321/#1322. Avoid making status the authored tier source.
- Extend controlled merge only if tier enforcement remains outside retained PR gate/merge-ready results.
- Extend terminal closeout metadata only if #1321 decides closeout needs the tier field in terminal carrier truth.

### Not Applicable

- Do not put tier logic in `tools/loom.py` router functions beyond argument plumbing.
- Do not change low-level `git_head_sha`, `git_branch`, GitHub locator detection or workspace resolution for tier support.
- Do not create `.loom/closeout/` for this inventory.
- Do not retroactively edit closed #1316/#1317 review records to add new governance fields.
- Do not treat the absent `scripts/` directory as an uninspected surface.

### Deferred

- Shadow parity schema upgrade for governance strength.
- Broader release/no-release documentation and evidence closeout, which belongs to #1324.
- Full positive/negative fixture matrix, which belongs to #1323 after #1321/#1322 are implemented.
- External orchestrator or profile display of tier semantics unless a consumer requires it.

### Unknown / Follow-Up

- Whether #1321 should store the primary governance carrier as a repo-interface machine block only, a Work Item field, or a linked dual-surface. The inventory recommends one authored source plus PR body/readback mirror, but does not choose schema details.
- Whether `loom_check.py` needs profile-specific governance-strength subchecks after #1322. This inventory did not run high-cost `loom_check` to discover unimplemented future behavior.
- Whether current GitHub PR body history for PR #1335/#1340 contains ad hoc release/no-release text. That is historical evidence only and should not define the new machine carrier.

## Downstream Touchpoints

### #1321: Metadata Carrier

Minimum touchpoints:

- `.loom/companion/repo-interface.json` `metadata_contract.fields`
- PR metadata preflight in `skills/shared/scripts/loom_flow.py`
- A repo-authored carrier locator in Work Item/progress or an explicitly linked schema
- PR template guidance for rendering and readback of the governance machine block

Targeted validation:

- `loom pr metadata-preflight --body-file <rendered> --compare-body-file <readback> --surface merge_ready`
- missing field, unknown enum, invalid `suite_not_applicable`, PR body/head mismatch, carrier mismatch negative cases
- `loom suite validate --target . --item <item> --json` for `suite_path: not_applicable`
- `loom pr gate <pr> --head-sha <sha> --work-item <item> --json`

### #1322: Docs-Governance Light Gate

Minimum touchpoints:

- `suite_gate_required_for_surface`
- `suite_gate_payload_for_surface`
- `spec_review_gate_payload`
- `implementation_review_status_payload`
- `checkpoint_payload("merge")`
- `pr_gate_payload`

Targeted validation:

- docs-governance `suite_path: not_applicable` positive case returns suite `not_applicable` while review, fact-chain, PR metadata, release judgment and closeout remain required.
- runtime/fixture/release-impact change cannot pass as `governance_intensity=light`.
- stale `reviewed_head`, missing `release_judgment`, missing rationale and PR body mismatch block.
- `loom merge check <pr> --head-sha <sha> --work-item <item> --json` consumes the tier-aware PR gate result.

### #1323: Escalation And Abuse Fixtures

Minimum fixture set:

- missing `suite_not_applicable`
- `change_class=runtime` with `governance_intensity=light`
- reviewed head does not cover PR head
- missing `release_judgment`
- `deferred` misused as `not_applicable`
- PR body and carrier mismatch

Targeted validation:

- Each negative fixture maps to `tiered-gate-consumption-contract.md` section 5 or 6.
- Results must be `block`, not advisory warnings.
- Fixtures should test real gate behavior after #1321/#1322, not only strings.

## Verification For This Inventory

This inventory should be verified with:

- `git diff --check`
- `python3 tools/loom.py suite validate --target . --item WI-1320 --json`
- `python3 tools/loom.py fact-chain --target . --item WI-1320 --json`
- review record bound to the final PR head
- PR metadata readback/preflight as applicable for this repository
- PR gate, hosted required checks, controlled merge, and post-merge closeout sync
