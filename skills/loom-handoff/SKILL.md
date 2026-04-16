---
name: loom-handoff
description: 负责交接当前事项。Use when Codex needs to prepare a handoff package before ending the current execution round.
---

# Loom Handoff

这个 skill 承接 handoff 场景。

优先入口：

- `python3 tools/loom_flow.py flow handoff --target <repo> [--item <id>]`

输入信号与输出合同见：

- [references/input-signals.md](./references/input-signals.md)
- [references/output-contract.md](./references/output-contract.md)
