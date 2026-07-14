# Gate Freeze（已退役）

本文件保留原合同 locator，但旧 gate-freeze snapshot 不再属于 Loom 公共产品面，
也不得作为默认交付路径的输入或补救建议。历史字段与设计过程由 Git 历史保留。

当前 gate 输入直接来自以下唯一事实源：

- GitHub Issue 拥有 Work Item scope；
- GitHub PR 拥有 branch、head、checks、mergeability 与 merge facts；
- 正式 issue-scoped worktree 由显式 item、branch 与路径绑定；
- current-head review 由 GitHub host attestation 证明；
- 产品验收由 acceptance adapter 独立证明。

默认交接顺序为：

1. `loom pre-review` 绑定真实 PR 与 current head；
2. `loom review` 消费 current-head host attestation；
3. `loom pr gate --full-output --json` 生成完整 readback，并保存在 repo-relative
   ignored workstation file；
4. `loom merge-ready --pr-gate-result-file <file>` 重新读取 GitHub host facts；
5. `loom merge check` 与 `loom merge run` 执行受控宿主委托。

该路径不读取或生成 committed current、status、progress、review、shadow、suite
carrier 或普通 closeout carrier。失败只返回一个 primary cause；补救必须指向公共
命令、GitHub/Git 手工动作或外部 provider action。

当前公共命令与 retained-result 合同见
[cli-command-matrix.md](./cli-command-matrix.md) 和
[controlled-merge.md](./controlled-merge.md)。
