---
name: loom-retire
description: 负责清理并退休当前事项现场。Use when Codex needs to clean up Loom-owned residue and retire a workspace without discarding user changes.
---

# Loom Retire

这个 skill 承接 cleanup / retire 场景。

优先入口：

- `python3 tools/loom_flow.py purity-check --target <repo> [--item <id>]`
- `python3 tools/loom_flow.py workspace cleanup --target <repo> --item <id>`
- `python3 tools/loom_flow.py workspace retire --target <repo> --item <id>`

输入信号与输出合同见：

- [references/input-signals.md](./references/input-signals.md)
- [references/output-contract.md](./references/output-contract.md)
