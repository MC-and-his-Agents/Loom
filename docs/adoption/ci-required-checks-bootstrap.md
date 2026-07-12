# CI Required Checks Bootstrap

Loom 可以提供 GitHub Actions workflow 模板和 stable check-name 合同，帮助新仓库把本地 gate starter 接到宿主控制面。

Loom 不把 workflow 文件存在解释为宿主强制门禁。强制能力仍由 GitHub branch protection、ruleset、required checks、PR merge path 与 runner 执行状态承接。

## Stable Check Names

当前默认 required check names：

- `py-compile`
- `loom-delivery-gate`

这些名称必须稳定，因为 GitHub required checks 绑定的是 check name。`main` push 只追加
`host-native-lifecycle`，消费 admission、closure guard、host attestation、product
acceptance、light profile 与 failure envelope 等 targeted contracts。旧的
`demo-bootstrap`、`repo-local-cli`、root self-governance 与 full `loom-check` carrier
aggregate 已退出 hot path，也不再提供 repo-local replay aliases。

PR/merge queue 的候选验证由 `loom-delivery-gate` 按 changed paths 与 repository
profile 选择最小 native targets；当 protected harness 本身变化时，PR 的
`release-judgment` 另行执行同一个 `make loom-check` host-native contract aggregate，
不重复 full CLI aggregate。

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

## Delivery Gate Enforcement 与身份 readback

`loom-delivery-gate` 的 base-owned direct `pull_request_target` 与默认分支 `merge_group` 固定以 `enforce` 运行。当前 partial delivery 只在 coordinator 的 run/path/event/head 与 trusted finalizer digest readback 不完整时让 terminal check 失败；读回完整时 compatibility check 成功，但机器结果固定为 `limited` / `host_enforcement_unavailable`，不能作为产品放行。gate 仍从 candidate tree 的 `loom-installed-state/v2` 读取 repository adoption profile；既有 execution-control 仓库可由 `loom-repo-interface/v2` companion 兼容识别。light adoption 无需在 direct-event facts 中手工声明 `profile`。candidate native 结果仅上传为带 `untrusted-` 前缀的诊断 artifact，不参与 terminal verdict；#2063 建立 strong host identity 后，forbidden carrier、profile mismatch 与 native validation 才能进入强制放行语义。

reusable caller 必须显式声明 `host_facts`、与 `uses@SHA` 相同的 `loom_ref`、
`profile`、`enforcement: advisory|enforce` 与目标仓自己的 `validation_command`。
其中 `validation_command` 不是 shell command，而是 Loom 固定 allowlist 中以空格
分隔的 Make targets；表达式、多行值、shell operator 与任意 executable 都会被拒绝。
Loom 不再给下游仓库默认注入 evaluator 自测命令。caller 的 `profile` 只能显式提升本次验证强度，不能降级 candidate repository profile，也不能覆盖 candidate adoption authority。无论模式为何，`product_acceptance: not_evaluated` 都不构成 delivery failure。

候选 native validation 与 trusted evaluator/finalizer 分属不同 runner。direct Loom PR
从 base SHA 读取 Makefile、checker 与固定 fixtures，把 head checkout 仅作为被测树；
direct 被测树出现任何 Git symlink 或 `lstat` symlink 时 fail closed。该零 symlink
规则只属于 Loom 自身 direct trusted validation，不自动外推到 reusable caller。
reusable caller 使用 GitHub readback 的 base/head SHA 建立 caller-owned trusted harness，并只对
Makefile、`tools` 与 `.github/actions` 等受保护验证路径禁止 symlink。
这里的“声明”不是 caller 自报 authority：reusable workflow 必须从当前
`pull_request_target`/`merge_group` 事件和 GitHub API readback 独立派生 base repository、
fork-aware head repository、base/head SHA 与 changed paths。caller `host_facts` 缺少
`change` 不影响派生；若其中自报的 repository/change/event/changed paths 与 host
readback 冲突，则以单一 host-readback failure 失败，且不得 fallback 到
`github.sha` 或 caller ref。reusable caller 的非 harness symlink 只有在使用相对路径、
目标存在且 resolve 后仍位于 candidate root 内时才允许；绝对、断链、越界或指向
runner/harness 的链接全部 fail closed。

只有 repository、event binding、fork-aware head repository 与 40 位 base/head SHA
全部通过 readback 后，workflow 才输出 `authority_ready=true`。该字段不是 caller
input。API 403/5xx、字段缺失或冲突时，plan/native/final 均执行零 checkout、零
candidate evaluator，并由 terminal step 输出固定 `host_authority_unavailable` blocked
envelope。PR changed paths 触及 GitHub 3000-file 上限、merge comparison 触及
300-file 上限时，完整性不可证明，同样 fail closed；不能把截断集合交给 selector。
private fork head 若无法由 base token 读取也保持 blocked，这属于已知宿主权限残余，
不能 fallback 到 base repository 的同名 ref 或当前 event SHA。

为使 direct 不变量可执行，本次删除以下已跟踪 legacy inventory，且不生成替代副本：

