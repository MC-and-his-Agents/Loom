# Upstream Delivery Surface

本文定义 Loom 作为上游系统时，对下游稳定暴露的交付面。

它的目标不是描述某个宿主如何发行，而是明确：哪些内容已经形成 Loom 的稳定发布面，哪些内容仍然属于候选或宿主特定实现。

## 1. 稳定交付面

当前稳定交付面包括：

- `governance/`
  - 核心原则、审查模型、成熟度与关闭语义
- `harness/`
  - 核心执行合同、恢复模型、状态面、纯度、[宿主动作主合同](../harness/host-action-contract.md)、宿主生命周期边界、closeout gate、reconciliation sync 写回约束与自动化前置
- `templates/`
  - 最小正式规约模板与最小 PR 模板
- `skills/`
  - 稳定入口合同、`loom-init` root 路由、7 个场景 skills、`registry.json`、`upgrade-contract.json` 与 `route-matrix.md`
- `adoption/`
  - 稳定 adoption 路径、经验回流、验证记录合同、版本化与升级路径
  - `repo companion migration` 稳定下游合同
  - 执行入口兼容说明、reconciliation audit/sync 兼容边界、7 个场景 skill 验证记录与完整执行内核复验记录
  - 第一批执行化补充验证记录：
    - `adoption/validation-main-path-new-project.md`
    - `adoption/validation-existing-repo-execution-sync.md`
  - companion 合同参考与验证记录：
    - `adoption/repo-companion-migration.md`
    - `adoption/reference-companion-spec-syvert.md`
    - `adoption/reference-companion-spec-webenvoy.md`
    - `adoption/validation-repo-companion-interface.md`
  - Loom 自身 `#143` 树 retrofit 记录：
    - `adoption/validation-retrofit-143-tree.md`
    - 只作为 Loom 自身 closeout / retrofit 依据，不单独提升为新的默认 adoption 路径
- 发布说明
  - `docs/complete-kernel-release.md`
  - 当前正式产品版本：`v0.2.0`

这些内容共同形成 Loom 的最小上游发布面。

## 2. 候选交付面

以下内容当前不属于稳定发布面：

- `adoption/candidate-patterns.md`
- 单靠 `adoption/validation-retrofit-143-tree.md` 推出的新 adoption 默认路径
- 宿主特定 adapter 实现
- 宿主完整回归矩阵
- 未升为 `keep` 的 `EXT-*` 结论
- 只在单一宿主或单一仓库成立的安装 / 发布细节

这些内容可以被 Loom 承认，但不应被伪装成默认必须消费的上游接口。

## 3. 交付对象

Loom 对下游交付的对象不是单个文件，而是以下组合：

- 一组稳定规则真相
- 一组最小模板
- 一组可升级的入口合同与 root/scene 路由入口
- 一组 adoption / upgrade 说明
- 一组下游 `repo companion migration` 机读合同（`.loom/companion/manifest.json` 与 `.loom/companion/repo-interface.json`）

下游不应被要求复制候选材料，才能消费 Loom 的核心能力。

## 4. 交付边界约束

- 宿主实现细节不进入稳定交付面
- 单仓验证不足的结论不进入稳定交付面
- 根入口摘要不重复内核正文；内核正文只保留在唯一主落点
- 任何想进入稳定交付面的内容，都必须能映射到 `landing-map.md`

## 5. 反例

以下不是稳定交付面：

- 某个宿主的 marketplace 发布流程
- 某个宿主的安装路径
- 某个仓库的本地 CI 脚本
- 一条尚未脱离单仓样本的候选方法论

这些对象可以存在，但只能作为宿主实现或候选材料，不应被下游当作 Loom 默认契约。
