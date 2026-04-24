# Maturity And Closing

本文件定义 Loom 的成熟度与关闭语义之间的关系。

治理档位定义见 [governance-maturity-model.md](./governance-maturity-model.md)。
稳定状态名与转移规则见 [state-machine.md](./state-machine.md)。

## 1. 文档定位

本文件只回答：

- 治理档位与事项成熟度状态如何协同
- 为什么关闭语义必须服从成熟度与 gate 链
- 哪些常见 shortcut 必须禁止

## 2. 成熟度先于关闭

关闭语义必须与事项成熟度一致，不得提前制造“已完成”状态。

默认顺序仍然是：

- 说明清楚
- 进入实现
- 达到 `merge_ready`
- 完成 `controlled merge`
- 完成 `closeout`

## 3. strong governance 的额外要求

在 `strong` 档位下，关闭前至少还要满足：

- `Work Item` 是合法执行入口
- formal spec 路径已完成 `spec review`
- implementation review 与 `merge-ready` 已消费前序 gate
- `controlled merge` 已完成 host control 验证
- `reconciliation audit` 未留下阻断 drift

## 4. 关闭一致性条件

只有 `closed_out` 才表示事项可以关闭。

以下结论都不等于完成：

- `spec review` 通过
- implementation review 通过
- `merge-ready` 通过
- PR 已 merged
- 实现已被 `absorbed`

## 5. 关闭反模式

禁止以下 shortcut：

- 用 PR 已 merged 代替 `closed_out`
- 用 parent 已 closeout 自动替代 child closeout
- 用局部文档补写代替缺失的 gate basis
- 用口头说明覆盖状态面缺口

## 6. 一句话结论

成熟度模型决定仓库具备多强的治理能力；状态机决定事项当前走到哪里；`closed_out` 只能发生在两者都成立时。
