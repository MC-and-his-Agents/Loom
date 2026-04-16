# Loom Resume Output Contract

输出固定为恢复摘要 JSON，至少需要给出：

- `item`
  - 当前事项编号、目标、范围、执行路径
- `result`
  - `pass` 或 `block`
- `summary`
  - 对当前恢复状态的单句结论
- `missing_inputs`
  - 当前阻断所需补齐的信息；无阻断时为空数组
- `fallback_to`
  - 若当前不能继续执行，应回退到哪个 checkpoint；无回退时为 `null`
- `workspace`
  - `workspace_entry`、解析后的现场路径、现场是否存在
- `recovery`
  - 恢复入口、当前停点、下一步、阻断项、最近验证摘要
- `checkpoint`
  - 原始 checkpoint 文本与归一化后的 checkpoint
- `state_check`
  - `state-check` 的结果、摘要、阻断项与检查分项
- `steps`
  - 固定按 `fact-chain -> state-check -> workspace-locate` 顺序列出

这个 skill 不回写任何载体；如果恢复链路不可继续，只返回阻断或回退语义。
