# Zero-Friction Adoption Contract

本文冻结 Loom 面向既有仓库的 agent-assisted zero-friction adoption 合同。

它不是新的治理真相源，也不是 unattended strong adoption。它把 agent 采用 Loom 时必须完成的读取、判断、回写与验证闭环固定下来，让下游仓库不需要手写 `repo companion` / `repo interop` / residue evidence 的基本结构。

## 1. 目标与边界

zero-friction adoption 的目标是让 agent 能从 Loom 输出独立完成一轮 bounded adoption：

- 读取目标仓库已有根规则、验证入口、治理载体与宿主控制面
- 判断本轮采用路径、启用能力、暂不启用能力与升级触发条件
- 在用户要求落盘时生成 repo-local companion / interop 入口
- 用 verify / fact-chain / resume guidance 关闭本轮 adoption

稳定边界：

- 不把任何下游仓库的 repo-native review / guardian 规则提升为 Loom core 默认规则
- 不要求 fully unattended one-command strong adoption
- 不把 `repo companion` 或 `repo interop` 写成第二套运行态真相
- 不让 generated files 接管 branch、PR、worktree、merge、ruleset 或 host action 的底层实现
- repo-owned residue 继续由目标仓库持有；Loom 只提供结构、locator、合同、生成与验证语义

## 2. 固定生命周期

zero-friction adoption 固定按 `read -> judge -> write -> verify` 关闭。

### 2.1 Read

`read` 必须收集可定位输入，而不是猜测仓库形态。

最小读取面：

- 根级边界文档，例如 `AGENTS.md`、`README`、workflow / review 文档
- 当前验证入口，例如 CI、测试命令、repo-local verify script
- 已有 governance / status / recovery / review / closeout carrier
- 已有 repo-specific gates、retained host actions、repo-native carriers
- 当前 Loom manifest、repo companion、repo interop 是否已存在

每个关键结论必须带 source locator。没有 locator 的判断只能作为缺口，不能作为采用事实。

### 2.2 Judge

`judge` 输出采用决策，而不是直接改写仓库。

固定判断项：

- `repository_mode`
  - `new | small-existing | complex-existing | unknown`
- `adoption_path`
  - `minimal-bootstrap | lightweight-retrofit | recognize-and-attach | defer`
- `adoption_intent`
  - `observe-only | skill-install-only | attach-only | light-governance | execution-control | strong-governance | unspecified`
- `enabled_capabilities`
- `deferred_capabilities`
- `upgrade_triggers`
- `decision_reason`
- `source_locators`
- `write_targets`
- `validation_commands`

当判断需要 repo-specific 信息时，Loom 输出必须给出固定 decision prompt，而不是让执行者自由猜测。

当 `adoption_intent = unspecified` 且写入计划会创建 Loom-authored `work-items`、`progress`、`status` 或 `specs` 等重执行控制面时，CLI 必须 fail closed：输出候选 intent、风险摘要和 planned writes，不得静默落盘。

当 `adoption_intent = attach-only` 时，dry-run / write 输出必须同时列出 required carriers 与 `forbidden_authored_carriers`。默认禁止 `.loom/work-items/**`、`.loom/progress/**`、`.loom/status/current.md`、`.loom/reviews/**`、`.loom/specs/**`；verify 必须检查磁盘存在、`init-result` 声明、`planned_writes`、bootstrap manifest 与 write touched。发现任一 forbidden carrier 时必须 fail closed，并要求迁移到宿主 truth locator、删除 competing carrier，或显式升级到 `execution-control`。

## 3. Decision Prompt Fields

decision prompt 至少包含：

- `target_repository`
- `adoption_scope`
- `write_intent`
  - `dry-run | write`
- `adoption_intent`
  - 用户显式选择的接入意图；未给出时必须写为 `unspecified`
- `repository_mode_guess`
  - 可为 `unknown`
- `existing_governance_signals`
  - 每项必须包含 `summary` 与 `locator`
- `existing_validation_entry`
  - 命令、CI 或 repo-local 验证入口；没有时必须显式为缺口
- `companion_boundary_intent`
  - 本轮是否生成或更新 `repo companion`，以及目标 locator
- `interop_boundary_intent`
  - 本轮是否生成或更新 `repo interop`，以及目标 locator
- `repo_owned_residue`
  - 本轮保留在目标仓库 ownership 下的规则、carrier 或 host action
- `verification_commands`
- `resume_after_adoption_intent`

每个 prompt 字段必须能被写回为：

