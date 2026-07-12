# Loom Merge Ready Input Signals

当任务满足以下任一信号时，进入 `loom-merge-ready`：

- merge-ready
- 最终放行前预检
- 确认当前事项是否可合并
- 确认 `GitHub controlled merge` 前置是否齐全

最小输入：

- 目标仓库
- GitHub Work Item、PR 与 host artifact locator
- suite path decision：full path 的 reviewed suite/evidence/consistency locators，或
  minimal path 的 `not_applicable` rationale、consumer boundary、recheck condition
- PR locator；current head 与 reviewed head 必须由 GitHub host readback
