# Lane Orchestration

本文件定义 Loom 在高吞吐 milestone / FR 推进中使用的最小 lane orchestration 协议。

它承接 #1544 暴露的并行推进需求，但不把 Loom 扩展成通用调度器、后台队列或第二控制面。
lane 只是主执行线内部的 bounded delegation / bounded write contract。

## 1. 目标

lane orchestration 只解决四件事：

- 让主执行线可以并行发起多个边界清楚的 read-only 或 owned-write lane
- 让每个 lane 在开始前声明稳定的读写边界、验证方式与输出格式
- 保护共享 truth carrier 不被多个 lane 并行写入
- 在结果过期、冲突或重复阻断时，强制回到主执行线做串行整合与 root-cause 判断

它不负责：

- 调度 worker daemon 或后台任务平台
- 替代 GitHub dependency、PR slicing、review、merge-ready 或 closeout gate
- 允许 subagent / lane 直接 author PR body、issue body、`.loom/status/current.md`、
  `.loom/progress/*`、`.loom/reviews/*` 或 `.loom/shadow/*`
- 把 lane 输出提升为新的 authored truth

## 2. 与现有合同的关系

lane orchestration 建立在以下既有合同之上：

- [subagent-driven-execution.md](./subagent-driven-execution.md)
  - 定义 bounded build mode、ownership contract、integration boundary 与 repeated blocker
- [recovery-model.md](./recovery-model.md)
  - 定义 `current_lane` 由恢复主入口 author，其他 lane 只提供待整合 evidence
- [external-orchestrator-interop.md](./external-orchestrator-interop.md)
  - 定义外部 orchestrator 只能通过 recovery writeback 写回进展，不 author status/gate truth
- [fact-chain-contract.md](./fact-chain-contract.md)
  - 定义 authored truth、host mirror、retained result 与 derived surface 的优先级

lane contract 只补足“如何并行推进而不污染 truth carrier”，不重写这些文件的原有职责。

## 3. 最小 Lane Descriptor

每个 lane 在开始前至少要声明一份 machine-readable 或等价结构化 descriptor。

最小字段如下：

- `lane_id`
  - 当前 lane 的稳定标识；同一主执行轮内不得复用到不同范围
- `parent_goal`
  - 当前主线程 `/goal` 或 Work Item goal
- `task_goal`
  - 当前 lane 试图完成的单一子目标
- `context_locators`
  - lane 允许依赖的 issue、文档、代码、日志、fixtures 或 host readback locator
- `read_scope`
  - 允许读取的仓库路径、issue/PR 范围、host surface 或运行时 evidence 范围
- `write_ownership`
  - lane 唯一拥有写权限的文件、目录或 carrier；read-only lane 固定为空数组
- `forbidden_targets`
  - 明确禁止写入的路径、carrier、host object 或动作
- `validation_expectation`
  - lane 完成前必须给出的验证命令、readback 或 evidence 形式
- `output_format`
  - lane 返回摘要和证据的固定结构
- `integration_target`
  - 主执行线将在何处整合 lane 输出，例如 docs、source skills、validation record
- `conflict_policy`
  - ownership overlap、shared carrier write 或并行 drift 时的处理方式
- `stale_result_policy`
  - 结果过期时的判定条件、阻断方式与回退去向

如果 descriptor 缺少 `task_goal`、`read_scope`、`write_ownership`、
`validation_expectation`、`output_format` 或 `stale_result_policy`，主执行线不得把该
lane 当作可整合输入。

## 4. Lane 类型

Loom 当前只承认三类 lane：

1. `read_only`
   - 可并行读取 docs、代码、issue tree、logs、fixtures 或 host readback
   - 不写 repo、carrier 或 host object
2. `owned_write`
   - 只写 `write_ownership` 声明的不重叠路径
   - 允许在独立 worktree 中产出局部实现或 docs 修改
3. `shared_carrier_serial`
   - 只能由主执行线持有
   - 负责把已整合结论串行写回共享 truth carrier 或 host machine carrier

Loom 不承认“并行共享 carrier 写 lane”。凡是涉及共享 truth carrier 的写入，必须升级为
主执行线的串行整合动作。

## 5. 共享 Truth Carrier 串行写规则

以下对象一律视为 shared truth carrier 或 shared machine carrier：

- PR body machine carrier
- issue body / closeout comment machine carrier
- `.loom/status/current.md`
- `.loom/progress/*`
- `.loom/reviews/*`
- `.loom/shadow/*`
- recovery 主入口与其 authored 动态字段

