# Real Adoption Validation: Workspace Lifecycle In `hotcp`

## 1. 样本标识

- 样本仓库：`hotcp`
- 仓库类型：`复杂既有仓库`
- 仓库位置：`/Users/mc/dev/hotcp`
- 验证日期：`2026-04-16`
- 对应 Loom issue：`#37`

## 2. 仓库事实

- 仓库已有多应用、多目录职责与本地基础设施
- 运行入口、数据库入口、Extension 入口和浏览器自动化入口并存
- 现行规则入口与历史说明并存，恢复时必须先判定当前应进入哪个执行现场
- 当前仓库的风险不只是“目录很多”，而是现场定位、恢复边界、纯度与环境 lane 都会影响执行正确性

## 3. Loom 判断

- 该样本必须有单现场单事项、可定位恢复入口和可机械执行的 cleanup / retire
- 生命周期入口必须消费事实链中的 `workspace_entry`、`recovery_entry` 和状态面，而不是靠分支名或聊天记忆
- 对该样本而言，`workspace lifecycle` 与 `purity-check` 必须进入默认执行入口，而不是只停留在规则文档

## 4. 首批装配结果

- 稳定合同现在已形成：
  - `harness/workspace-model.md`
  - `harness/workspace-and-purity.md`
  - `harness/workspace-lifecycle.md`
- 机械入口现在已形成：
  - `python3 tools/loom_flow.py workspace create --target <repo> --item <id>`
  - `python3 tools/loom_flow.py workspace locate --target <repo> --item <id>`
  - `python3 tools/loom_flow.py workspace cleanup --target <repo> --item <id>`
  - `python3 tools/loom_flow.py workspace retire --target <repo> --item <id>`
  - `python3 tools/loom_flow.py purity-check --target <repo> [--item <id>]`
- 第一版硬失败口径已固定：
  - 事实链断裂
  - workspace 不匹配
  - 未分流残留
  - 明显的多事项共享现场

## 5. 摩擦、失效点与升级信号

- `hotcp` 证明“只定义单现场单事项规则”不够：
  - 真正高成本的是 locate / cleanup / retire 是否能稳定重复执行
  - 复杂仓库若没有 purity-check，review 前很难机械暴露现场残留
- 本次实现同时保留了边界：
  - 不默认创建宿主特定 worktree
  - 不自动清掉用户改动
  - branch / PR purity 先做报告，不在第一版硬失败

## 6. 台账回写结果

- 本次没有新增 `EXT-*`
- 对齐并补强的稳定落点：
  - `EXT-0025`
  - `EXT-0029`
- 受影响 Loom 文件：
  - `harness/workspace-lifecycle.md`
  - `harness/workspace-model.md`
  - `harness/workspace-and-purity.md`
  - `tools/loom_flow.py`

## 7. 关闭依据

- `#37` 要求的生命周期合同、执行入口、纯度检查与 retire 终态语义都已进入版本控制
- Loom demo 已覆盖 `create -> locate -> cleanup -> retire` 与 purity 负例回归；`hotcp` 补足了复杂仓库为什么需要这套入口的真实样本依据
- 当前仍保留为宿主适配层的部分：
  - 具体 worktree / branch 命名规则
  - PR 平台级 purity 硬门禁
