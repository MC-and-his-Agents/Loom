# Closeout Gate

本文件定义 Loom 当前最小 closeout 执行链路。

宿主动作统一结果词表与 `fallback_to` 纪律见 [host-action-contract.md](./host-action-contract.md)。本文件只承接 closeout 专有的 fail-closed 顺序与同步边界。

## 1. 能力定位

closeout gate 用来回答两件事：

- 当前事项是否已经达到“进入主干并收口”的最小条件
- GitHub issue / PR / project / main 是否与仓内结果态一致

在 installed-skills 或 `.loom/bin` carrier 下，`reconciliation audit|sync` 与 `closeout check|sync` 必须先消费 `runtime-state`。
若 install layout、shared runtime、shared references 或 bootstrap manifest 漂移，入口必须直接 `block`。

Closeout-only PRs may consume the `loom-closeout-freeze/v1` terminal profile
defined in [gate-freeze.md](./gate-freeze.md#10-closeout-terminal-profile).
That profile freezes terminal facts for admission and closeout-specific gate
consumption; it is not a second closeout truth source and does not replace the
host/git/carrier readback performed by this file.

## 2. 稳定入口

- `python3 skills/shared/scripts/loom_flow.py reconciliation audit --target <repo> [--issue <n>] [--pr <n>] [--project <n>]`
- `python3 skills/shared/scripts/loom_flow.py closeout check --target <repo> [--issue <n>] [--pr <n>] [--project <n>]`
- `python3 skills/shared/scripts/loom_flow.py closeout sync --target <repo> [--issue <n>] [--pr <n>] [--project <n>]`
- `python3 skills/shared/scripts/loom_flow.py reconciliation sync --target <repo> [--issue <n>] [--pr <n>] [--project <n>] [--comment-file <path>] [--dry-run]`

## 3. `check` 最小检查面

`closeout check` 至少读取：

- closeout contract gate source、profile、subchecks 与 trigger reason
- 同范围 `reconciliation audit` 结果
- 若仓库声明了目标仓库 `release / version`，则读取当前 target release object 与 release closeout evidence；Loom 自身 CLI release 还必须消费 [Loom CLI Release Surface](../../adoption/loom-cli-release-surface.md) 中冻结的 release validation evidence contract
- issue 状态
- PR 是否已 merged
- 事项对应实现是否已达到 `absorbed`
- `host-binding inspect` 的 `binding_chain` 与 `dependency_graph`
- merged PR 是否已进入 `origin/main`
- project 中对应 issue 的状态
- suite path decision 与 full suite artifact locators，或 minimal path
  `not_applicable` rationale
- evidence-map locator、classification、freshness、scope、PR head、merge commit
  与 target branch backlink
- consistency-analysis locator、blocking/advisory/stale/missing/conflict/
  `not_applicable` 分类，以及未处理 gap 的 remediation direction
- merge-ready 消费过的 behavior evidence / test evidence 摘要
- 主干包含合并结果后仍可回链的 fresh verification evidence
- 可选 `/goal completion` evidence；调用方提供时只作为一致性输入消费，不作为完成真相源

若这些事实不一致，结果必须返回 `block`。

closeout 本地 gate 分为五层：

| profile | 默认消费者 | 说明 |
| --- | --- | --- |
| `closeout-contract` | 普通 closeout 默认 | 只校验 retained evidence schema、freshness、backlink、merge commit、target branch、issue / PR / Project / reconciliation 范围 |
| `source-self-fixture` | Loom source repo 或显式 source profile | 执行 Loom source fixture、runtime hygiene 与 repo-local wrapper 自检 |
| `bootstrap-regression` | scaffold / installer / demo bootstrap 场景显式 opt-in | 验证 bootstrap shaping，不是普通 closeout 默认必需面 |
| `distribution-regression` | release / generated skills / installer version 场景显式 opt-in | 验证安装面与发行面，不是普通 closeout 默认必需面 |
| `strong-profile-full-gate` | strong governance 或 repo-declared profile 显式 opt-in | 执行完整本地 gate；必须声明 owner、fallback、override path 与 authority-of-truth |

`--gate-profile auto` 等价普通 closeout 的 `closeout-contract`。`--skip-gate` 只允许跳过显式 heavy profile 的本地 `loom_check` 执行；它不得跳过 `closeout-contract` 的 retained evidence、backlink、PR、merge commit、target branch 或 reconciliation 检查。

When `closeout-contract` consumes a retained closeout freeze snapshot, it must
still re-read the current issue, PR, merge commit, target branch, carrier
bindings, release/no-release evidence, allowed paths, and retained review
disposition. Snapshot/hash mismatch, behavior or implementation drift, contract
or gate rule changes, release judgment disputes, mixed-risk batches, or allowed
paths violations require full review / guardian escalation.

review record backlink 使用与 merge checkpoint 相同的 head-binding 语义：PR head 与 reviewed head 完全一致时通过；差异仅限允许的 recovery/status/review/shadow/runtime carrier 时通过并输出 `head_binding.status == carrier-only`；任何实现文件漂移、schema drift、validation summary drift 或 unreadable head comparison 必须 fail closed。

native dependency unreadable、stale edge、open blocker 或 host binding inspector conflict 都必须按 [host-binding-inspector.md](./host-binding-inspector.md) 与 [native-dependency-contract.md](./native-dependency-contract.md) 暴露为 closeout finding；blocking profile 下不得把这些 gap 折叠成普通 issue closed/open 判断。

若仓库声明了目标仓库 `release / version`，`closeout check` 还必须至少能区分：

- `merged but unreleased`
- `released but unreconciled`
- 缺 changelog / release notes / migration notes / tag-artifact evidence
- 缺 rollback basis

这些缺口必须作为显式 closeout finding 暴露，不能被折叠成笼统的 host drift。

`closeout check` 只允许返回 `pass` 或 `block`：

- 普通 closeout 缺口
  - 返回 `block`，并把 `fallback_to` 指向 `merge`
- reconciliation 返回 `fix-needed`
  - 返回 `block`，并把 `fallback_to` 指向 `reconciliation-sync`
- reconciliation 返回 `block`
  - 返回 `block`，并把 `fallback_to` 指向 `manual-reconciliation`

`closeout` 不把 drift 或控制面缺口伪装成顶层 `fallback` 结果。

当显式选择 `source-self-fixture`、`bootstrap-regression`、`distribution-regression` 或 `strong-profile-full-gate` 时，本地 heavy gate 读取顺序必须保留来源：

1. 有 repo-declared `Makefile` `loom-check` target 时，先执行 `make loom-check`，来源标记为 `repo_declared_make_target`。
2. 只有缺少该 target 时，才回退到 profile-aware `.loom/bin/loom_check.py`，来源标记为 `repo_local_loom_check`；bootstrapped consumer repo 必须走 consumer profile / consumer validation chain，不得套用 Loom source/distribution self-check。
3. 只有缺少 repo-local runtime gate 时，才回退到 shared runtime `loom_check.py`，来源标记为 `shared_loom_check`；shared runtime 也必须先识别 source / consumer profile。

Adopted product repo 的 closeout 不得因为缺少 Loom source repo self-fixture（例如 `examples/new-project`）而绕过 repo 声明的正式 gate。

`closeout check` 内部消费 `reconciliation audit` 时，阻断纪律如下：

- `pass`：允许继续读取 merge / main / project 等 closeout 事实
- `warn`：必须显式挂到 closeout 输出，但不默认阻断
- `fix-needed`：必须返回 `block`；先经 `reconciliation sync` 完成机械对齐，再重新执行 closeout check
- `block`：必须返回 `block`；先消除硬冲突或缺失事实，且在 audit 重新达标前禁止任何 closeout sync 写入

`shadow parity` 默认不进入 closeout 阻断面。只有 strong governance profile 或显式 opt-in 启用 blocking 消费时，closeout/review/merge-ready 才能把 shadow parity 的 `mismatch` / `unreadable` 当作阻断输入；启用点必须同时声明 owner、fallback、override path 与 authority-of-truth。

closeout 消费 behavior/test evidence 的语义如下：

- 它不重新执行 BDD/TDD 判断，只校验 merge-ready 放行所消费的证据仍可回链当前 merged result
- 普通 closeout 默认消费 `review record -> merge-ready execution_attempt -> PR head -> host required checks -> merge commit -> target branch -> reconciliation audit`
- full path 下，closeout 还必须消费 evidence-map 与 consistency-analysis 的
  retained locator；若 retained locator 不可读、与 PR head / merge commit /
  target branch 不一致，或仍含 blocking consistency gap，必须返回 `block`
- minimal path 下，closeout 可以消费 `not_applicable` rationale 作为合法缺省，
  但 rationale 必须带 source locator、consumer boundary、recheck condition，并且
  与 spec / plan / recovery / merged result 不冲突；否则按 missing closeout basis
  处理
- consistency-analysis 中的 advisory gap 可以进入 closeout 输出摘要，但不得遮蔽
  source locator、freshness 或后续 remediation；blocking gap、stale evidence、
  head drift、host state conflict、deferred-as-completed 必须阻断
- host PR checks evidence 只证明当前 head 的检查状态和 freshness，不替代 Loom review record 或 reconciliation audit；当 versioned `merge-ready` execution_attempt 未被 retained runtime 写入版本控制时，可作为 legacy merge-ready freshness fallback，但必须在 subcheck 中标记 `source=host_pr_checks` 与 `fallback_reason=missing_versioned_execution_attempt`
- review record 必须 `decision == allow`、kind 属于 implementation review，并且 `reviewed_validation_summary` 与当前 validation summary 一致；`reviewed_head` 必须覆盖 PR head，若 review 后到 PR head 的差异只包含 review / recovery / status / owned runtime evidence carriers，可作为 `carrier-only` head binding 消费
- merge-ready evidence 优先来自同一 Work Item 的 successful `merge-ready` execution attempt，且 `head_sha` 与 PR head 一致；若 retained execution_attempt 存在但 stale、invalid 或 head mismatch，不得回退到 host checks
- 当 validation summary 引用 `daily-execution-cli-fast` / `daily-execution-cli-full` 时，closeout 必须保留两者的消费边界：fast run 只能作为 focused troubleshooting 或本地迭代证据；full run 或等价 full aggregate 才能作为默认 daily-execution-cli retained validation basis。若 closeout 只能找到 fast locator，必须返回 `block` 或记录拥有方明确的 narrow-scope rationale、remaining risk、recheck condition 与 scheduler-owned gate disposition。
- 默认 `no_release` closeout 仍必须消费 release/no-release 判断本身。`daily-execution-cli-full` pass 可以支持 no-release 的验证依据，但不能替代 PR metadata、review、fact-chain、hosted checks、controlled merge、target branch readback、reconciliation audit 或 release judgment。
- Loom CLI release closeout 必须把三类 release evidence 分开保留：
  - release-surface validation evidence：例如 `release-doc-contract`、`release-workflow-contract`、`installer-sunset-guard`、`forbidden-release-surface-patterns`、`npm-package-manifest`、`npm-pack-payload`、`installed-global-cli-smoke`，证明 release/package 机制、临时全局安装 smoke 和 payload 合同在当前 head 上仍成立。
  - release-required closeout evidence：发布发生后绑定 PR head、merge commit、`loom-cli-release` main-push run、GitHub `v*` tag、GitHub Release、npm package registry readback、dist-tag state、installed/global CLI smoke 和 installer non-advancement。
  - `no_release` rationale evidence：未发布时说明没有用户可见 CLI / skills / package / workflow / runtime behavior 被交付，并证明该结论不依赖 PR-event `release-judgment-only`。
- 下游 release-required Work Item 可以消费这些 evidence label，而不是把 release/package validation 当成单一黑盒；但 closeout 必须记录当前实际命令或 hosted run 如何覆盖对应 label。命令可以是 named surface（例如 `--surface npm-package-manifest`）或 aggregate surface（例如 `--surface aggregate-release-surface` / `--surface aggregate`），但 aggregate 证据仍必须保留 label、head/merge commit、run locator 和 consumer boundary。若只能看到 aggregate command pass 而没有这些字段，结果必须返回 `block` 或要求 release evidence repair。
- 若证据只覆盖 merge 前 `HEAD`，必须能通过 PR / merge commit / main 包含关系证明该证据仍覆盖当前主干结果
- 若 closeout 发现主干、issue、project 或 evidence locator 无法互相回链，必须返回 `block`
- 若 subagent 输出没有被整合到 review record、验证摘要或 merge-ready basis，closeout 不得把它作为 `absorbed` 或 `closed_out` 依据
- 若提供 `/goal completion` evidence，closeout 必须校验它的 Work Item 与 `head_sha` 仍绑定当前 closeout 上下文；mismatch 返回 `block`，valid 也只表示该 evidence 可消费，不表示 closeout 已完成

Closeout reconciliation 对 full suite evidence 的消费顺序固定为：

1. 先消费 PR / merge commit / target branch / issue / Project / dependency
   graph 的 host basis。
2. 再消费 review record 与 merge-ready execution attempt 中 retained 的
   suite、evidence-map、consistency-analysis backlink。
3. 再判断 evidence-map 是否仍覆盖 merged result。
4. 最后消费 `reconciliation audit` 的 refreshed result。

任一步无法回链时，closeout 只能返回 `block`，并指向 `merge`、
`reconciliation-sync` 或 `manual-reconciliation`。PR merged、issue closed、
Project Done、CI success 或 host checks green 都不能单独证明 `closed_out`。

closeout truth 与 workspace retire 必须分层：

- 版本化 closeout truth 必须在 merge 前通过 review / merge-ready / closeout basis 进入可审查载体
- merge 后 `closeout check|sync` 只消费 PR、merge commit、target branch、issue、Project 与 repo-authored artifacts 的一致性
- `workspace retire` 只做 local cleanup / runtime evidence，不写 `.loom/progress/**` 或 `.loom/status/current.md`
- `carrier closeout-sync` 是唯一用于写入结构化 terminal closeout metadata 的版本化 carrier sync 入口；默认 dry-run，只有显式 `--apply` 才写 `.loom/progress/<item>.md`
- post-merge retire 不得制造新的需要再开 PR 合入 main 的 carrier diff

HotCP-style stale active carrier closeout 必须把三类 evidence 分开保留：

- host evidence：PR mergedAt、merge commit、target branch contains merge commit、issue state/reason、Project status，以及 release/no-release judgment。
- local-only retire evidence：`workspace retire` 的 `retire_scope = local_only` 与 `versioned_carrier_updates = []`。
- carrier sync evidence：`carrier closeout-sync --dry-run` 与 `--apply` 的 `host_mutations = false`、写入的 terminal metadata、以及随后 `fact-chain` 读回 `idle` / `no_active_item`。

这一路径可以消费 #1236 HotCP regression fixture 的行为证明；它不能把 workspace retire、host issue close、CI success 或 PR merge 单独当作 repo carrier closeout 完成。

这里的 `absorbed` 只表示 host merge 后可证明的实现吸收结论，不等于 `closed_out`。
因此，`closeout check` 至少要能区分：

- 该 issue 已由其对应实现进入 `closed_out`
- 该 issue 的对应实现已 merged，但 issue 仍 open，需要 `reconciliation sync`
- 该 issue 的实现已被其他 merged work `absorbed`，但控制面尚未完成 closeout sync
- 该 issue 仍保留独立剩余缺口，不能被视为 `absorbed`
- GitHub host signal 不可读或互相冲突，必须进入 `manual-reconciliation`

## 4. `sync` 最小动作

本阶段的正式写路径是 `reconciliation sync`。`closeout sync` 不单独跳过这一步；它只在同范围 reconciliation 已达可同步条件后继续消费 closeout 结论。`reconciliation sync` 只做控制面对齐动作：

- 先消费同范围的 `reconciliation audit` 结果，再生成可执行 sync 计划
- 在条件满足时关闭 issue
- 在 project 中把对应 item 状态设为 `Done`
- 可选写入 closeout comment，但该写入必须作为 `add_closeout_comment` plan action 独立出现

约束：

- 若 `reconciliation audit` 出现任一 `block` finding，`sync` 必须直接返回 `block`，且不做任何写入
- `sync` 只允许对 `fix-needed` finding 做机械修复；`warn` 仅保留提示，不触发写入
- `--dry-run` 只输出基于 audit 的计划，不修改 GitHub 控制面
- `--dry-run` 是默认行为；只有显式 `--apply` 才允许执行写入
- `--comment-file` 与 `--comment` 二选一，只为当前 issue closeout comment 提供正文来源
- 输出必须保留 `audit`、`sync_plan`、`applied_actions`、`skipped_actions`、`manual_actions`、`refreshed_audit` 与 `remaining_findings`
- sync 后的 closeout 判断只能消费 `refreshed_audit`；不得只相信写入命令成功

`closeout sync` 仍保持 closeout 控制面对齐入口，但不得绕过已显式暴露的 reconciliation 结果。

`closeout sync` 也只允许返回 `pass` 或 `block`。若同步前置不满足，或同步后仍无法把控制面对齐，必须继续显式指向 `reconciliation-sync`、`manual-reconciliation` 或 `merge`，而不是产出新的 host action 结果词表。

`carrier closeout-sync` 不得调用 GitHub、关闭 issue、修改 Project、合并 PR 或删除 worktree。它只消费调用者显式提供的 terminal closeout metadata，并产出 reviewable repo diff。

若 parent issue 通过 child issue 的 `closed_out` / `absorbed` 结果完成自身 closeout 判断，`sync` 只负责把这一已成立结论写回控制面，不替代 parent 对剩余缺口的判断。

它不替代：

- PR merge 动作
- `absorbed` 证明本身
- review 执行层
- recovery writeback
- workspace cleanup / retire

## 5. 非目标

- 不在 Loom 内核里固化 GitHub UI、按钮或 ruleset 细节
- 不把 project 中不存在的 PR item 强行当作阻断
- 不让 closeout sync 绕过 gate 或 merge 事实
- 不把 reconciliation sync 扩展成新的对象模型或自动化宿主产品
