# Full Spec Suite CLI Surface Plan

本文件规划 full spec suite 相关 `loom` CLI 自动化入口。它是 #1052 的规划产物，只冻结后续 CLI implementation 的命名、行为分类、JSON 输出、failure taxonomy 与接入边界；本文件不实现 CLI，不新增真实命令入口。

## 1. 消费边界

本规划只消费已冻结合同，不反向改写 core 语义：

- Delivery planning、issue-tree plan、PR slicing 与 GitHub host mapping 由 [../templates/delivery-planning.md](../templates/delivery-planning.md)、[../templates/issue-tree-plan.md](../templates/issue-tree-plan.md)、[../templates/pr-slicing.md](../templates/pr-slicing.md) 与 [../../adoption/github-profile.md](../../adoption/github-profile.md) 定义。
- Full / minimal spec suite 由 [../templates/spec-suite.md](../templates/spec-suite.md) 定义。
- Execution breakdown 与 task carrier 由 [../templates/execution-breakdown.md](../templates/execution-breakdown.md) 与 [task-carrier-contract.md](./task-carrier-contract.md) 定义。
- Evidence-map 与 consistency-analysis 由 [../templates/evidence-map.md](../templates/evidence-map.md) 与 [../templates/consistency-analysis.md](../templates/consistency-analysis.md) 定义。
- Review、merge-ready 与 closeout 消费顺序由 [gate-chain.md](./gate-chain.md) 定义。
- Current CLI authority、JSON minimum shape 与 fail-closed rules 由 [cli-first-control-plane.md](./cli-first-control-plane.md) 与 [cli-command-matrix.md](./cli-command-matrix.md) 定义。

禁止项：

- 不复制 spec-kit `/speckit.*` 命令名、`.specify/` layout 或 extension trust model。
- 不让 CLI 生成的 carrier、JSON、status 或 host mirror 替代 `Work Item`、recovery、review record、merge checkpoint、closeout basis 或 docs/source 合同。
- 不把 `tasks.md`、Project `Done`、checklist checked、PR merged 或 issue closed 当作 behavior evidence、test evidence、review pass、merge-ready pass 或 closeout truth。

## 2. 建议命令族

后续 CLI implementation 应优先放在 `loom suite ...` 命名空间下，避免把 formal spec suite 的子面拆成多个顶层命令。

