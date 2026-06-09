# CI Required Checks Bootstrap

Loom 可以提供 GitHub Actions workflow 模板和 stable check-name 合同，帮助新仓库把本地 gate starter 接到宿主控制面。

Loom 不把 workflow 文件存在解释为宿主强制门禁。强制能力仍由 GitHub branch protection、ruleset、required checks、PR merge path 与 runner 执行状态承接。

## Stable Check Names

当前默认 check names：

- `py-compile`
- `demo-bootstrap`
- `repo-local-cli`
- `loom-check`

这些名称必须稳定，因为 GitHub required checks 绑定的是 check name。

`repo-local-cli` check 内部的可诊断 command groups 可以在本地用 [repo-local gate starter aliases](../methodology/harness/repo-local-gate-starter.md#repo-local-cli-local-validation) 重放。那些 local aliases 必须保留 CI group names/order，但它们不是新的 required check names，也不能被描述为比 hosted `repo-local-cli` 或 `loom-check` 更弱的 merge-ready gate。

## Read Surface

`github_control_plane.ci_check_presence` 区分：

- `workflow_exists`
- `check_ran`
- `required_checks_configured`
- `host_enforcement_status`

`github_control_plane.host_enforcement` 区分：

- `branch_protection_or_ruleset`
- `required_checks`
- `workflow_exists`
- `check_ran`
- `verification_status`

## Upgrade Rule

新仓库可以先拥有本地 aliases 和 workflow 文件，但只有以下事实被宿主读面验证后，才能作为 strong governance 的输入：

- workflow 存在并由宿主识别。
- stable check names 已配置为 required checks。
- branch protection 或 ruleset 处于 enforced 状态。
- check runs 真实运行过。

远端读取失败时必须输出 `unverified` 或 `host_unavailable`，不能把失败解释为空 ruleset、空 required checks 或 disabled protection。
