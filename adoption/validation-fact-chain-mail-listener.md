# Real Adoption Validation: Fact Chain Consumption In `mail-listener`

## 1. 样本标识

- 样本仓库：`mail-listener`
- 仓库类型：`小型既有仓库`
- 仓库位置：`/Users/mc/dev/mail-listener`
- 验证日期：`2026-04-16`
- 对应 Loom issue：`#35`

## 2. 仓库事实

- 已有清晰根级边界文档：`AGENTS.md`
- 已有最小执行入口与三类 checkpoint 合同：`WORKFLOW.md`
- 已有 merge 输入合同：`code_review.md`、`.github/PULL_REQUEST_TEMPLATE.md`
- 已有边界路径准入合同：`spec_review.md`
- 已有统一仓库级验证入口：`ruff format --check .`、`ruff check .`、`pytest`
- 当前 recovery 形态是 `checkpoint-lite`：build checkpoint 明确要求在 issue 或 PR 描述中记录停点、下一步与阻断项

这些事实说明它虽然没有独立 `exec-plan`，但已经具备单一宿主载体承接轻量事实链的前提。

## 3. `loom-init` 判断

- 场景判断：`小型既有仓库`
- 装配强度：`轻量`
- 推荐路径：`lightweight retrofit`
- 恢复形态：`checkpoint-lite`
- 不是 `hotcp`
  - `hotcp` 能证明复杂仓库为什么必须升级到更重事实链，但当前仓库里没有可无猜测消费的单一 `work item + recovery entry` 组合，不适合作为本 issue 的“可直接消费样本”
- 选择 `mail-listener`
  - 因为它已经把 issue / PR 作为单一宿主载体的边界写清，适合验证 Loom 的 `checkpoint-lite` 事实链消费规则

## 4. 事实链映射

本样本把 Loom 事实链消费到以下宿主载体：

- 静态执行真相：关联 issue
  - 目标、范围、路径判断由 `WORKFLOW.md` 约束
  - 边界路径时，`spec.md` / `plan.md` 补充静态边界，但不替代 issue 的执行入口
- 动态执行真相：同一事项选定的 issue 或 PR 描述
  - `WORKFLOW.md` 已明确 build checkpoint 期间由该单一宿主载体记录停点、下一步与阻断项
- 验证入口：仓库级质量门禁
  - `AGENTS.md` 中的 `ruff format --check .`、`ruff check .`、`pytest`
- merge checkpoint 输入：
  - `.github/PULL_REQUEST_TEMPLATE.md`
  - `code_review.md`
  - CI 结果

因此，`mail-listener` 能按 Loom 新合同回答：

- 当前目标和范围从哪里读
  - 关联 issue，必要时补读 `spec.md` / `plan.md`
- 当前 checkpoint、停点、下一步和阻断项从哪里读
  - 单一 issue 或 PR 描述
- merge checkpoint 放行前读什么
  - PR 模板、`code_review.md`、CI

它不需要再额外拼一份并行状态文档。

## 5. 摩擦、失效点与升级信号

当前默认路径成立的证据：

- `WORKFLOW.md` 已把 `checkpoint-lite` 的唯一宿主载体写清
- `code_review.md` 和 PR 模板已经约束 merge 输入
- 仓库有统一验证入口，merge checkpoint 不必靠口头补齐

会触发升级到标准恢复形态的信号：

- issue / PR 之外又出现第二份 authored 停点、下一步或阻断项
- 单一 issue / PR 宿主已无法稳定承接多轮恢复
- 新事项开始引入共享契约、CLI 变化、运行模型变化或更高恢复成本

## 6. 台账回写结果

- 受影响 Loom 核心文档：
  - `harness/fact-chain-contract.md`
  - `harness/recovery-model.md`
  - `harness/status-surface.md`
  - `harness/merge-checkpoint.md`
- 受影响 adoption 文档：
  - `adoption/validation-fact-chain-mail-listener.md`
- 本次验证没有新增 `EXT-*`
  - 它用于证明现有 `checkpoint-lite` 路径可以被新事实链合同直接消费

## 7. 关闭依据

- issue #35 要求的“至少一个真实 adoption 样本验证该事实链可被消费”已满足
- `mail-listener` 证明 Loom 可以在 `checkpoint-lite` 路径下把静态真相、动态真相和 merge 输入收成单一事实链
- `hotcp` 继续保留为复杂路径升级样本，而不是本 issue 的直接消费样本
