---
name: loom-resume
description: 负责恢复当前事项的执行入口。Use when Codex needs to take over an active Loom item, rebuild context, and continue from the current checkpoint.
---

# Loom Resume

这个 skill 承接恢复上下文、接手当前事项与继续推进。

它依赖统一恢复摘要入口：

- `python3 tools/loom_flow.py flow resume --target <repo> [--item <id>]`

输入信号与输出合同见：

- [references/input-signals.md](./references/input-signals.md)
- [references/output-contract.md](./references/output-contract.md)
