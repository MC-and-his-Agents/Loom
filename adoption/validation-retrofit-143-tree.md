# Real Adoption Validation: Live Retrofit Of The `#143` Tree

## 1. 样本标识

- 验证对象：Loom 仓库当前真实 `#143` 父树
- 目标仓库：`/Users/mc/dev/Loom`
- 父 issue：`#143`
- 直接子 issue：
  - `#145`
  - `#146`
  - `#148`
  - `#150`
- 本次重点 retrofit 节点：
  - `#162`
  - `#178`
  - `#179`
- 对应 Loom issue：`#180`
- 验证日期：`2026-04-18`

## 2. 本次 retrofit 的固定边界

`#180` 只消费已经冻结的 issue / closeout / reconciliation 合同，对 Loom 自身当前真实树做 live 对账。

本次不做以下事情：

- 不新增新的对象模型
- 不改写 `absorbed`、`closed_out`、`parent issue` 的定义
- 不把本次 retrofit 直接扩写成 adoption / 发布面总回写

因此，本记录只承接三件事：

1. 读取 `#143` 树当前 issue / PR / Project 真相
2. 对存在 drift 的节点执行正式 `reconciliation`
3. 把“哪些节点已完成收口、哪些节点仍必须保持 open”写回版本控制

## 3. 初始树真相

在本轮 live retrofit 开始时，`#143` 树的控制面状态可以分成三类：

- 已 merge 但仍未完成 control-plane 收口的子节点：
  - `#162` 对应 PR `#186`
  - `#178` 对应 PR `#184`
  - `#179` 对应 PR `#185`
- 结构上已无 child drift，但仍保持 open 的父层节点：
  - `#145`
  - `#146`
- 按计划仍需保持 open 的节点：
  - `#150`
  - `#143`

相关 merged PR 的宿主事实如下：

- PR `#184`
  - `mergedAt = 2026-04-17T15:00:56Z`
  - `merge commit = 017ce1be0848640477795c41746bc833286c4d3f`
- PR `#185`
  - `mergedAt = 2026-04-17T15:33:04Z`
  - `merge commit = 2546a357ea04070be656c68797d549ff0ac88e84`
- PR `#186`
  - `mergedAt = 2026-04-17T15:42:18Z`
  - `merge commit = f13998fd0ba21129e1c6e465d7cd34cb90f7b8af`

## 4. 审计与 sync 执行

### 4.1 先读父树，再定位 drift

先对 `#145`、`#146`、`#148`、`#150`、`#143` 运行：

```bash
python3 tools/loom_flow.py reconciliation audit --target /Users/mc/dev/Loom --issue 145 --project 5
python3 tools/loom_flow.py reconciliation audit --target /Users/mc/dev/Loom --issue 146 --project 5
python3 tools/loom_flow.py reconciliation audit --target /Users/mc/dev/Loom --issue 148 --project 5
python3 tools/loom_flow.py reconciliation audit --target /Users/mc/dev/Loom --issue 150 --project 5
python3 tools/loom_flow.py reconciliation audit --target /Users/mc/dev/Loom --issue 143 --project 5
```

结果：

- `#145`、`#146`、`#148`、`#150`、`#143` 都返回 `result = pass`
- 这证明树结构本身不存在新的 `parent_drift`
- 但这不等于这些 open issue 已自动满足 closeout；它只表示当前没有“已 merge 子项仍未被父 issue 消费”的结构性漂移

### 4.2 对已 merge 但仍 open 的子节点执行正式 sync

对实际存在 drift 的节点执行：

```bash
python3 tools/loom_flow.py reconciliation sync --target /Users/mc/dev/Loom --issue 162 --pr 186 --project 5
python3 tools/loom_flow.py reconciliation sync --target /Users/mc/dev/Loom --issue 178 --pr 184 --project 5
python3 tools/loom_flow.py reconciliation sync --target /Users/mc/dev/Loom --issue 179 --pr 185 --project 5
```

结果：

- `#162`
  - 关闭 absorbed-but-open issue
  - 将 Project 5 的 issue 状态对齐到 `Done`
- `#178`
  - 关闭 absorbed-but-open issue
  - 将 Project 5 的 issue 状态对齐到 `Done`
- `#179`
  - 关闭 absorbed-but-open issue
  - 将 Project 5 的 issue 状态对齐到 `Done`
  - 同时消费了 `#148` 的 parent drift，使 `#148` 进入关闭态并对齐到 `Done`

