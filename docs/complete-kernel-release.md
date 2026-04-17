# Complete Kernel Release (2026-04-16)

本文是 Loom 完整执行内核与第一波场景 SKILLS 的上游发布与升级说明。

对应 Loom issue：`#63`、`#71`

## 1. 已发布的稳定能力面

本次发布将以下能力收敛为稳定交付面：

- 单一事实链读取与一致性校验
  - `loom_init fact-chain`
  - `loom_flow fact-chain`
- root + 场景 SKILLS 入口层
  - root entry：`loom-init`
  - 场景 skills：`loom-adopt`、`loom-resume`、`loom-pre-review`、`loom-review`、`loom-handoff`、`loom-retire`、`loom-merge-ready`
  - 路由与升级工件：`skills/registry.json`、`skills/upgrade-contract.json`、`skills/route-matrix.md`
- 三类 checkpoint 工程化入口
  - `loom_flow checkpoint admission|build|merge`
- workspace 生命周期与纯度治理入口
  - `loom_flow workspace create|locate|cleanup|retire`
  - `loom_flow purity-check`
  - `loom_flow host-lifecycle`
- 运行时证据入口与语义校验
  - `loom_flow runtime-evidence`
- 活跃状态/完整性检查与高频统一入口
  - `loom_flow state-check`
  - `loom_flow flow pre-review`
  - `loom_flow flow review`
  - `loom_flow review read|record`
  - `loom_flow flow resume`
  - `loom_flow flow handoff`
  - `loom_flow flow merge-ready`
  - `loom_flow recovery writeback`
  - `loom_flow work-item create|update`
- gate 入口
  - `loom_check`
  - `loom_init verify`
  - `loom_flow closeout check|sync`

## 2. 下游升级路径

### 2.1 新项目

1. `loom_init bootstrap --write --verify`
2. 让 root entry 或显式 skill 调用把执行者路由到正确场景
3. 使用 `fact-chain/state-check/flow resume|pre-review|review|merge-ready` 建立日常读取、恢复、正式审查与 merge 前放行
4. 按 checkpoint 链路推进（admission -> build -> merge）

### 2.2 既有仓库（轻量到完整）

1. 先接入 `bootstrap + verify + fact-chain`
2. 接入 `checkpoint` 与 `workspace` 入口
3. 接入 `runtime-evidence`、`state-check` 与 4 个聚合 flow：`resume` / `handoff` / `review` / `merge-ready`
4. 在 review 前统一走 `flow pre-review`，正式审查使用 `flow review` + `review record`
5. 让宿主刷新 `skills/registry.json`、`skills/upgrade-contract.json`、skill manifests 与引用资源

### 2.3 兼容原则

- 新增入口不替代旧入口语义
- 单命令入口与聚合入口并存
- gate 与 verify 复用同一入口，不维护第二套检查命令

详见：[adoption/execution-entry-compatibility.md](../adoption/execution-entry-compatibility.md)

## 3. 复验覆盖

本次发布前已完成以下复验并回写到版本控制：

- 6 个场景 skill 的显式触发、隐式路由与下游消费验证
- 事实链复验：`mail-listener`
- checkpoint 复验：`hotcp`
- 运行时证据复验：`hotcp`
- automation-frontload 复验：`hotcp`
- 新项目完整内核复验：`loom-adoption-new-project`
- 既有仓库完整内核复验：`mail-listener` + `hotcp`

验证记录位于 `adoption/validation-*.md`。

## 4. 发布后操作建议

- 下游仓库先执行 `verify`，再通过 root route 或显式 skill 调用进入对应场景
- 日常恢复优先走 `flow resume`，交接优先走 `flow handoff`，merge 前统一走 `flow merge-ready`
- review 前仍先执行 `flow pre-review`，正式审查改为 `flow review` + `review record`
- 如遇 `state-check` 或 `checkpoint` 阻断，先回退补齐事实链/范围/证据，不要绕过入口
- 仅在宿主适配层补平台细节，避免反向污染 Loom 内核合同

## 5. 第一波场景 SKILLS 收口依据

`#71` 的 Done When 现已由以下仓库真相共同覆盖：

- 7 个场景 skills 均已注册、可发现、可显式调用
  - 以 `skills/registry.json`、各 skill `contract.json` 与 `skills/route-matrix.md` 为准
- `loom-init` 可按任务信号隐式导向这 7 个场景
  - 以 `loom_init route`、`skills/route-matrix.md` 与 `loom_check` 路由校验为准
- CLI / gate / docs / validation / GitHub 状态一致
  - CLI：`loom_flow flow resume|pre-review|review|handoff|merge-ready`
  - gate：`loom_check`
  - docs：`skills/README.md`、`adoption/execution-entry-compatibility.md`、`adoption/versioning-and-upgrades.md`
  - validation：`adoption/validation-skill-*.md`
  - GitHub：父子 issue 树与对应 PR 已收口到主干

## 5. 第一波场景 SKILLS 收口状态

本次发布已完成以下收口条件：

- `loom-init` 继续作为唯一 root entry，7 个场景 skill 均已注册、可发现、可显式调用
- `loom-init route`、`flow resume`、`flow review`、`flow handoff`、`flow merge-ready` 已与既有入口一起纳入 `loom_check`
- 7 个场景 skill 的验证记录、升级说明、交付面说明与发布说明已全部回写到版本控制
- GitHub issue / sub-issue、CLI、gate、文档与 adoption 记录已对齐到同一条仓库真相

对应总父 issue：`#71`
