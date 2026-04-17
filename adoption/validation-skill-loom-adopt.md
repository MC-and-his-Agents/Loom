# Skill Validation: `loom-adopt`

## 1. 样本标识

- 场景 skill：`loom-adopt`
- 验证日期：`2026-04-16`
- 对应 Loom issue：`#76`
- 子 issue：`#77`、`#78`、`#79`

## 2. 验证样本

- Demo 仓库：`examples/new-project`
- 新项目样本：`/Users/mc/dev/loom-adoption-new-project`
- 既有仓库样本：`/Users/mc/dev/mail-listener`

## 3. 显式触发验证

执行：

- `python3 tools/loom_init.py route --target examples/new-project --skill loom-adopt`

期望：

- 返回 `result: pass`
- `selected_skill` 为 `loom-adopt`
- 不绕行到其他场景 skill

## 4. 隐式路由验证

执行：

- `python3 tools/loom_init.py route --target examples/new-project --task "请初始化这个新项目并接入 Loom"`

期望：

- 返回 `result: pass`
- `selected_skill` 为 `loom-adopt`
- `matched_signals` 能解释为什么命中 adopt 场景

## 5. 下游消费验证

执行：

- `python3 tools/loom_init.py bootstrap --target examples/new-project --write --force --verify --install-pr-template`
- `python3 tools/loom_init.py verify --target examples/new-project`
- `python3 tools/loom_init.py fact-chain --target examples/new-project`

结论：

- `loom-adopt` 没有自造新 CLI，而是稳定消费 `loom_init bootstrap/verify/fact-chain`
- 初始化结果、验证入口与事实链入口仍由同一条 root bootstrap 真相承接
- `loom-adopt` 对外公开的治理读面固定复用 root 输出合同中的 `governance_surface`
- 场景 skill 只负责“何时进入 adopt 场景”和“进入后调用什么”，不新增并行状态源

## 6. 关闭依据

- `loom-adopt` 已从 skeleton 提升为正式场景入口
- 显式触发、隐式路由、下游消费三条线都已有可追溯验证
- `governance_surface` 继续唯一落在 root 初始化输出合同，不在 adopt 场景再造第二套治理字段
- 本次未扩张 root bootstrap 的真相边界
