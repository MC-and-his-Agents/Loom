# Loom Merge Ready Output Contract

输出固定为 merge-ready 摘要 JSON，至少需要给出：

- `item`
  - 当前事项编号、目标、范围、执行路径
- `result`
  - `pass`、`block` 或 `fallback`
- `summary`
  - 对 merge 前统一放行状态的单句结论
- `missing_inputs`
  - 当前仍阻断放行的缺口列表
- `fallback_to`
  - 若当前必须回退，应回退到的 checkpoint；无回退时为 `null`
- `state_check`
  - `state-check` 的结果、摘要、阻断项与检查分项
- `runtime_evidence`
  - 5 项运行时证据对象，保留 `present` 与 `not_applicable`
- `build_checkpoint`
  - `checkpoint build` 的结果、摘要、阻断项与回退去向
- `merge_checkpoint`
  - `checkpoint merge` 的结果、摘要、阻断项、回退去向，以及可读的 PR 模板检查结果
- `current_checkpoint`
  - 当前 recovery checkpoint 的原始值与归一化值
- `current_lane`
  - 当前 lane 定位
- `latest_validation_summary`
  - 最近可用验证摘要
- `steps`
  - 固定按 `fact-chain -> state-check -> runtime-evidence -> checkpoint-build -> checkpoint-merge` 顺序列出

这个 skill 只给出 merge 前统一放行摘要，不替代宿主平台 merge，也不直接执行平台动作。
