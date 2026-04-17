# Output Contract

使用本文件约束 `loom-init` 的输出。

输出目标不是给出泛建议，而是形成可继续执行的初始化产物模型。

## 必须输出的区块

### 1. 项目判断

必须说明：

- 初始化场景：
  - `新项目`
  - `小型既有仓库`
  - `复杂既有仓库`
- 装配强度：
  - `轻量`
  - `标准`
  - `强化`
- 当前最主要的结构性问题是什么
- 为什么推荐这条路径，而不是另外两条路径

### 2. 推荐装配

至少列出：

- 本轮启用的能力清单
- 每项能力分别映射到哪些 `governance`、`harness`、`templates`、`adoption` 规则
- 这次采用的是最小装配、轻量 retrofit 还是更完整装配
- 接入方式是根级重写还是 `companion docs`
- 恢复形态是 `checkpoint-lite` 还是标准恢复形态

### 3. 暂不引入

必须显式写出：

- 当前不引入哪些 Loom 能力
- 不引入的原因是什么
- 这些能力未来的升级触发条件是什么

### 4. 首批工件

至少说明：

- 初始能力清单的承载位置
- 首批 work item 或等价事项清单的承载位置
- 恢复主入口是什么
- progress / checkpoint 载体是什么
- 验证入口是什么
- 状态读取入口是什么
- `Runtime Evidence` 区块的落位方式是什么，且至少覆盖：
  - `Run Entry`
  - `Logs Entry`
  - `Diagnostics Entry`
  - `Verification Entry`
  - `Lane Entry`
- 初始 clean state 的定义是什么
- 首个稳定提交或等价回退边界是什么
- 事实链 carrier 如何定位
- 统一事实链读取入口是什么
- `governance_surface` 是什么，并至少稳定给出：
  - `repository_mode`
  - `loom_state`
  - `carrier_summary`
    - `work_item`
    - `recovery`
    - `review`
    - `status_surface`
    - `spec_path`
    - `plan_path`
  - `execution_entry`
  - `validation_entry`
  - `review_merge_surface`
    - `pr_template`
    - `validation_surface`
    - `merge_surface`
  - `github_control_plane`
    - `repository`
    - `default_branch`
    - `branch_protection`
    - `required_checks`
    - `pr_reviews`
  - `summary`
  - `missing_inputs`

若本轮不装配标准恢复或状态面，也必须写清现有载体如何承接这些职责。

`init-result` 只允许承接 locator-only 信息，不并行复制实时停点、下一步、阻断项或最近验证摘要。

`Runtime Evidence` 的五个字段必须逐项给出 locator 或 `not_applicable`，不得留空；若使用 `not_applicable`，必须给出可复核原因。

### 5. 首批事项

至少拆出：

- 每个事项的：
  - 事项标识
  - 目标
  - 范围
  - 执行路径
  - 关联工件
  - 关闭条件
- 恢复主入口与工作现场入口
- 若事项已进入轻量跨轮承接，必须说明谁负责回写停点、下一步、阻断项与最近验证摘要

## `governance_surface` 的公共约束

`governance_surface` 是 `loom-init`、`loom-adopt` 与 `loom-resume` 共享的稳定公共读面。

它只回答“当前仓库属于哪种执行模式、Loom 装配到什么程度、治理载体和宿主控制面分别位于哪里”，不复制实时 authored 状态。

固定要求：

- 字段命名保持 `governance_surface`
- 字段命名保持：
  - `repository_mode`
  - `loom_state`
  - `carrier_summary`
  - `execution_entry`
  - `validation_entry`
  - `review_merge_surface`
  - `github_control_plane`
  - `summary`
  - `missing_inputs`
- `carrier_summary` 的 6 个子项固定为：
  - `work_item`
  - `recovery`
  - `review`
  - `status_surface`
  - `spec_path`
  - `plan_path`
- `carrier_summary` 每个子项固定为 `{status, locator, source}`，`status` 只允许 `present | missing | planned`
- `github_control_plane` 缺失时允许用 `unknown`，但不得猜测

禁止事项：

- 把 `governance_surface` 写成第二套事项进度真相
- 改名或拆出并行的治理读面字段
- 在 `governance_surface` 中并行复制实时停点、下一步、阻断项或验证摘要
- 用 `governance_surface` 覆盖 `work item`、恢复入口、PR 或规则文档的 authored 事实

### 6. 验证与收口

至少说明：

- 如何验证初始化输出已经可直接承接执行
- 三个 checkpoint 的承接关系是什么（固定命名为 `admission -> build -> merge`，不再使用 `commit checkpoint` 命名）
- 什么状态算“说明已清楚”
- 什么状态算“已进入主干并收口”
- 何时 issue 可以关闭

## 初始化产物模型的最低要求

无论场景轻重，初始化输出都必须让后续执行者能直接回答以下问题：

- 当前属于哪条初始化路径
- 当前启用了哪些能力，暂不启用哪些能力
- 首批执行从哪里进入
- 恢复主入口在哪里
- 验证入口在哪里
- 当前 clean state 如何识别
- 首个稳定提交或等价回退边界如何识别
- 相关信息分别落在哪个载体上

若这些问题仍需要靠临场解释补齐，说明输出合同未达标。
