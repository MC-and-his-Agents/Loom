# Status Surface Contract

本文件冻结 Loom 当前统一治理状态读取面的最小合同。

它回答的不是“状态写在哪”，而是“哪些状态必须能被同一个读面稳定读出”。

## 1. 目标

统一状态面至少要同时服务：

- `loom-resume`
- `loom-spec-review`
- `loom-review`
- `loom-merge-ready`
- repo-local `loom_status`
- host-backed GitHub 状态消费

它不新增 authored 真相，只收口已有真相的读取语义。

## 2. 最小读取对象

统一状态面至少必须能读出：

- 当前 `Work Item`
- 当前 checkpoint
- 当前 recovery 状态
- `spec review` 结果
- implementation review 结果
- `merge-ready` 结果
- 最小 `item context`
- 宿主控制面信号

其中：

- `Work Item`、recovery、checkpoint 来自事实链
- `spec review`、implementation review 来自 review records
- `merge-ready` 来自 merge checkpoint
- `item context` 来自 [item-context-contract.md](./item-context-contract.md)
- 宿主控制面信号来自 Git / GitHub 或等价 host adapter

## 3. 最小字段组

统一状态面至少要能稳定暴露以下字段组：

- `item`
  - `id`
  - `goal`
  - `scope`
  - `execution_path`
  - `workspace_entry`
  - `recovery_entry`
  - `review_entry`
  - `validation_entry`
- `current_checkpoint`
  - `raw`
  - `normalized`
- `recovery`
  - `current_stop`
  - `next_step`
  - `blockers`
  - `latest_validation_summary`
  - `recovery_boundary`
  - `current_lane`
- `spec_review`
- `review`
- `merge_ready`
- `governance_surface`
- `github`

## 4. 结果语义

统一状态面本身只允许输出两类总结果：

- `pass`
- `block`

判定原则：

- 所有关键读取都成功，且没有缺失前序 gate，结果才是 `pass`
- 只要存在缺失输入、前序 gate 未满足、`head_sha` 漂移或宿主信号缺失，结果就是 `block`

统一状态面不负责把 `block` 细分成新状态机；它只负责把阻断原因暴露给上游 skill 和 gate。

## 5. 消费边界

### 5.1 `loom-resume`

消费：

- 当前 `Work Item`
- recovery 字段
- 当前 checkpoint
- `governance_surface`

### 5.2 `loom-spec-review`

消费：

- 当前 `Work Item`
- formal spec 路径
- `item context`
- `spec_review` gate

### 5.3 `loom-review`

消费：

- `spec_review` 是否已通过
- implementation review 是否 stale
- `head_sha` 是否仍绑定当前实现

### 5.4 `loom-merge-ready`

消费：

- `spec_review`
- implementation review
- merge checkpoint
- 宿主控制面中的 PR / head / merge gate 信号

## 6. repo-local 与 host-backed 边界

- repo-local 路径可以只依赖 `.loom/` 事实链与本地 git
- host-backed 路径可以额外消费 issue / PR / branch protection / required checks
- 两条路径必须收敛到同一状态语义，而不是生成两套 status 格式

## 7. 当前最小实现

当前仓库中的统一读取入口为：

- `python3 tools/loom_status.py --target <repo> [--item <id>]`

安装态等价入口为：

- `python3 shared/scripts/loom_status.py --target <repo> [--item <id>]`

## 8. 非目标

- 不把状态面升级成第二套 authored 账本
- 不在不同 skill 中各自发明不同 JSON 结构
- 不把 GitHub 私有字段直接冻结成 Loom core 唯一词汇
