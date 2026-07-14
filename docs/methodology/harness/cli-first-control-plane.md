# CLI-First Control Plane

Loom 的 CLI 拥有可执行语义；GitHub、Git worktree、Codex 与外部 provider
继续拥有各自事实。CLI 不把这些事实复制成仓库 execution carrier。

## 公共产品面

当前公共面固定为 `loom help --json` 返回的 30 个命令。命令名、domain、
状态与分层由 [cli-command-matrix.md](./cli-command-matrix.md) 和
`tools/loom.py` 的公共 registry 共同约束。

稳定规则：

- 公共命令必须是 `implemented`，不得以 delegated、reserved 或隐藏 alias
  充当默认入口；
- help、task route、`remediation_command`、skills 与默认 aggregate 只能推荐
  公共 registry 中的命令；
- compatibility 实现即使仍为迁移诊断保留，也不得进入公共 parser、默认路由、
  release readiness 或普通生命周期；
- branch、PR、head、checks、merge 与 issue 状态通过 GitHub readback 获得；
- worktree 通过显式 item、branch 和正式路径绑定，不读取 committed current
  pointer；
- review 与 closeout 消费 host attestation，不生成 status、progress、review、
  shadow 或 closeout carrier。

## 默认生命周期

默认交付路径是：

```text
route -> build -> pre-review -> review -> merge-ready
      -> pr gate -> merge check -> merge run -> closeout
```

`closeout` 消费 `attestation closeout` 的 host readback。`workspace
create|check|retire` 只管理显式 issue-scoped worktree；`retire` 是 local-only
cleanup。`acceptance resolve` 独立消费产品验收，不从 merge、CI 或 delivery
closeout 推导产品完成。

安装与诊断路径由 `detect`、`doctor`、`repair plan`、`install`、`upgrade`、
`verify` 和 `release readback` 承担。Codex plugin 安装与缓存属于 Codex host，
Loom 只返回 `provider_action`，不暴露额外的 host 安装或注册命令。

## 失败合同

每次失败只暴露一个 primary cause。机器输出使用 `loom-cli-output/v1` 或命令
拥有的窄 schema，并至少包含：

- `command`
- `result`
- `summary`
- `primary_error_code` 或等价 primary cause
- 可执行时的 `remediation_command`

`remediation_command` 必须来自 30 命令公共 registry。GitHub、Git、npm、
Codex、人工或 external provider 动作分别写入 `manual_action` 或
`provider_action`，不得伪装成 Loom 命令。

## 验证边界

默认产品验收使用：

- `python3 tools/check_cli_contract.py --surface public-default-path`
- `python3 tools/check_cli_contract.py --surface failure-envelope`
- `python3 src/skills/shared/scripts/loom_check.py --profile source --source-surface source-self-fixture .`

显式 compatibility aggregate 只用于迁移诊断，不是公共默认产品面或 release
完成证明。
