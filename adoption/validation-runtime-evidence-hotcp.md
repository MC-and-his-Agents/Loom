# Real Adoption Validation: Runtime Evidence In `hotcp`

## 1. 样本标识

- 样本仓库：`hotcp`
- 仓库类型：`复杂既有仓库`
- 仓库位置：`/Users/mc/dev/hotcp`
- 验证日期：`2026-04-16`
- 对应 Loom issue：`#38`

## 2. 仓库事实

- `AGENTS.md` 已给出 Web App 启动入口、本地基础设施入口、Extension 启动入口与浏览器自动化入口
- 仓库存在明确环境 lane 差异：本地开发、强制本地模式、联调线上模式、生产构建
- 可读取证据入口并不只有“应用能不能启动”，还包括日志、数据库、浏览器自动化和 UI/API 观察面
- 这类仓库若没有正式运行时证据承接，merge 前验证很容易退化成“本地跑过”口头结论

## 3. Loom 判断

- 运行时可见性必须进入状态面的固定机读区块，而不是只在说明文档里散落
- `Runtime Evidence` 五字段对该样本都具有明确语义：
  - `Run Entry`
  - `Logs Entry`
  - `Diagnostics Entry`
  - `Verification Entry`
  - `Lane Entry`
- `not_applicable` 必须支持按字段逐项声明，而不是整组一刀切

## 4. 首批装配结果

- 稳定合同现在已形成：
  - `harness/status-surface.md`
  - `skills/loom-init/references/output-contract.md`
- 机械入口现在已形成：
  - `python3 tools/loom_init.py fact-chain --target <repo>`
  - `python3 tools/loom_init.py verify --target <repo>`
- `fact_chain_support.py` 已能解析并校验 `Runtime Evidence`
- `verify` 与 `loom_check` 已把缺字段、`not_applicable` 区分和 gate 输入检查纳入默认路径

## 5. 摩擦、失效点与升级信号

- `hotcp` 证明运行时证据不能只收成一条自由文本：
  - 不同 lane 会改变启动与诊断入口
  - UI/API 验证入口和日志/诊断入口需要分别可读
- 本次实现同时保留了轻量边界：
  - 对 new-project 等无运行载体样本，五字段可以逐项 `not_applicable`
  - `Verification Entry` 仍可单独保持可读

## 6. 台账回写结果

- 本次没有新增 `EXT-*`
- 对齐并补强的稳定落点：
  - `EXT-0035`
  - `EXT-0036`
- 受影响 Loom 文件：
  - `harness/status-surface.md`
  - `skills/loom-init/references/output-contract.md`
  - `tools/fact_chain_support.py`
  - `tools/loom_init.py`
  - `tools/loom_check.py`

## 7. 关闭依据

- `#38` 要求的固定运行时证据区块、脚本解析、`not_applicable` 分项语义与 gate 校验都已进入版本控制
- Loom demo 已覆盖机读回归，`hotcp` 补足了复杂仓库中这五类证据为什么必须稳定可读的真实样本依据
- 当前仍保留在宿主适配层的部分：
  - 具体 observability 产品与 browser automation 工具链
  - 宿主平台如何把这些入口投放到 UI 或 CI
