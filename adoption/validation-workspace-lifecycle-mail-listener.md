# Real Adoption Validation: Workspace Lifecycle Compatibility In `mail-listener`

## 1. 样本标识

- 样本仓库：`mail-listener`
- 仓库类型：`复杂既有仓库`
- 仓库位置：`/Users/mc/dev/mail-listener`
- 验证日期：`2026-04-16`
- 对应 Loom issue：`#37`

## 2. 仓库事实

- 已有清晰边界文档：`AGENTS.md`
- 已有最小 checkpoint 规则与单一宿主承接面：`WORKFLOW.md`
- 已有统一验证入口：`ruff format --check .`、`ruff check .`、`pytest`
- 当前仓库依然保留 `checkpoint-lite` 宿主边界，但按当前 `loom-init` heuristics 已不再被视为轻量默认正例

## 3. Loom 判断

- 该样本验证的是 `#37` 的兼容边界，而不是标准恢复正例
- 生命周期入口不能默认要求宿主必须先有独立 worktree 或专门现场目录
- 第一版 `workspace lifecycle` 应允许 `workspace_entry: .` 这类最小语义成立，并把 branch / PR purity 保持为报告项

## 4. 首批装配结果

- Loom 当前的 `workspace create/locate/cleanup/retire` 语义不会强制引入宿主特定现场实现
- `purity-check` 第一版把硬失败收敛在事实链、workspace 匹配和未分流残留，不会误把轻量路径样本直接判成不成立
- 这让 `checkpoint-lite` 路径与后续标准路径保持同一组生命周期命令边界

## 5. 摩擦、失效点与升级信号

- `mail-listener` 证明：
  - 生命周期命令必须兼容最小 `workspace_entry`
  - 不应把复杂仓库的现场治理强度直接提升为所有仓库的默认前提
- 一旦出现以下信号，仍应升级到标准恢复形态：
  - 多轮恢复成本上升
  - Issue / PR 宿主无法继续承接停点和下一步
  - 运行入口、lane 或验证证据开始需要独立读取

## 6. 台账回写结果

- 本次没有新增 `EXT-*`
- 对齐并补强的稳定落点：
  - `EXT-0025`
  - `EXT-0029`
  - `EXT-0033`
- 受影响 Loom 文件：
  - `harness/workspace-lifecycle.md`
  - `tools/loom_flow.py`

## 7. 关闭依据

- `#37` 的实现没有把 `checkpoint-lite` 路径排除在外
- `mail-listener` 为这组生命周期命令补上了“`workspace_entry: .` 与 `checkpoint-lite` 宿主边界”的真实样本
