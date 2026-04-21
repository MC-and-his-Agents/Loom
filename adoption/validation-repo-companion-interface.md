# Validation: Repo Companion Interface

本文记录 `repo companion interface` 的最小验证口径。

它覆盖的不是下游仓库实时运行状态，而是 Loom 当前冻结的机读接口能否稳定区分 4 类读面，以及 companion requirements / gates 是否按既定纪律被消费。

## 1. 覆盖面

本批验证至少覆盖以下 8 种情况：

- absent companion
- companion docs only
- incomplete manifest / repo-interface
- present `v1` manifest + interface
- present `v2` manifest + interface
- present manifest + blocking review requirements
- present manifest + advisory merge-ready requirements
- present manifest + blocking closeout requirements

## 2. 判定口径

| 覆盖项 | 判定条件 | 预期结果 |
| --- | --- | --- |
| absent companion | 仓库不存在 `.loom/companion/manifest.json` | `governance_surface.repo_interface.availability = absent` |
| companion docs only | 仓库存在旧式 companion docs，但无 manifest | `availability = companion_docs_only` |
| incomplete | manifest 存在但 locator / schema / surface 缺失，或 manifest 带入 authored 字段 | `availability = incomplete` |
| present `v1` | manifest 与 `repo-interface v1` 完整 | `availability = present`，`loom_flow` 继续可消费 requirements |
| present `v2` | manifest 与 `repo-interface v2` 完整，且 typed gates / metadata / context 均合法 | `availability = present`，`v1`/`v2` 不分叉执行结果语义 |
| present + review | manifest 与 repo-interface 完整，且 `review` surface 含 blocking requirement | `flow review` 必须显式 `block` |
| present + merge-ready | manifest 与 repo-interface 完整，且 `merge_ready` surface 只含 advisory requirement | `repo_specific_requirements.result = pass`，不新增顶层阻断 |
| present + closeout | manifest 与 repo-interface 完整，且 `closeout` surface 含 blocking requirement | `repo_specific_requirements.result = block`，closeout 不得宣称 Loom core 已覆盖 |

## 3. 负样本纪律

以下情况必须保持 `incomplete` 或直接 `block`：

- manifest 出现 `current_stop`、`blockers`、`review summary` 等 authored 字段
- `repo-interface.json` 缺少 `review`、`merge_ready`、`closeout` 任一 surface
- requirement 使用非法 `enforcement`
- specialized gate 使用非法 `gate_type`
- `metadata_contract` 缺少 `applicability_locator`、`authority_locator` 或使用非法 `enforcement`
- `context_schema` 缺少 `type`、`required`、`mapping_rule_locator` 或使用非法基础类型
- locator 指向不存在的文件
- 旧式 companion docs 被伪装成 `present`

## 4. 当前落点

本批 companion interface 的验证由以下入口共同承接：

- `loom_check`
  - synthetic fixtures 同时覆盖 `v1`、`v2`、非法 `v2` 输入、4 类 availability 与 3 个 surface 的结果纪律
- `governance_surface`
  - 负责 companion 机读读面
- `loom_flow review|merge-ready|closeout`
  - 负责 companion-declared repo-specific requirements 的消费结果

## 5. 参考样本

接口样本见：

- [reference-companion-spec-syvert.md](/Users/mc/dev/Loom/adoption/reference-companion-spec-syvert.md)
- [reference-companion-spec-webenvoy.md](/Users/mc/dev/Loom/adoption/reference-companion-spec-webenvoy.md)

它们只证明当前接口足以承接两类真实下游，不宣称这些仓库的 repo-specific 规则已被提升为 Loom core 默认规则。