| Command | Status for #1052 | Behavior class | Scope |
| --- | --- | --- | --- |
| `loom suite inspect` | planned | read-only | 读取 Work Item、suite path decision、artifact inventory、delivery planning、task carrier、evidence-map、consistency-analysis 与 gate-chain locators。 |
| `loom suite scaffold` | planned | scaffold-write | 生成或补齐 suite scaffold 文件；必须显式 `--apply`，默认只输出 plan。 |
| `loom suite validate` | implemented core (#1120/#1121) | validate | 校验 suite path decision、core required artifact envelope 与 full path conditional artifact inventory；minimal `not_applicable` rationale、spec -> plan mapping、task carrier mapping 与 evidence-map freshness 由后续 Work Items 加深。 |
| `loom suite analyze` | planned | analyze | 运行 consistency-analysis 风格的跨工件分析，只输出 finding 与 remediation direction，不修文件。 |
| `loom suite evidence inspect` | planned | read-only | 读取 evidence-map row、source locator、freshness、HEAD / PR / merge binding。 |
| `loom suite evidence scaffold` | planned | scaffold-write | 为当前 suite 生成 evidence-map scaffold；必须显式 `--apply`。 |
| `loom suite evidence validate` | planned | validate | 校验 behavior evidence、test evidence、fresh verification evidence 的 mapping 与 freshness。 |
| `loom suite consistency inspect` | planned | read-only | 读取现有 consistency-analysis 结果和 gate consumer boundary。 |
| `loom suite consistency analyze` | planned | analyze | 生成 `loom-consistency-analysis/v1` 风格分析结果，不写修复。 |
| `loom suite carrier inspect` | planned | read-only | 读取 execution breakdown unit 与 task carrier normalized status。 |
| `loom suite carrier validate` | planned | validate | 校验 carrier locator、relationship、normalized status、Work Item / breakdown / spec / plan / validation 回链。 |

`loom spec` 与 `loom plan` 保持现有 scenario surface：它们暴露 expected locators 并在 authoring carriers 缺失时 fail closed。后续若实现 `loom suite scaffold`，它可以调用或复用 `loom spec` / `loom plan` 的 locator 规则，但不得让 `loom spec` / `loom plan` 变成 full suite orchestrator。

## 3. 行为分类

### Read-only

Read-only 命令只读取 repo、host、runtime evidence 与 docs/source contracts。它们可以返回 derived summary，但不得写入 repo、host、Project、PR、issue、runtime attempts 或 generated skills surface。

适用命令：

- `suite inspect`
- `suite evidence inspect`
- `suite consistency inspect`
- `suite carrier inspect`

### Scaffold-write

Scaffold-write 命令只能写入 caller 指定的 repo-local planning / scaffold target，并且必须满足：

- 默认 dry-run，`mutates: false`。
- 只有显式 `--apply` 才能写。
- 写入前输出 planned files、source template、consumed locators、overwrite policy 与 rollback note。
- 不创建 GitHub issue、Project item、PR、review record 或 merge-ready result。
- 不更新 generated skills surface；docs/source 到 generated 的同步仍由 skills surface workflow 处理。

适用命令：

- `suite scaffold`
- `suite evidence scaffold`

### Validate

Validate 命令只判断当前 artifacts 是否满足已冻结合同。它们可以返回 `pass` / `block` / `advisory` / `not_applicable`，但不得修复文件。

适用命令：

- `suite validate`
- `suite evidence validate`
- `suite carrier validate`

### Analyze

Analyze 命令输出 finding、classification、consumer impact 与 remediation direction。它们不得执行 remediation，也不得把 advisory gap 自动升级为 blocking，除非 owning contract 明确规定当前 consumer surface 必须阻断。

适用命令：

- `suite analyze`
- `suite consistency analyze`

### Fail-closed

所有 planned 命令在实现前必须作为 unknown 或 reserved surface fail closed。实现后仍必须在输入缺失、schema drift、host drift、stale evidence、parallel truth 或 mutating action 缺少 `--apply` 时 fail closed。

## 4. JSON 输出字段

所有命令默认使用 `loom-cli-output/v1` 最小字段，并在 `payload` 中嵌入 suite-specific data。建议 envelope：

```json
{
  "schema_version": "loom-cli-output/v1",
  "command": "suite validate",
  "result": "pass|block|advisory|not_applicable",
  "generated_at": "ISO-8601 timestamp",
  "target": ".",
  "item_id": "WI-1052",
  "summary": "human-readable one-line summary",
  "mutates": false,
  "failed_layer": "suite|spec|plan|evidence_map|consistency_analysis|task_carrier|gate_chain|host_state",
  "fail_closed_reason": "missing_source_locator",
  "fallback_to": "loom suite inspect --target . --item WI-1052 --json",
  "payload": {}
}
```

Suite payload fields:

- `suite_path`: `full | minimal | not_applicable | unknown`
- `suite_locator`
- `path_decision_locator`
- `artifact_inventory`
- `not_applicable_rationale`
- `deferred_items`
- `consumed_contracts`
- `story_readiness_locator`
- `business_confirmation_locator`
- `spec_locator`
- `plan_locator`
- `delivery_planning_locator`
- `issue_tree_plan_locator`
- `pr_slicing_locator`
- `execution_breakdown_locator`
- `task_carrier_locators`
- `evidence_map_locator`
- `consistency_analysis_locator`
- `gate_chain_consumption`
- `head_sha`
- `pr`
- `host_state_locator`
- `validation_summary_locator`
- `findings`
- `missing_inputs`
- `advisory_gaps`
- `blocking_gaps`
- `remediation_directions`

Scaffold-write payload fields:

- `planned_writes`
- `source_templates`
- `overwrite_policy`
- `apply_required`
- `rollback_note`
- `created_locators`

Validate / analyze finding fields:

- `id`
- `classification`: `blocking | advisory | stale | missing | conflict | not_applicable`
- `failure_kind`
- `surface`
- `source_locator`
- `conflicting_locator`
- `freshness`
- `binding`
- `consumer_impact`
- `remediation_direction`
- `fallback_to`

## 5. Failure Taxonomy

后续实现应复用下列 failure kinds，并把它们映射到 `failed_layer`、`fail_closed_reason` 与 `fallback_to`。

| Failure kind | Default result | Failed layer | Meaning | Fallback |
| --- | --- | --- | --- | --- |
| `missing_work_item` | block | work_item | 当前目标不是可读取的 Work Item。 | `loom issue inspect` 或 `loom fact-chain` |
| `missing_suite_path_decision` | block | suite | 找不到 full / minimal / not_applicable path decision。 | `loom suite inspect` |
| `missing_required_artifact` | block | suite | full path 必需工件缺失或不可读。 | `loom suite scaffold` dry-run |
| `invalid_not_applicable_rationale` | block | suite | minimal path 缺 rationale、consumer boundary 或 recheck condition。 | `loom suite validate` after authoring rationale |
| `deferred_as_completed` | block | suite | deferred 被当作 completed 或 ready 消费。 | 回到 owning issue / follow-up locator |
| `missing_spec_plan_mapping` | block | spec/plan | scenario -> validation 或 acceptance -> test mapping 缺失。 | `loom suite validate` |
| `missing_task_carrier_locator` | advisory or block | task_carrier | 当前 path 需要 task carrier，但 locator 缺失。full path 默认 block。 | `loom suite carrier validate` |
| `carrier_truth_conflict` | block | task_carrier | carrier / Project / checklist 与 Work Item 或 recovery truth 冲突。 | `loom suite carrier inspect` + host reconciliation |
| `missing_evidence_map` | block | evidence_map | 当前 gate 需要 evidence-map 但 locator 缺失。 | `loom suite evidence scaffold` dry-run |
| `stale_evidence` | block | evidence_map | evidence 绑定旧 head、旧 scope、旧 validation summary 或旧 PR head。 | 重新验证并更新 evidence locator |
| `missing_fresh_verification_evidence` | block | evidence_map | behavior/test evidence 无法组合成当前对象的 fresh evidence。 | `loom suite evidence validate` |
| `blocking_consistency_gap` | block | consistency_analysis | consistency-analysis 存在 blocking finding。 | `loom suite consistency analyze` |
| `host_state_conflict` | block | host_state | issue、PR、Project、checks、branch 或 merge state 冲突。 | `loom reconcile` dry-run |
| `head_or_pr_drift` | block | host_state | current head、reviewed head、PR head 或 merge commit 包含关系不一致。 | 回到 review 或 merge gate |
| `missing_prerequisite_gate` | block | gate_chain | gate chain 缺前序结论。 | 对应 `loom gate ...` |
| `mutating_action_requires_apply` | block | cli | scaffold-write 或 host write 未显式 `--apply`。 | 重跑 dry-run 或显式 apply |
| `reserved_surface` | block | cli | planned command 尚未实现。 | 当前 docs/source workflow |
| `schema_drift` | block | cli | 输入或输出 schema 与冻结合同不一致。 | 回到 owning contract / implementation issue |

## 6. `loom doctor` / `loom verify` 接入点

`loom doctor` 与 `loom verify` 不应直接执行 full suite validation。它们的接入边界是发现当前 repository 是否安装并暴露了可执行的 suite command surface。

建议后续实现：

- `loom doctor --target . --json`
  - 读取 installed-state、CLI command matrix 与 legacy/mixed surfaces。
  - 若 suite commands 未实现但当前 version 未声明支持它们，结果仍可 pass。
  - 若 installed-state 声明支持 suite commands，但 `loom help --json` 缺命令或命令输出 schema drift，fail closed to `loom repair plan` 或 `loom suite inspect`。
- `loom verify --target . --json`
  - 继续消费 `doctor`。
  - 仅在 target profile 或 Work Item gate 明确要求 full suite command surface 时，才要求 `suite validate` / `suite evidence validate` / `suite consistency analyze` 可执行。
  - 不把 validation-only parity 自动提升为 blocking gate。

## 7. Scenario Skills 接入点

Scenario skills 仍是 agent-facing entrance；CLI 是 machine interface。后续接入应按现有 route matrix 消费，而不是在 skill 中重写 suite 语义。

- `loom-story`
  - 继续输出 Story Readiness / Business Confirmation locator 或合法 `not_applicable` rationale。
  - 可调用 `loom suite inspect` 读取 path decision，不写 suite。
- `loom-spec-review`
  - 在 formal spec review 前调用 `loom suite validate`。
  - full path 缺 required artifact、provenance 或 mapping 时 fail closed to spec shaping / suite scaffold dry-run。
- `loom-build`
  - 在 build readiness 前消费 `suite validate` 与 `suite carrier validate`。
  - 不把 carrier `done` 当作 evidence present。
- `loom-pre-review`
  - 调用 `suite evidence validate` 与 `suite consistency analyze`，把 blocking gap 挡在正式 review 前。
- `loom-review`
  - 只消费已通过 pre-review 的 suite/evidence/analysis locators，并把 consumed locators 写入单一 review record。
- `loom-merge-ready`
  - 消费 reviewed full suite evidence、fresh verification evidence、PR head / reviewed head / validation freshness 与 gate-chain 结论。
- `loom-handoff` / `loom-resume`
  - 只展示 suite locator、blocking gap 与 next check；不得 authored suite truth。
- `loom-closeout` / `loom-retire`
  - closeout 只校验 suite/evidence/analysis 与 PR head、merge commit、target branch、issue、Project 和 reconciliation audit 可回链；retire 不删除 suite truth。

## 8. Implementation Backlog 建议

后续 CLI implementation 应拆成独立 Work Items，不在 #1052 中实现：

1. `suite inspect` read-only：读取 suite path decision、artifact inventory、core locators 与 host binding。
2. `suite scaffold` dry-run / apply：基于 docs scaffold 生成 suite artifacts，默认 fail closed without `--apply`。
3. `suite validate`：#1120 先校验 full/minimal/not_applicable path 与 core required artifacts；#1121 加深 path decision 合法性、required artifact 普通文件约束与 full path conditional artifact inventory；后续 Work Items 继续加深 `not_applicable` rationale、spec -> plan mapping 与 delivery planning locators。
4. `suite carrier inspect|validate`：读取 execution breakdown / task carrier normalized status 与 truth conflict。
5. `suite evidence inspect|scaffold|validate`：生成并校验 evidence-map locator、row fields、freshness 与 evidence binding。
6. `suite consistency inspect|analyze`：输出 consistency-analysis findings、classification 与 remediation direction。
7. Scenario skill integration：让 `loom-spec-review`、`loom-build`、`loom-pre-review`、`loom-review`、`loom-merge-ready` 消费 suite CLI JSON。
8. Doctor / verify / command-matrix checks：在 declared-support profile 下检查 suite command presence、schema 与 fail-closed behavior。
9. GitHub reconciliation / closeout integration：让 closeout 可消费 suite evidence、merge commit、target branch、issue / Project 状态与 reconciliation audit。

每个 implementation Work Item 都必须保留 #1052 的边界：先读合同、再实现最小命令、最后补充 `tools/check_cli_contract.py` 或等价 surface check；不得把实现回写成新的 docs truth。