规则固定如下：

- lane 可以读取这些 carrier，但不得并行 author
- 多个 lane 可以分别产出建议、diff、验证证据或 locator
- 只有主执行线可以在 readback 后决定是否写回这些 carrier
- 写回必须串行发生，并绑定当前 Work Item、branch、workspace、PR 与 `head_sha`
- 共享 carrier 写回前，主执行线必须重新检查相关 readback 是否仍 fresh

若 lane 试图直接写这些 carrier，必须视为 ownership violation，并阻断本轮整合。

## 6. 结果输出与回收

每个 lane 返回的最小摘要固定包含：

- `task_goal`
- `locators`
- `changes`
- `validation`
- `remaining_risks`
- `boundary_touched`
- `stale_basis`

其中：

- `changes`
  - 只说明改了什么、为什么，不回传整段长日志
- `validation`
  - 至少给出命令、结果与必要 evidence locator
- `boundary_touched`
  - 明确说明是否触碰共享 carrier、host object 或禁改范围
- `stale_basis`
  - 说明该结果绑定的 branch、`head_sha`、carrier readback 或 schema/version 前提

主执行线回收 lane 输出时，必须做三件事：

- 判断输出是否仍绑定当前主线上下文
- 把可接受内容整合进实现、验证证据或后续 review 输入
- 把冲突、过期或 repeated blocker 升级为主线判断，而不是静默忽略

未整合的 lane / subagent 输出只能停留在 evidence 层，不能单独构成 completed truth。

## 7. Stale Result 判定

lane 输出满足以下任一条件时，必须视为 `stale`：

- lane 基于的 branch 已 behind 当前主执行线或目标 branch 绑定
- lane 基于的 `head_sha` 已变化
- PR body readback 或 machine block fingerprint 已变化
- 主执行线依赖的 classifier、字段名或 machine carrier schema 已变化
- lane 读取的共享 carrier hash、locator 或 freshness 已变化
- lane 依赖的 review / validation / runtime evidence 已不再绑定当前范围

`stale` 的固定处理为：

- 不直接复用旧结果写回 shared truth carrier
- 主执行线标记该 lane 输出为 `stale` 或 `needs-rerun`
- 若只是 read-only 结论失效，可重新读取并生成新摘要
- 若 stale 暴露根因是 shared contract 漂移、ownership 设计错误或重复阻断，必须回到主执行线做 root-cause escalation

## 8. 冲突处理

以下情况必须 fail closed：

- 两个 active lane 的 `write_ownership` 重叠
- read-only lane 混入未声明的写入
- owned-write lane 试图 author shared truth carrier
- 主执行线尚未整合旧 lane 输出时，又基于同一范围启动第二个写 lane
- 多个 lane 重复报告同一 blocker signature，但主执行线没有做 root-cause 判断

冲突发生时，允许的回退只有：

- `build`
- `admission`
- `binding_repair`
- `root_cause_escalation`

不得回退到私有 scheduler state、隐式 retry queue 或未声明的 host action。

## 9. 最小示例

### 9.1 并行 read-only lanes

- lane A：读取 milestone 相关 issue tree，输出依赖图与 stale 风险
- lane B：读取 `docs/methodology/harness`，输出现有协议落点与缺口
- 两者都不写 carrier，可并行执行

### 9.2 非重叠 owned-write lanes

- lane C：只写 `docs/methodology/harness/lane-orchestration.md`
- lane D：只写 `src/skills/shared/references/harness/lane-orchestration.md`
- 若主执行线确认两者不冲突，可并行或近并行推进

### 9.3 shared carrier 串行写

- lane E 输出 PR slicing 建议
- lane F 输出 review metadata 建议
- 主执行线整合 E/F 结论后，单独完成 PR body readback 与串行写回

## 10. 对 skill 的影响面

当前最小影响面如下：

- `loom-build`
  - 消费 lane descriptor、ownership conflict、integration evidence 与 repeated blocker
- `loom-resume`
  - 只恢复主执行线当前 `current_lane`，不把 lane 输出当成第二恢复入口
- `loom-handoff`
  - 只输出主执行线需要回写的 handoff 清单，不 author lane-local truth
- `loom-merge-ready`
  - 只消费已整合进主线 carriers 的结果；未整合或 stale 的 lane 输出不得作为放行依据

后续若需要更强约束，应通过 CLI JSON、carrier contract 或 fixture 回归继续收敛，而不是先扩展为队列系统。
