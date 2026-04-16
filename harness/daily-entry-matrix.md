# Daily Entry Matrix

本文件定义 Loom 日常高频动作的统一入口矩阵与职责边界。

它只回答三件事：

- 哪个动作由 `skills`、CLI、gate 哪一层承接
- 每个入口读取哪类输入
- 哪些动作属于“执行入口”，哪些属于“放行入口”

## 1. 入口矩阵

| 动作 | 首选入口 | 读取基线 | 结果形态 | 备注 |
| --- | --- | --- | --- | --- |
| `bootstrap` | `python3 tools/loom_init.py bootstrap --target <repo>` | intake + 仓库信号 | 初始化结果 JSON + 首批工件 | `skills/loom-init` 负责路由，CLI 负责落盘 |
| `verify` | `python3 tools/loom_init.py verify --target <repo>` | init-result + fact-chain + flow 子命令 | `ok` / `errors` | 核验初始化产物与入口可读性 |
| `fact-chain` | `python3 tools/loom_flow.py fact-chain --target <repo> [--item <id>]` | 单一事实链 | `pass` / `block` | 日常统一读取入口 |
| `pre-review`（统一高频入口） | `python3 tools/loom_flow.py flow pre-review --target <repo> [--item <id>]` | fact-chain + state-check + runtime evidence + admission + workspace locate | `pass` / `block` / `fallback` | 第一版聚焦 review 前高频检查流 |
| `checkpoint` | `python3 tools/loom_flow.py checkpoint <admission\\|build\\|merge> --target <repo> [--item <id>]` | fact-chain + purity + merge 放行材料 | `pass` / `block` / `fallback` | `merge` 可额外消费 PR 模板 |
| `resume` | 恢复主入口 + execution-context 读取顺序 | work item + recovery entry + status-surface | 可继续执行的下一步上下文 | 语义落点在 `recovery-model.md` |
| `handoff` | 恢复主入口回写 + 状态面同步 | 当前停点/下一步/阻断项/验证摘要 | 可移交的恢复状态 | 不新增第二套 authored 状态 |
| `review` | `spec_review` / `code_review` + merge checkpoint 输入 | 最小必要上下文 + 前置检查结果 | `allow` / `block` / `fallback` | reviewer 负责语义判断，脚本负责机械判断 |
| `merge` | `merge checkpoint` + 仓库平台合并动作 | build 结果 + 风险回滚 + 验证摘要 | 放行或阻断 | Loom 不替代宿主平台合并接口 |
| `retire` | `python3 tools/loom_flow.py workspace retire --target <repo> --item <id>` | cleanup 结果 + recovery 主入口 | checkpoint 终态 `retired` | 不默认删除现场目录 |

## 2. 分层边界

- `skills`
  - 负责“把执行者导向正确入口”
  - 不承接 authored 执行真相
- CLI
  - 负责读取、校验、回写与输出稳定 JSON 语义
  - 不替代 reviewer 的语义判断
- gate (`loom_check` / CI)
  - 负责复用同一 CLI 入口做机械阻断
  - 不维护第二套检查口径

## 3. 非目标

- 不把宿主特定 UI/按钮/平台命令写成 Loom 内核默认入口
- 不把 `review` 结论伪装成脚本可自动生成的语义判断
- 不把 `resume`/`handoff` 另写为并行真相文件
