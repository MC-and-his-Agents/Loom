---
name: loom-merge-ready
description: 负责 merge 前统一放行。Use when Codex needs to confirm whether the current item is ready for merge without replacing the host platform merge action.
---

# Loom Merge Ready

这个 skill 承接 merge-ready 场景。

优先入口：

- `python3 tools/loom_flow.py flow merge-ready --target <repo> [--item <id>]`

输入信号与输出合同见：

- [references/input-signals.md](./references/input-signals.md)
- [references/output-contract.md](./references/output-contract.md)