- `.agents/skills/loom-adopt`
- `.agents/skills/loom-build`
- `.agents/skills/loom-handoff`
- `.agents/skills/loom-init`
- `.agents/skills/loom-merge-ready`
- `.agents/skills/loom-pre-review`
- `.agents/skills/loom-resume`
- `.agents/skills/loom-retire`
- `.agents/skills/loom-review`
- `.agents/skills/loom-spec-review`
- `.agents/skills/loom-story`

这些路径原先都是绑定 `/Users/claw/dev/Loom/...` 的绝对 symlink；安装合同已将
`.agents/skills` 定义为默认 absent 的 compatibility residue，因此不能继续参与 CI
或安装事实判断。

caller 的 `enforcement` input 可以随 PR workflow 改写，因而它只能选择本次执行模式，不能证明下游仓库已经把该检查设为 required。迁移保护面时必须采用增量顺序：先在现有保护面中追加 `loom-delivery-gate`，再执行只读 host readback，最后才移除旧 required checks。不能提交 registry、caller YAML、PR body 或 workflow 文件作为这种证明。

```bash
python3 tools/read_delivery_gate_required_identity.py \
  --repository WebEnvoy/Lode \
  --branch main \
  --context 'loom-delivery-gate / loom-delivery-gate' \
  --app-id 15368 \
  --trust-mode pull_request_target_same_app \
  --retained-context py-compile \
  --legacy-context demo-bootstrap \
  --legacy-context repo-local-cli \
  --legacy-context loom-check \
  --legacy-context loom-pr-merge-gate
```

`--context` 与 `--app-id` 都是显式期望值：不能由 workflow 名、caller input 或 Loom 默认值猜测。上例来自 Lode PR #260 的 GitHub check-runs host readback：head `f910392…` 上成功 check 的 display context 是 `loom-delivery-gate / loom-delivery-gate`，app 是 `github-actions`（id `15368`）。切换前应先对目标仓库实际运行的 check-runs 做同样的只读读取，再把观察到的 pair 传给本命令。

该命令同时只读 GitHub branch-protection API、`rules/branches/<branch>` 的适用
branch rules 与 Actions workflow id/path/state。后者由 GitHub 按目标 branch 计算，
避免客户端自行猜测 ruleset 的 ref 条件。信任模式固定为：

- `required_workflow`：当前只能收集诊断，固定为 `limited`；仅有 workflow path、
  repository/ref/ruleset id 与 workflow id/path/state 仍不能证明当前 run、目标分支和
  ruleset enforcement 的完整绑定，#2063 完成专用 host adapter 前不得返回 `strong`；
- `distinct_app_check`：required check 绑定到不同于 GitHub Actions（app id
  `15368`）的专用 GitHub App，才是 `strong`；
- `pull_request_target_same_app`：base-owned coordinator 是受限防线，但同一
  GitHub Actions app 下仍可产生同名 check，因此 verdict 固定为 `limited`，以
  `host_enforcement_unavailable` 返回 `blocked`。

当前 Loom repo rulesets 为空，org rulesets API 返回“Upgrade to GitHub Team”，且
repo-level REST rules surface 不提供 required-workflow rule。因此现有计划没有可配置
的 repo-level required-workflow payload，也没有 distinct App；#2054 必须把此限制
记录为 blocked，不能把 same-app required context 表述为 stable/strong。输出是一次
host readback evidence，不是应提交进仓库的 registry。

当前 `pull_request_target` compatibility check 的 conclusion 可以成功，但机器输出固定为
`assurance: limited`、`trust_verdict: limited` 与
`host_enforcement: host_enforcement_unavailable`。GitHub branch protection 不消费这些
workflow outputs，因此该同名 compatibility context 绝不能配置为 required product gate；
只有 #2063 建立的独立 strong consumer/context 才能放行。当前能力只允许作为 #2046 的
partial delivery 合入，不满足 #2046 FR closeout 或 #2054 stable release。

`--retained-context` 可重复定义迁移后仍允许的 native 或 release check；默认没有额外保留项，但 `--context` 本身自动保留。`--legacy-context` 可重复提供所有应退役的旧检查。任意 branch-protection 或适用 ruleset 仍要求其中之一时，结果为 `legacy_required_checks_present`，即使新 check 已经出现也不能移除旧治理面。上例中的 `loom-pr-merge-gate` 来自 Lode `main` 的实际适用 ruleset（id `18294167`）。

effective required 集是精确合同：除预期 context 和显式 retained contexts 外，任何其他 context 都返回 `unexpected_required_checks_present` 并阻断。这避免遗漏旧 check 便把 protection/ruleset 视为已替换。已声明 legacy 与未声明 unexpected 同时存在时，legacy verdict 优先，先引导退役已知旧 gate。GitHub ruleset required-status-checks 响应只给 context、不给 app identity；因此预期 check 若只出现在 ruleset 而没有同一 context 的 branch-protection app readback，结果保持 `unknown`，不得把 context-only 规则误报为身份已验证。

GitHub branch-protection API 把 required status check 绑定到 context 与 GitHub App，不能由此证明某个可变 PR caller workflow 的具体路径。因此本 readback 只授权采用该 app identity 的 required-check 过渡；若下游改用 GitHub `required_workflows` ruleset，必须先补充并通过该 ruleset 所能提供的精确 workflow host readback，不能把本检查的 `ready` 外推为 workflow-path identity。
