# Automation Frontload

本文件定义 Loom 当前公共产品面的自动化前置原则：机械事实尽早验证，语义判断留给
current-head review，昂贵验证只在输入稳定后运行。

## 1. 前置顺序

1. `loom detect` / `loom doctor` 读取安装角色与 light invariant；
2. `loom build` 绑定 typed Work Item、正式 worktree 与 branch；
3. 仓库原生 static / contract / targeted tests 验证当前 diff；
4. `loom pre-review` 绑定真实 PR 与 GitHub live head；
5. `loom review` 消费 current-head host attestation；
6. `loom pr gate --full-output --json` 生成单一根因的完整 readback；
7. `loom merge-ready` 消费 retained result、attestation 与最新 GitHub facts；
8. 只在稳定 head 上运行必要 aggregate、hosted negatives 与 release readback。

公共路径不要求空提交、空 PR、committed current pointer、status、progress、review、
shadow、suite 或 closeout carrier。

## 2. 机械检查边界

| Surface | Machine-owned check | Not decided by the check |
| --- | --- | --- |
| install/profile | role、manifest、forbidden path、payload digest | 仓库是否值得采用 Loom |
| workspace | Work Item、branch、formal worktree、PR/head 一致性 | scope 是否正确 |
| diff | paths、format、compile、targeted tests | 产品语义是否满足 |
| review handoff | exact PR head、attestation identity/digest | reviewer 的语义判断 |
| delivery gate | policy、required checks、mergeability、单一根因 | product acceptance |
| release | live WI/milestone/dependencies、umbrella acceptance、version/package consistency | 外部产品故事是否完成 |

Governance lint 只提供 derived diagnostics，不写第二份事实。taxonomy 见
[governance-lint-taxonomy.md](./governance-lint-taxonomy.md)。

## 3. 失败处理

高成本检查失败后先归类为代码语义、evidence、PR metadata、Git history、环境、
权限、host service 或 external dependency。每个公共命令只暴露一个 primary
cause；其余诊断必须标成 consequence 或 suppressed diagnostic。

不得把 stale pointer、缺少 repo carrier 或旧内部命令包装成通用
`governance_metadata_failure` 后要求恢复旧控制面。

## 4. CI 节奏

- feature head 运行 targeted PR workflow；
- main push 运行 aggregate；
- release workflow 的普通 PR/main 事件只做 judgment；
- 每个 release head 只生成一次 umbrella acceptance；
- superseded run 可取消，但同一高成本 run pending 时应等待，不重复启动。

默认 aggregate 必须验证公共命令 reachability、removed-state semantics、package
payload、generated parity 与 release admission；不能让 transition fixture 反向要求
恢复已删除实现。

## 5. 非目标

自动化不判断目标是否值得做、方案是否正确或产品是否真正可用。产品完成必须由
目标 acceptance adapter 的可信 evidence 证明，delivery gate 不得自行推导。