这里要特别记录一个事实：

- PR `#184`、`#185`、`#186` 的 `closingIssuesReferences` 均为空
- 因此，`#162`、`#178`、`#179` 并不是被 PR 自动关闭
- 它们是在 merge 事实已成立后，经 `reconciliation sync` 正式完成 control-plane 收口

### 4.3 对“阻断项已消失但仍 open”的父层 issue 做人工收口

`#145` 与 `#146` 在审计时都返回 `pass`，但 `closeout check` 继续因 “`issue is not closed`” 返回 `block`。这说明它们不是还存在结构漂移，而是仍缺最后一步正式 closeout。

本次 live retrofit 对这两个节点执行的动作是：

```bash
gh api repos/MC-and-his-Agents/Loom/issues/145/comments --method POST ...
gh api repos/MC-and-his-Agents/Loom/issues/145 --method PATCH --raw-field state=closed --raw-field state_reason=completed
gh api repos/MC-and-his-Agents/Loom/issues/146/comments --method POST ...
gh api repos/MC-and-his-Agents/Loom/issues/146 --method PATCH --raw-field state=closed --raw-field state_reason=completed
```

写回的 closeout basis 固定说明：

- `#145` 的最后 reopen blocker 是 `#167`，而 `#167` 现已 `CLOSED / Done`
- `#146` 的最后 reopen blocker 是 `#152`，而 `#152` 现已 `CLOSED / Done`
- 两个 issue 在 `2026-04-18` 的 `reconciliation audit` 都返回 `pass`

这一步不发明新的 sync 机制，只把已经消失的 reopen blocker 机械回写为最终 closeout 说明。

随后再对 `#145` 与 `#146` 的 Project 5 item 做最小字段 mutation，对齐到 `Done`。复验结果显示：

- `#145`
  - `state = CLOSED`
  - Project 5 `status = Done`
- `#146`
  - `state = CLOSED`
  - Project 5 `status = Done`

## 5. 树的收口结果

本轮 retrofit 结束后，`#143` 树可分成两组：

### 5.1 已完成收口的节点

- `#162`
  - `CLOSED`
  - Project 5 `Done`
- `#178`
  - `CLOSED`
  - Project 5 `Done`
- `#179`
  - `CLOSED`
  - Project 5 `Done`
- `#148`
  - `CLOSED`
  - Project 5 `Done`
- `#145`
  - 已补 closeout comment
  - issue 已关闭
  - Project 5 `Done`
- `#146`
  - 已补 closeout comment
  - issue 已关闭
  - Project 5 `Done`

### 5.2 仍必须保持 open 的节点

- `#150`
  - 继续作为“第一批多仓验证、发布面与收口”容器
  - `#169` 与 `#180` 完成前不得关闭
- `#143`
  - 继续作为第一批执行化父 issue
  - 在 `#150` 仍 open 时不得关闭

## 6. 与既有主合同的消费关系

本记录只消费已存在的正式合同：

- [../governance/issue-model.md](../governance/issue-model.md)
  - 承接 parent / child 与关闭语义边界
- [../governance/state-machine.md](../governance/state-machine.md)
  - 承接 `closed_out` 的唯一主定义
- [../harness/reconciliation-audit.md](../harness/reconciliation-audit.md)
  - 承接 `absorbed_but_open`、`parent_drift`、`project_drift`
- [../harness/closeout-gate.md](../harness/closeout-gate.md)
  - 承接 closeout gate 如何消费 reconciliation 结果
- [./validation-host-lifecycle-and-closeout.md](./validation-host-lifecycle-and-closeout.md)
  - 承接 control-plane sync 与 fail-closed 纪律的先前复验

## 7. 结论

`#180` 已经把 Loom 自身真实 `#143` 树上的关键残留 drift 收成版本化事实：

- 已 merge 但仍 open 的 `#162`、`#178`、`#179` 已通过正式 `reconciliation sync` 收口
- `#148` 已随 child drift 消失一并完成 closeout
- `#145`、`#146` 的最后 reopen blocker 已被消除，并已补写最终 closeout basis
- `#150` 与 `#143` 仍保持 open，这不是遗漏，而是对 `#169` 之前剩余收口面的显式保留

因此，本记录证明了 Loom 当前冻结的 issue / reconciliation / closeout 合同，已经足以对 Loom 自身的真实父子树执行 live retrofit，而不需要再发明新的关闭语义。