- source locator
- reasoning
- writeback target
- verification evidence

缺任一项时，本轮采用不得宣称完成；只能输出缺口与下一步。

## 4. Generated Companion Boundary

generated `repo companion` 只能生成或更新以下内容：

- `.loom/companion/manifest.json`
- `.loom/companion/README.md`
- `.loom/companion/repo-interface.json`
- 与 repo-specific requirements、specialized gates、metadata/context locator 相关的 companion-owned 文档

它必须遵守 [repo-companion-contract.md](./repo-companion-contract.md)：

- manifest 只做 locator
- `repo-interface.json` 只承接 repo-specific requirements、specialized gates、metadata/context locator contract
- 不写入运行态、review summary、validation status、current stop、closeout result 或 host action result
- 不把 repo-specific 字段升为 Loom core 默认 taxonomy

## 5. Generated Interop Boundary

generated `repo interop` 只能生成或更新以下内容：

- `.loom/companion/interop.json`
- retained host action result 的只读 locator
- repo-native carrier / evidence / truth 的只读 locator
- shadow parity compare surface 的只读 locator

它必须遵守 [repo-interop-contract.md](./repo-interop-contract.md)：

- `interop.json` 只告诉 Loom 去哪里读，不告诉 Loom 如何执行宿主动作
- 默认 shadow parity 是 validation-only
- 不声明 blocking owner、override path、authority-of-truth 或 final verdict
- 不把 guardian、integration、ruleset 或 merge-native verdict 复制成 Loom-authored truth

## 6. Write Discipline

`write` 只在 `write_intent = write` 时执行。

写入前必须明确：

- 本轮 write targets
- 每个 target 的 source locators
- 每个 target 的 ownership
- 每个 target 的验证命令
- 不写入项与原因

写入后必须保证：

- 新增文件可被 Loom 入口定位
- 未生成的 companion / interop surface 被显式记录为 intentionally absent
- repo-owned residue 保留在原 ownership
- 没有新增平行事实链或平行状态面
- 稳定 `.loom` carrier 遵守 [.loom surfaces 版本控制策略](./loom-surfaces-version-control.md)，不能被 blanket `.loom/` ignore 隐藏

## 7. Adopt Verify Closure

`loom-adopt verify` 关闭 adoption 时，至少必须确认：

- generated companion locators 存在，或被标记为 intentionally absent
- generated interop locators 存在，或被标记为 intentionally absent
- companion / interop 边界未承载运行态真相、host action result 或 closeout result
- repo-specific 判断都有 source locator、reasoning、writeback target 与 verification evidence
- 稳定 `.loom` carrier 对 Git 可见；`.loom/runtime`、`.loom/tmp`、`.loom/cache` 等运行态残留不被误报为必须提交
- `fact-chain` 能复读 adoption 结果
- resume guidance 能给出后续 continuation entry 或明确说明无需恢复

如果 verify 无法证明以上条件，结果必须 fail closed，并输出缺口。

## 8. Resume Guidance

adoption 完成后，`loom-resume` 不消费 adoption 输出作为新的事实源。

它只能把 adoption 输出当成 locator 与 control-plane context：

- adoption source
- companion locator
- interop locator
- verification summary
- post-adoption next step

随后仍按 `runtime-state -> fact-chain -> state-check -> workspace-locate` 恢复。若 adoption 只完成 dry-run 或 verify 未关闭，resume 必须回退到 admission 或 adoption verify，而不是猜测下一步。

## 9. 与其他合同的关系

- [repo-companion-contract.md](./repo-companion-contract.md)
  - 冻结 repo-specific requirements、specialized gates、metadata/context locator 的主合同
- [repo-interop-contract.md](./repo-interop-contract.md)
  - 冻结 retained host action result、repo-native carrier 与 shadow parity 的只读合同
- [lightweight-retrofit-default.md](./lightweight-retrofit-default.md)
  - 小型既有仓库的默认低摩擦采用路径
- [deep-existing-repo-default.md](./deep-existing-repo-default.md)
  - 成熟治理重仓的 attach-only 默认路径
- [github-profile-upgrade.md](./github-profile-upgrade.md)
  - GitHub profile 的 advisory / blocking / rollback gate rollout 合同
- [loom-surfaces-version-control.md](./loom-surfaces-version-control.md)
  - 冻结稳定 `.loom` carrier 与运行态 scratch 的 Git 可见性边界

本合同只定义 adoption 闭环，不复制这些合同的 schema 或 gate 规则。
