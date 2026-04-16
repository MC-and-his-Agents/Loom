---
name: loom-pre-review
description: 负责统一 review 前检查。Use when Codex needs a single pre-review gate before entering semantic review.
---

# Loom Pre Review

这个 skill 包裹统一的 review 前 flow。

优先入口：

- `python3 tools/loom_flow.py flow pre-review --target <repo> [--item <id>]`

输入信号与输出合同见：

- [references/input-signals.md](./references/input-signals.md)
- [references/output-contract.md](./references/output-contract.md)
