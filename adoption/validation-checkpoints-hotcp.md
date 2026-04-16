# Real Adoption Validation: Checkpoints In `hotcp`

## 1. 样本标识

- 样本仓库：`hotcp`
- 仓库类型：`复杂既有仓库`
- 仓库位置：`/Users/mc/dev/hotcp`
- 验证日期：`2026-04-16`
- 对应 Loom issue：`#36`

## 2. 仓库事实

- 已有清晰根级规则入口：`AGENTS.md`
- 已有多类运行与验证入口：Web App、本地基础设施、Extension、本地数据库、浏览器自动化
- 已有 merge 前承接面：`.github/`、PR 模板、review 规则、运行说明
- 仓库同时存在共享契约、高风险边界、多运行面与多环境 lane
- 当前缺口不是“有没有 checkpoint 名字”，而是 admission / build / merge 三类判断如何稳定前移并消费同一事实链

## 3. Loom 判断

- 当前样本不能继续停留在“只有 merge gate 较强”的状态
- 若用 Loom 承接，该样本必须走标准恢复形态，而不是 `checkpoint-lite`
- 三类 checkpoint 的执行侧入口应由 `tools/loom_flow.py checkpoint <admission|build|merge>` 承接
- `merge checkpoint` 之外新增的 `admission checkpoint` 与 `build checkpoint` 应先消费事实链，再消费 PR / review / 运行证据等补充材料

## 4. 首批装配结果

- 执行侧合同现在已形成：
  - `harness/checkpoint-model.md`
  - `harness/execution-chain.md`
  - `harness/merge-checkpoint.md`
- 机械入口现在已形成：
  - `python3 tools/loom_flow.py checkpoint admission --target <repo> [--item <id>]`
  - `python3 tools/loom_flow.py checkpoint build --target <repo> [--item <id>]`
  - `python3 tools/loom_flow.py checkpoint merge --target <repo> [--item <id>]`
- gate 不再只检查“是否有 merge 输入”，还会检查 checkpoint 入口存在性与最小结果语义

## 5. 摩擦、失效点与升级信号

- `hotcp` 证明 admission/build 必须稳定工程化：
  - 多运行面和多环境 lane 使“边做边想”不可持续
  - 若 build 阶段没有独立纠偏点，merge gate 会再次承担第一次系统性判断
  - PR 模板只能补充 merge 放行，不足以替代前序 checkpoint
- 当前样本也说明：
  - checkpoint 入口必须消费统一事实链，不能再造第二套状态摘要
  - 复杂仓库 adoption 仍需要正式 carrier 落位后，CLI 才能直接读取；本次 CLI 回归验证在 Loom demo 样本完成，`hotcp` 承担真实复杂仓库事实验证

## 6. 台账回写结果

- 本次没有新增 `EXT-*`
- 对齐并补强的稳定落点：
  - `EXT-0022`
  - `EXT-0030`
- 受影响 Loom 文件：
  - `harness/checkpoint-model.md`
  - `harness/execution-chain.md`
  - `harness/automation-frontload.md`
  - `tools/loom_flow.py`

## 7. 关闭依据

- `#36` 要求的 checkpoint 合同、执行入口、最小结果语义与 gate 校验都已进入版本控制
- Loom demo 现已覆盖 CLI 回归，`hotcp` 补足了复杂仓库为什么必须消费这组三类 checkpoint 的真实样本依据
- 当前仍未进入 Loom 默认内核的部分：
  - 宿主特定 PR / review / CI 集成细节
  - 复杂仓库内部更细的 checkpoint profile 分层
